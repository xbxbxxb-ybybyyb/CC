import sys
import os
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import datetime as dt
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()
import warnings
warnings.filterwarnings('ignore')
from ProdWork.CommonTools import excel_saver, inttime2str
from ProdWork.log_analyse.new_prod.jupiter.LogParse_Tool import LogParse_Tool

if __name__ == "__main__":
    tradeDate = dt.datetime.now().strftime('%Y-%m-%d')
    # tradeDate = '2025-08-01'    # 当天即可
    nowdate = tradeDate[:4] + tradeDate[5:7] + tradeDate[8:]
    begindate, enddate = nowdate, nowdate

    for date in s.tradingday(begindate, enddate):
        tradeDate = '%s-%s-%s'%(date[:4],date[4:6],date[6:])
        tradeDatestr = tradeDate[:4] + tradeDate[5:7] + tradeDate[-2:]
        lastdate = s.tradingday(tradeDatestr, -2)[0]
        lastdate_h = pd.Timestamp(s.tradingday(tradeDatestr, -2)[0]).strftime('%Y-%m-%d')
        environment_lst =['prod', 'UAT']
        # environment_lst =['UAT']
        # environment_lst =['night']
        for environment in environment_lst:
            print(tradeDate, environment, '\n')
            # ------------ 按环境加载日志的目录 ---------------
            import gzip
            if environment == 'UAT':
                file_list = list(sorted(list(filter(lambda x: f'{tradeDate}' in x and 'JupiterStrategy' in x and 'BJ' not in x, os.listdir('/data/group/800463/StrategyLog/xsim/')))))
                file_name = '/data/group/800463/StrategyLog/xsim/' + file_list[0]
            if 'night' in environment:
                file_list = list(sorted(list(filter(lambda x: f'{tradeDate}' in x and 'JupiterStrategy' in x and 'BJ' not in x, os.listdir('/data/group/800463/StrategyLog/xsim/')))))
                file_name = '/data/group/800463/StrategyLog/xsim/' + file_list[-1]
            if environment == 'test':
                # file_name = '/data/group/800463/xiely/save-file/forFc/log/log_local_20230629.txt'
                file_name = '/data/user/013551/forXT/log/local_log/eventdriven_log/20231108-xdev38-metis.log'
            print(file_name)

            # FIXME：分别是IT传进来和谢璐遥传进来的
            o45file_name = '/data/group/800463/StrategyLog/prd/SZEX.JupiterStrategy-' + tradeDate + '.log.gz'
            o45file_SHname = '/data/group/800463/StrategyLog/prd/SHEX.JupiterStrategy-' + tradeDate + '.log.gz'

            if environment == 'prod' and os.path.exists(o45file_name):
                print('提取o45日志')
                o45_g_file = gzip.GzipFile(o45file_name)
                o45_lines = o45_g_file.readlines()
                print('SZ',len(o45_lines))
            else:
                o45_lines = []

            if environment == 'prod' and os.path.exists(o45file_SHname):
                print('提取o45SH日志')
                o45_g_SHfile = gzip.GzipFile(o45file_SHname)
                o45_SHlines = o45_g_SHfile.readlines()
                print('SH', len(o45_SHlines))
            else:
                o45_SHlines = []

            if environment not in  ['prod']:
                g_file = gzip.GzipFile(file_name)
                # g_file = open(file_name)
                lines = g_file.readlines()
            else:
                lines = []
            lines = lines + o45_lines + o45_SHlines
            lines = list(filter(lambda x: str(x).startswith(f"b'{tradeDate[:4]}-"), lines))

            logparse = LogParse_Tool(environment, tradeDatestr, lines)
            print('日志数据读取完毕\n', len(logparse.lines))

            log_split_file_path = '/data/group/800463/日内强势股/jupiter_log_parse/日志拆分/%s_%s环境/' % (tradeDatestr, environment)
            # TODO: 这里要先删除这个文件夹中的所有内容，防止在上次的结果上追加
            if not os.path.exists(log_split_file_path):
                os.makedirs(log_split_file_path)
            for code, log in logparse.log_dic.items():
                if code in logparse.algo_code_dict.keys():
                    code_code = logparse.algo_code_dict[code]
                    with open(log_split_file_path + '%s-%s-%s环境.txt' % (tradeDatestr, code_code, environment), 'a+') as file_handle:
                        for line in log:
                            file_handle.write(str(line))

            # 解析日志
            inf_df_, factor_df, trade_dic, now_trade_dic, all_code_model_data, daily_zt_df, order_info_df, unfilled_info_df, \
            new_trade_dic = logparse.get_inf_from_log()

            except_df = logparse.get_except_df()
            factor_df.sort_index().to_excel('/data/group/800463/日内强势股/jupiter_log_parse/因子数据/因子数据_%s_%s.xlsx' % (tradeDate, environment))
            print('create file %s' % '/data/group/800463/日内强势股/jupiter_log_parse/因子数据/因子数据_%s_%s.xlsx' % (tradeDate, environment))

            if len(except_df) > 0:
                except_df.to_excel('/data/group/800463/日内强势股/jupiter_log_parse/异常报错/异常报错_%s_%s.xlsx' % (tradeDate, environment))
                print('create file %s' % '/data/group/800463/日内强势股/jupiter_log_parse/异常报错/异常报错_%s_%s.xlsx' % (tradeDate, environment))
            md_data_path = '/data/group/800463/日内强势股/jupiter_log_parse/行情数据/%s_%s/' % (tradeDate, environment)

            model_factor_data_path = '/data/group/800463/日内强势股/jupiter_log_parse/模型数据/%s_%s/' % (tradeDate, environment)
            if not os.path.exists(md_data_path):
                os.makedirs(md_data_path)
            if not os.path.exists(model_factor_data_path):
                os.makedirs(model_factor_data_path)

            if 'ZT_Time' in inf_df.columns.tolist():
                inf_df = inf_df.sort_values('ZT_Time')
                inf_df['ZT_Time_str'] = inf_df['ZT_Time'].apply(inttime2str)
                daily_zt_df['ZT_Time'] = inf_df['ZT_Time'].loc[daily_zt_df.index]
            inf_df['machine_code'] = pd.Series(logparse.machine_code_dict).loc[inf_df.index].values

            tupo_excel_dic = {'每日突破': daily_zt_df,
                              '每日订单': order_info_df,
                              '每日拒绝': unfilled_info_df}
            excel_saver(tupo_excel_dic, '/data/group/800463/日内强势股/jupiter_log_parse/每日突破/每日突破_%s_%s.xlsx' % (tradeDatestr, environment))

            inf_df_dic = {'因子耗时': inf_df,
                          '机器统计': pd.Series(pd.Series(logparse.machine_counter_dict))}

            excel_saver(inf_df_dic, '/data/group/800463/日内强势股/jupiter_log_parse/因子耗时/因子耗时_%s_%s.xlsx' % (tradeDate, environment))

            if environment == 'prod':
                from dataApi.sendInfo import send_message
                send_message(f'{tradeDate} 实盘jupiter日志已解析')