# @Time : 2020/12/29 15:12
# @Author : Zhichen Lu
# @File : online_conf.py

# 实盘路径
realtime_path = '/data/group/800002/realtime/alpha/'
# 本地保存每天配置文件的路径
local_config_path = '/data/group/800319/strategy_local_path3/'
# 当日收盘持仓信息(持仓量、第一次买入信息、可交易量)
holding_info_path = local_config_path + 'holding_info/'
# 当日收盘持仓股的买入时间
buy_time_info_path = local_config_path + 'buy_time_info/'
# 超参数(均值、标准差)，日期为T-1日，参数用于T日
hyper_param_path = local_config_path + 'factor_hyper_param/'
# T-1日计算出用于T日的股票池，名字为T-1日
code_list_path = local_config_path + 'code_list/'
# 模型配置文件，文件名为模型更新的日期
model_config_path = local_config_path + 'model_conf/'
model_path = local_config_path + 'model/'
# 模型文件保存路径
model_path = local_config_path + 'model/'
# 每天策略初始化参数路径
init_conf_path = local_config_path + 'daily_init_config/'
# 每天输出路径
daily_out_path = local_config_path + 'daily_output/'
# 每天输出路径
daily_out_path_offline = local_config_path + 'daily_output_offline/'
# 算法交易比例路径,文件名为文件计算日期
alog_trading_distr_path = local_config_path + 'algo_trading_distr/'
#
vol_info_path = local_config_path + 'vol_info/'
restrict_list_path = local_config_path + 'restrict_list/'
# 前一日
# 模型对应的因子列表


timetable = {'1000': ['10:10:00', '10:20:00', '10:30:00'],
             '1030': ['10:10:00', '10:20:00', '10:30:00'],
             '1100': ['10:10:00', '10:20:00', '10:30:00'],
             '1300': ['10:10:00', '10:20:00', '10:30:00'],
             '1330': ['10:10:00', '10:20:00', '10:30:00'],
             '1400': ['10:10:00', '10:20:00', '10:30:00'],
             '1430': ['10:10:00', '10:20:00', '10:30:00']}
