import os
import warnings
warnings.filterwarnings('ignore')

from utils.date_helper import *


if __name__ == '__main__':
    start_date, end_date, _ = check_update_date()
    report_flag_date = end_date
    
    
    def minute_flag_check(date):
        path1 = '/data/user/017024/data/flag/' + str(date) + '/' + str(date) + '_overnight_factors_cfg_ic.success'
        path2 = '/data/user/017024/data/flag/' + str(date) + '/' + str(date) + '_overnight_factors_cfg_if.success'
        path3 = '/data/user/017024/data/flag/' + str(date) + '/' + str(date) + '_overnight_factors_future_index.success'
        return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3)
    
    flag_root = '/data/user/017024/data/flag/' + str(end_date) + '/'
    if not os.path.exists(flag_root):
        os.makedirs(flag_root)
    flag_path_start = flag_root + str(end_date) + '_overnight_factor_link.start'
    with open(flag_path_start,'w') as file:
        pass 
    
    print('------wait minute flag')
    while True:
        if minute_flag_check(end_date):
            break
        time.sleep(60)
    print('flag check finished!')
    
    
    prod_76_path = '/data/user/017024/share/overnight/alpha/prod_76'
    prod_50_path = '/data/user/017024/share/overnight/alpha/prod_50'
    prod_27_path = '/data/user/017024/share/overnight/alpha/prod_27'
    prod_26_path = '/data/user/017024/share/overnight/alpha/prod_26'
    
#    factors_50 = sorted([i for i in os.listdir(prod_50_path) if i.endswith('.h5')])
#    factors_list_50 = [os.path.join(prod_50_path, i) for i in factors_50]
#    factors_list_50_76 = [os.path.join(prod_76_path, i) for i in factors_50]    
#    # map(lambda x, y: os.link(x, y), factors_list_50_76, factors_list_50)
#    for i, i_factor in enumerate(factors_list_50):
#        os.link(factors_list_50_76[i], i_factor)
    
#    factors_27 = sorted([i for i in os.listdir(prod_27_path) if i.endswith('.h5')])
#    factors_list_27 = [os.path.join(prod_27_path, i) for i in factors_27]
#    factors_list_27_76 = [os.path.join(prod_76_path, i) for i in factors_27]
#    for i, i_factor in enumerate(factors_list_27):
#        os.link(factors_list_27_76[i], i_factor)
#    # map(lambda x, y: os.link(x, y), factors_list_27_76, factors_list_27)
    
    factors_26 = sorted([i for i in os.listdir(prod_26_path) if i.endswith('.h5')])
    factors_list_26 = [os.path.join(prod_26_path, i) for i in factors_26]
    factors_list_26_76 = [os.path.join(prod_76_path, i) for i in factors_26]
    for i, i_factor in enumerate(factors_list_26):
        os.link(factors_list_26_76[i], i_factor)
    
    
    flag_path_success = flag_root + str(end_date) + '_overnight_factor_link.success'
    with open(flag_path_success,'w') as file:
        pass
    
    
    
    
    
    
    
    