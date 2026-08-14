# coding: utf-8
# Author：fengchi863
# Date ：2024/11/28 16:09

"""
上交所证券代码规则:
全部以6开头
600、601、603、605开头个股：上证A股
900开头个股：上证B股（不考虑）
688开头个股：科创板

深交所证券代码规则：
全部以0开头或者以3开头
000、001开头：深证A股
002开头：中小板A股
300、301开头：创业板A股
200开头：深证B股（不考虑）

北交所证券代码规则：
82开头：优先股
83或87开头：普通股票
88开头：公开发行的股票
920开头：摇号选号或直接选号方式
43开头：老三板股票
"""

def trans_any2code(stk_id: str or int):
    if type(stk_id) == int:
        stk_id = str(stk_id)

    if stk_id.find('.') > 0:
        stk_id = int(stk_id.split('.')[0])

    stk_id = str(stk_id).zfill(6)

    if stk_id.startswith('6'):
        ret = stk_id + '.SH'
    elif stk_id.startswith('3') or stk_id.startswith('0'):
        ret = stk_id + '.SZ'
    else:
        ret = stk_id + '.BJ'

    return ret

if __name__ == '__main__':
    test_code = '920099'
    print(trans_any2code(test_code))