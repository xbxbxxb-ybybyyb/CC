import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
import IO as IO
import datetime as dt

s = FactorData()
def run_factor(func, factor_name, factor_type, start_date, end_date, basic_file_path, result_path, append_next_tradingday=False, interval_res=True,
               emotion_data = {'Basic_zt':None, 'Label_zt':None},
               data_path_dic= {'TTransaction': '/data/group/800463/data/project1_prod/transaction_test_001_ezt/',
                                'LastTouchTTick':'/data/group/800463/data/project1_prod/last_touch_t_tick/',
                                'MarketTTick':'/data/group/800463/data/project1_prod/market_t_tick/',
                                'Market1TTick':'/data/group/800463/data/project1_prod/market_t_tick/',
                                'MarketIndTTick':'/data/group/800463/data/project1_prod/market_t_tick/',
                               'TOrder':'/data/group/800463/data/project1_prod/order_test_001/',
                               'TTickab': '/data/group/800463/data/project1_prod/tickab_test_001/'}):
        # 个股因子
        if '.pkl' in basic_file_path:
            basic_df = pd.read_pickle(basic_file_path)
            basic_df = basic_df.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
        else:
            basic_df = IO.read_data([start_date, end_date], alt=basic_file_path)
        if factor_type in ['TTickfull','TTransaction', 'TTickab', 'TOrder']:
            tradingday_list = s.tradingday(start_date, end_date)
            # factor_df_list = []
            # for tradingday, num in zip(tradingday_list, range(len(tradingday_list))):
            def calc_tmp_df(tradingday,num):
                data = pd.read_pickle('%s%s.pkl'%(data_path_dic[factor_type], tradingday))
                tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x))
                return tmp_df
            from joblib import Parallel, delayed
            factor_df_list = Parallel(n_jobs=16)(delayed(calc_tmp_df)(tradingday,num) for tradingday, num in zip(tradingday_list, range(len(tradingday_list))))
                # factor_df_list.append(pd.concat([tmp_df], axis=1))
            factor_df = pd.concat(factor_df_list, axis=0)
            factor_df = factor_df.reindex(basic_df.index)
            # 使用因子计算函数中的fillna进行异常值填充, inf的填充则在计算函数内部进行处理
            fill_dic = func(None, return_fillna_dic=True)
            result_df = factor_df.fillna(fill_dic)
        elif factor_type in ['TTransaction_TTickab', 'TTransaction_TOrder', 'TTickab_TOrder']:
            factor_type0,factor_type1=factor_type.split('_')[0],factor_type.split('_')[1]
            tradingday_list = s.tradingday(start_date, end_date)
            factor_df_list = []
            for tradingday, num in zip(tradingday_list, range(len(tradingday_list))):
                view_bar(num, len(tradingday_list), tradingday)
                data0 = pd.read_pickle('%s%s.pkl' % (data_path_dic[factor_type0], tradingday))
                data0['type'] = 0
                data1 = pd.read_pickle('%s%s.pkl' % (data_path_dic[factor_type1], tradingday))
                data1['type'] = 1
                data = pd.concat([data0,data1],axis=0,sort=False)
                tmp_df = data.groupby(level=[0, 1]).apply(lambda x: func(x))
                factor_df_list.append(pd.concat([tmp_df], axis=1))
            factor_df = pd.concat(factor_df_list, axis=0)
            factor_df = factor_df.reindex(basic_df.index)
            # 使用因子计算函数中的fillna进行异常值填充, inf的填充则在计算函数内部进行处理
            fill_dic = func(None, return_fillna_dic=True)
            result_df = factor_df.fillna(fill_dic)
        elif factor_type in ['LastTouchTTick', 'MarketTTick','Market1TTick','MarketIndTTick']:
            if factor_type in ['MarketIndTTick']:  # 读取一级行业
                start_date_ = int(s.tradingday(str(start_date), - 5)[0])
                ind_data = IO.read_data([start_date_, end_date], columns=['amt'],
                                        alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
                ind_data['Industry'] = IO.read_data([start_date_, end_date], columns=['Industry'],
                                                    alt='/data/group/800080/warehouse/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5')
                ind_data['Industry'] = ind_data['Industry'].unstack().shift(1).stack()

            tradingday_list = s.tradingday(start_date, end_date)
            factor_df_list = []
            basic_list = list(basic_df.groupby(level=0))
            basic_dic = {sample[0].strftime('%Y%m%d'):sample[1] for sample in basic_list}
            for tradingday, num in zip(tradingday_list, range(len(tradingday_list))):
                view_bar(num, len(tradingday_list), tradingday)
                if os.path.exists('%s%s.pkl' % (data_path_dic[factor_type], tradingday)) == False:
                    print(tradingday, 'tradingday not exist!')
                    continue
                else:
                    data = pd.read_pickle('%s%s.pkl' % (data_path_dic[factor_type], tradingday))

                tmp_df_list = []
                for index, inf in basic_dic[tradingday].iterrows():
                    zt_time = inf['ZT_Time']
                    zt_time = max(fun_get_time(int(zt_time), -3), 93000000)
                    filter_data = data[data['MDTime']<zt_time].copy()
                    if factor_type in ['Market1TTick']:
                        #过滤单市场
                        Ticker=index[1]
                        if '.SH' in Ticker:
                            filter_data = filter_data[filter_data['is_SH']]
                        else:
                            filter_data = filter_data[~filter_data['is_SH']]
                    if factor_type in ['MarketIndTTick']:
                        # 过滤一级行业
                        try:
                            Industry=ind_data.loc[index,'Industry']
                            filter_data = filter_data[filter_data['Industry']==Industry]
                        except Exception as e:
                            print(index,e,'!'*10)
                    if factor_type in ['MarketTTick','Market1TTick','MarketIndTTick']:
                        filter_data=filter_data.groupby(['dt','Ticker']).nth([0,-1]) #目前只使用开盘和最后一个tick

                    tmp_df_list.append(pd.Series(func(filter_data), name=index))
                tmp_df = pd.concat(tmp_df_list, axis=1).T
                factor_df_list.append(tmp_df)
            result_df = pd.concat(factor_df_list, axis=0)
            result_df = result_df.reindex(basic_df.index)
            fill_dic = func(None, return_fillna_dic=True)
            result_df = result_df.fillna(fill_dic)
        elif factor_type in ['T-1_factor', 'other']:
            factor_df = func(start_date, end_date, IO)
            start_date_ = int(s.tradingday(str(start_date), - 5)[0])
            if append_next_tradingday:
                last_date = int(s.tradingday(str(end_date), - 2)[0])
                # 获取md_data用来对齐样本，防止factor_df里缺少某些样本，因此T-1日因子必须要先等MD更新完之后才能更新
                md_data = IO.read_data([start_date_, last_date], columns=['amt'],alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
                factor_df = factor_df.reindex(md_data.index)
                factor_df = fun_append_next_tradingday(factor_df)
                result_df = pd.DataFrame(index=factor_df.index)
            else:
                result_df = pd.DataFrame(index=basic_df.index)
            for factor_col in factor_df.columns:
                result_df[factor_col] = factor_df[factor_col].unstack().shift(1).stack()
            # 使用因子计算函数中的fillna进行异常值填充, inf的填充则在计算函数内部进行处理
            fill_dic = func(None, None, None, return_fillna_dic=True)
            result_df = result_df.fillna(fill_dic)
        if interval_res:
            data_output([start_date, end_date], result_df, result_path, factor_name=factor_name)
        else:
            second_data_output([start_date, end_date], result_df, result_path, factor_name=factor_name)
        return result_df
    elif factor_type in ['T-1_Emotion', 'TEmotion']:
        #日频情绪因子
        basic_df = pd.read_hdf(emotion_data['Basic_zt'])
        label_df = pd.read_hdf(emotion_data['Label_zt'])
        for data_name, data in zip(['Basic_zt', 'Label_zt'], [basic_df, label_df]):
            date_list = list(pd.Series(data.index.get_level_values(0)).apply(lambda x:x.strftime('%Y%m%d')))
            first_date, last_date = min(date_list), max(date_list)
            end_date_ = s.tradingday(str(end_date-10000), str(end_date))[-1]
            if factor_type == 'T-1_Emotion':
                if ((last_date < str(end_date)) and (len(s.tradingday(last_date, str(end_date)))>2)) or \
                    (len(s.tradingday(first_date, str(start_date)))<10):
                    print('%s-%s data interval error!!!!factor interval:%s, data interval:%s'%(factor_name, data_name, [start_date, end_date], [int(first_date), int(last_date)]))
                    return
                else:
                    date_df = func(start_date, end_date, emotion_data['Basic_zt'], emotion_data['Label_zt'])
                    date_df = date_df.fillna(func(None, None, None, None, return_fillna_dic=True))
            elif factor_type == 'TEmotion':
                if (last_date < str(end_date_)) or (len(s.tradingday(first_date, str(start_date))) < 10):
                    print('%s-%s data interval error!!!!factor interval:%s, data interval:%s' % (factor_name, data_name, [start_date, end_date], [int(first_date), int(last_date)]))
                    return
                else:
                    date_df = func(start_date, end_date, emotion_data['Basic_zt'], emotion_data['Label_zt'])
                    date_df = date_df.fillna(func(None, None, None, None, return_fillna_dic=True))
        if not os.path.exists(result_path):
            os.makedirs(result_path)
        if interval_res:
            date_df.to_pickle(result_path + '%s_%d_%d.pkl' % (factor_name, start_date, end_date))
        else:
            second_output(result_path + '%s.pkl'%(factor_name), date_df)
        return date_df