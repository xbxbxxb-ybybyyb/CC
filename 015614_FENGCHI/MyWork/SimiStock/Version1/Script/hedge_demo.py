# coding: utf-8
# Author：fengchi863
# Date ：2022/4/11 13:13

hedge_result = [
    dict({
        'stk_id': 1,
        'date': 20200630,
        'discount': 0.91,
        'hedge_list': [dict({'calc_date': 'T-2',
                             'start_date': 'T',
                             'end_date': 'T+5',
                             'hedge_list': [1, 2, 4],
                             'hedge_value': [0.6, 0.59, 0.55]}),    # hedge_weight这一步用不到，可以去掉吧
                       dict(),  # 下一个7日周期
                       dict()],  # ...
        'param': {'history_future_len': (120, 7)},
    }),
    dict()  # 另一只股票
    # ...
]

"""
三个周期
"""