from overnight.factor_generator import executor, executor_1
from xquant.investment.strategyfile import upload_strategy_file
from xquant.xqutils.helper import link
from overnight.final_prepare_history import prepare_history
lm = link.LinkMessage()

    
            
if __name__ == '__main__':
#    excel_transmission_tyyth('20240410')
#    upload_strategy_file('DiamondStrategy', '20240415', 1, '/data/user/017024/cache/Diamond_20240415_afternoon_test.xlsx', is_delete = False, is_ready=1)
#    upload_strategy_file('DiamondStrategy', '20240403', 1, '/data/group/800466/trade/overnight/plan/20240403_1449/Diamond_20240403_morning.xlsx', is_delete = False, is_ready=1)
#    retrieve_misc_minute_helper()
#    executor(max_workers=1)
    
    #prepare_history('20241203')
    executor('20241204')