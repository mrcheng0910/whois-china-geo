# encoding:utf-8

import math
vote_results = {
    'a': 3,
    'b': 3,
    'c':2,
    'd':2
}

option_num = len(vote_results)
total_poll = sum(vote_results.values())

maximum_thresholds = []  # 记录每级别的最大阈值


def cal_maximum_thresholds(option_num,total_poll):
    """
    计算每级的最大阈值
    :param option_num:
    :param total_poll:
    """
    level_num = option_num - 2
    if level_num >= 0:
        for i in range(level_num + 1):
            level_poll = float(total_poll - i)
            # exact
            # division
            max_threshold = math.ceil(level_poll/(option_num-i))
            if level_poll % (option_num-i) == 0:
                exact_division = True
            else:
                exact_division = False
            maximum_thresholds.insert(
                0,
                {
                "value": max_threshold,
                "exact_division":exact_division
                }
            )
    else:
        print "异常"

    print maximum_thresholds
    return maximum_thresholds


def get_max():

    maximum_thresholds = cal_maximum_thresholds(option_num, total_poll)
    max_th = vote_results['a']
    for i, j in enumerate(maximum_thresholds):
        if max_th > j['value']:
            print max_th
            break
        elif max_th == j['value'] and not j['exact_division']:
            print max_th
            break
        elif max_th == j['value'] and j['exact_division']:
            print max_th
            break
        else:
            pass


get_max()


