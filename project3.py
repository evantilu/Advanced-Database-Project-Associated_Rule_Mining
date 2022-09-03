import pandas as pd
import itertools
import argparse


#Apriori 
def join(L):
    """
    Follows the implementation in paper's section 2.1.1
    input: list of item lists of length k
    output: list of item lists of length k+1, i.e., candidate item lists of length k+1, or C_{k+1} in paper's notation
    """

    L_next = []

    # special case of 1-itemset
    if len(L[0]) == 1:
        for i in range(len(L)):
            for j in range(i+1, len(L)):
                # avoid redundancy, e.g., L[i] = ('bor_1', 'val_2', 'yrs_1')  L[j] = ('bor_1', 'val_2', 'yrs_2')
                # generating (..., yrs_1, yrs_2) is nonsense since yrs_1 and yrs_2 are the same category 
                if L[i][-1][:3] == L[j][-1][:3]:
                    # print('skip...', L[i][-1][:3])
                    continue
                # add to L_2-itemset
                tmp = list(L[i])
                tmp.extend(L[j])
                L_next.append(tuple(tmp))
        return L_next

    for i in range(len(L)):
        for j in range(i+1, len(L)):
            if L[i][:-1] == L[j][:-1] and L[i][-1] < L[j][-1]:
                # print(L[i][:-1])
                # print(L[j][:-1])
                # print()
                # print(L[i][-1])
                # print(L[j][-1])
                # print()
                # avoid redundancy, e.g., L[i] = ('bor_1', 'val_2', 'yrs_1')  L[j] = ('bor_1', 'val_2', 'yrs_2')
                # generating (..., yrs_1, yrs_2) is nonsense since yrs_1 and yrs_2 are the same category 
                if L[i][-1][:3] == L[j][-1][:3]:
                    # print('skip...', L[i][-1][:3])
                    continue
                # add to L_k+1
                tmp = list(L[i])
                tmp.append(L[j][-1])
                L_next.append(tmp)
    return L_next


def prune(C, L_pre):
    """
    Follows the implementation in paper's section 2.1.1
    input: 
        C: a list of candidate item lists of length k
        L_pre: k-itemset
    output: pruned list of item lists, i.e., L_k+1
    """

    for itemsets in C:
        # check every (k-1)-subset of itemsets is in L_k-1
        # print('itemset: ', itemsets)
        for subset in itertools.combinations(itemsets, len(itemsets)-1):
            # print('subset: ', subset)
            if subset not in L_pre:
                # remove itemset from C
                # print('attempt to remove ', itemsets)
                C.remove(itemsets)
                break

    return C


def apriori_gen(L):
    """
    input: current list of k-itemsets
    output: next, i.e., k+1-itemsets
    """

    Candidates = join(L)

    # let's make sure the items in each itemset is in sorted order
    res = []
    tmp = prune(Candidates, L)
    for x in tmp:
        res.append(tuple(sorted(x)))

    return res


def gen_assoc_rules(L, min_sup, min_conf):
    """Generate Association Rules"""

    rules = []

    for k, k_itemset in L.items():
        if k == 1:
            # trivial case
            continue
        
        # compute confidence for every permutation in every itemset tuple
        #print('k = ', k)
        for item_tup, sup in k_itemset.items():
            for item in item_tup:
                #print(item, item_tup)
                # rule = item -> every other items in item_tup
                # conf = sup(item_tup) / sup(item)
                right_items = set(item_tup) - {item}    # doesn't matter if right item is sorted bc the computation doesn't use it
                item_sup = L[1][tuple([item])]
                item_tup_sup = sup
                conf = item_tup_sup / item_sup

                # print(item, ' ------> ', right_items, 'conf: ', conf, 'sup: ', sup, '\n')
                if conf >= min_conf:
                    # item => right_items, conf, support
                    rules.append(([item], list(right_items), conf, sup))

    rules = sorted(rules, key=lambda x: x[2], reverse=True)

    return rules


