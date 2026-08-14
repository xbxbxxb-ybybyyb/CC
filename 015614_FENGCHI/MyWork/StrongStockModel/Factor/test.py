sys.path.append('/data/group/800319/junkBigFactorPool/core/')
from FactorTest import FactorTest

ft = FactorTest()

program = dict(
    program_code='''
    
    pn_condition2(
        dt_max(dt_lwm(turn_trade_buy, 4), 3), 
        dt_cumsum(log(ds_cumsum(adj_high)))
        )
    ''',

    program_complex=False,
    program_manual=False,

    program_author='016835',
    program_class='机器挖掘',
    program_reference='无知无畏',
    program_logic='无知无畏',
)

ft.test_factor(program)

#
# import pandas as pd
# import os
# from tqdm import tqdm
#
# file_list = os.listdir('/data/group/800319/junkBigFactorPool/level2_waiting/')
#
# all_res = {}
# for each in tqdm(file_list):
#     res = pd.read_pickle('/data/group/800319/junkBigFactorPool/level2_waiting/%s'%each)
#     res = pd.Series(res)
#     res = res[res.index[:11]]
#     all_res[each] = res
#
# all_res = pd.DataFrame(all_res)
# all_res = all_res.T
# all_res.to_excel('/data/user/015664/AFuckingTrigger/因子总结.xlsx')
