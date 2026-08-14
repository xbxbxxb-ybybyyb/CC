# coding: utf-8
# Author：fengchi863
# Date ：2024/10/8 17:36

import os

root_path = '/data/user/015614/Lucien/MixedWork/GreyStockGenerator/'

today_date = '20241011'

os.system(f'python3 {root_path}Abnormal_notice_T_day.py {today_date}')
os.system(f'python3 {root_path}After_dt_black_list.py {today_date}')
os.system(f'python3 {root_path}defer_reply_api_test.py {today_date}')
os.system(f'python3 {root_path}Defer_Reply_list.py {today_date}')
os.system(f'python3 {root_path}pre_dt_list.py {today_date}')
os.system(f'python3 {root_path}Pre_ST_list.py {today_date}')
os.system(f'python3 {root_path}share_comp_restrict_list.py {today_date}')
os.system(f'python3 {root_path}share_offer_list.py {today_date}')
os.system(f'python3 {root_path}ST_rid_of_hat.py {today_date}')
os.system(f'python3 {root_path}Super_abnormal.py {today_date}')
os.system(f'python3 {root_path}ycbd_5.py {today_date}')

os.system(f'python3 {root_path}Grey_list.py {today_date}')