def main():

    """main loop"""
    
    # receive command line arguments
    parser = argparse.ArgumentParser("Usage of Our Relation Extraction Program:")
    parser.add_argument("file", help="The dataset to be run on", type=str)
    parser.add_argument("min_sup", help="Minimum support ratio (floating point number ranging 0~1)", type=float)
    parser.add_argument("min_conf", help="Minimum confidence (floating point number ranging 0~1)", type=float)
    args = parser.parse_args()    

    file = args.file
    min_sup = args.min_sup
    min_conf = args.min_conf

    print('Input params:')
    print('----------------------------------------------------------\n\n')
    print('Dataset: ', file)
    print('Min sup: ', min_sup)
    print('Min conf: ', min_conf)
    print('----------------------------------------------------------\n\n')

    # read in dataset
    # the dataset should already be in bucketized format
    df = pd.read_csv(file)

    # the transaction table
    # the transaction table should be in format of list of sets for Apriori algo.
    trans = []
    for index, row in df.iterrows():
        trans.append(set(sorted([row['BORO'], row['FULLVAL'], row['STORIES'], row['YEAR'], row['LOT'], 
                                row['BLDGCL'], row['AVTOT2'], row['Community_Board'], row['Council_District'],
                                row['Lot_Area'],row['Building_Area'],row['Census_Tract'],row['AVLAND2'],
                                row['EXLAND2'],row['EXTOT2'],row['EXCD2']])))

    min_sup_cnt = min_sup * len(trans)

    ####################################
    # L = {
    #   1: {'item_1': #sup,
    #       'item_2': #sup,
    #        ...      
    #       },
    #   2: {('item_1', 'item_2'): #sup,
    #       ...
    #       },
    #   3: {('item_1', 'item_4', 'item_6): #sup,
    #        ...
    #       },
    #   ...
    # }
    ####################################
    L = dict() 
    items = [_ for _ in df.BORO.unique()]
    items.extend([_ for _ in df.FULLVAL.unique()])
    items.extend([_ for _ in df.STORIES.unique()])
    items.extend([_ for _ in df.YEAR.unique()])
    items.extend([_ for _ in df.LOT.unique()])
    items.extend([_ for _ in df.BLDGCL.unique()])
    items.extend([_ for _ in df.AVTOT2.unique()])
    items.extend([_ for _ in df.Community_Board.unique()])
    items.extend([_ for _ in df.Council_District.unique()])
    items.extend([_ for _ in df.Lot_Area.unique()])
    items.extend([_ for _ in df.Building_Area.unique()])
    items.extend([_ for _ in df.Census_Tract.unique()])
    items.extend([_ for _ in df.AVLAND2.unique()])
    items.extend([_ for _ in df.EXLAND2.unique()])
    items.extend([_ for _ in df.EXTOT2.unique()])

    '''initialization: init L1 (1-itemsets and counts)'''
    #print('Initializing L1...\n')
    L[1] = dict()
    for item in items:
        cnt = 0
        for row in trans:
            if item in row:
                cnt += 1
        L[1][tuple([item])] = cnt
    #print('Initialization...Done\n')

    k = 2
    # while L_(k-1) is not empty, execute the loop
    while len(L[k-1].keys()) > 0:

        Ck = apriori_gen(list(L[k-1].keys()))
        #print('--------------------')
        #print('k = ', k)
        # print('Ck = \n', Ck)

        # one pass counting for Ck
        # construct hash table (dict)
        cnt_tb = dict()
        for c in Ck:    # each c is a tuple of items
            cnt_tb[c] = 0

        # count
        for tran in trans:
            for tup in itertools.combinations(tran, k): 
                tup = tuple(sorted(tup))
                if tup in set(cnt_tb.keys()):
                    cnt_tb[tup] += 1

        # eliminate tuples < min_sup, i.e., only add those >= min_sup
        L[k] = dict()
        for tup, cnt in cnt_tb.items():
            # print(tup)
            # print(cnt)
            # print()
            if cnt >= min_sup_cnt:
                L[k][tup] = cnt

        k += 1

    
    list_of_rules = gen_assoc_rules(L, min_sup, min_conf)

    '''output results'''
    with open('output.txt', 'w') as f:
        title1 = "==Frequent itemsets (min_sup=" + str(format(min_sup*100, ".1f")) + "%)"
        f.write(title1)
        f.write('\n')
        frequent_itemset = {}

        #Check frequent itemset for k=1
        d = L[1]
        for key, value in d.items():
            if value > min_sup_cnt:
                frequent_itemset[key] = str(format((value/len(trans))*100,".1f")) + "%"

        for key2 in L:
            if key2 == 1:
                continue
            else:
                for k, v in L[key2].items():
                    frequent_itemset[k] = str(format((v/len(trans))*100,".1f")) + "%"

        frequent_itemset = sorted(frequent_itemset.items(), key=lambda item: float(item[1].strip('%')), reverse=True)
        #print(frequent_itemset)

        for item_in_set, sup_of_item in frequent_itemset:
            tmp = "["
            for i in item_in_set:
                tmp += str(i)
                tmp += ", "
            tmp += "], "
            tmp += str(sup_of_item)
            f.write(tmp)
            f.write('\n')

        title2 = "==High-confidence association rules (min_conf=" + str(format(min_conf*100, ".1f")) + "%)"
        f.write(title2)
        f.write('\n')
        for i in list_of_rules:
            temp_rule = str(i[0])
            temp_rule += " => "
            for item in range(1,len(i)-2):
                temp_rule += str(i[item])

            temp_conf = str(format(i[len(i)-2]*100, ".1f")) + "%,"
            temp_supp = str(format(i[len(i)-1]/len(trans) * 100, ".1f")) + "%"  # bug fixed: should use len(trans) here
            temp_rule += " (Conf: " + temp_conf + " Supp: " + temp_supp + ")"

            f.write(temp_rule)
            f.write('\n')
    
    #list of tuples [([item],sup)]
    #frequent_itemset.append(([item],sup))

if __name__ == "__main__":
    
    main()