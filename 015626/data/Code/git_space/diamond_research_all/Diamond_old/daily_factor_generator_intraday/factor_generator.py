import os
import pandas as pd
from utils.help_functions_wsc import read_pickle, save_pickle, pd_writer, replace_zero, save_pickle


class FactorGenerator:
    __data__ = None
    __ticker__=None
    def __init__(self, factor_name = 'test', lookback_bars = 5000, required_columns = None,
                 savepath = '/data/user/017024/share/overnight/alpha_intraday/'):
        self.factor_name = factor_name
        self.lookback_bars = lookback_bars
        self.required_columns = required_columns
        self.savepath = savepath

    @classmethod
    def prepare_hot_data(inst, start_date, end_date):
        start_date = str(start_date)
        end_date = str(end_date)
        data_dict = {}
        
        ticker00 = pd.read_csv(os.path.join('/data/user/017024/share/overnight/data/intraday/', end_date, end_date+'_trading_contract.csv'), index_col=0).columns[0]
                
        future_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/FUTURE_DATA_2020.pkl')
        index_data = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/SPOT_DATA_2020.pkl')
        daily_future_data = read_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight/OUTSAMPLE/future_daily_overnight.pkl')
        daily_index_data = read_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight/OUTSAMPLE/spot_daily_overnight.pkl')
        today_data = pd.read_hdf(os.path.join('/data/user/012245/warehouse/prod/market/closure/', end_date) + '.h5')
        today_data.drop(pd.to_datetime(end_date+' 11:30:00'), axis=0, inplace=True)
        # today_data = pd.read_hdf('/data/user/012245/warehouse/prod/market/closure/demo.h5')
        assert int(today_data.index[-1].strftime("%H%M")) >= 1449
        today_data = today_data.rename(columns={'amt': 'amount', 'oi': 'position'})
        
        
#        for i in future_data.keys():
#            future_data[i] = future_data[i][:'20210310']
#        for i in index_data.keys():
#            index_data[i] = index_data[i][:'20210310']
#        for i in daily_future_data.keys():
#            daily_future_data[i] = daily_future_data[i][:'20210310']
#        for i in daily_index_data.keys():
#            daily_index_data[i] = daily_index_data[i][:'20210310']
        
        
        # 指数数据拼接
        today_data_spot_ic = today_data[today_data['windcode']=='000905.SH'].drop(['windcode', 'position'], axis=1)
        today_data_spot_ic.columns = [i+'_spot' for i in today_data_spot_ic.columns]
        today_data_spot_if = today_data[today_data['windcode']=='000300.SH'].drop(['windcode', 'position'], axis=1)
        today_data_spot_if.columns = [i+'_spot_if' for i in today_data_spot_if.columns]
        
        for i in today_data_spot_ic.columns:
            if i in ['open_spot', 'high_spot', 'low_spot', 'close_spot']:
                data_new = today_data_spot_ic[i].fillna(method='ffill')
            elif i in ['volume_spot', 'amount_spot']:
                data_new = today_data_spot_ic[i].fillna(0)
            data_old = index_data[i]
            data_need = pd.concat([data_old, data_new], axis=0, sort=True)
            data_dict[i] = data_need
    
        for i in today_data_spot_if.columns:
            if i in ['open_spot_if', 'high_spot_if', 'low_spot_if', 'close_spot_if']:
                data_new = today_data_spot_if[i].fillna(method='ffill')
            elif i in ['volume_spot_if', 'amount_spot_if']:
                data_new = today_data_spot_if[i].fillna(0)
            data_old = index_data[i]
            data_need = pd.concat([data_old, data_new], axis=0, sort=True)
            data_dict[i] = data_need
        
        
        # 期货数据拼接
        future_code_need = sorted([i[2:] for i in today_data['windcode'].unique() if i.startswith('IC')])
        future_code_need_ic = ['IC'+ i for i in future_code_need]
        future_code_need_if = ['IF'+ i for i in future_code_need]
        
        future_today_ic = today_data[today_data['windcode'].isin(future_code_need_ic)]
        future_today_ic['vwap'] = future_today_ic['amount'] / (replace_zero(future_today_ic['volume']) * 200)
        future_today_ic = future_today_ic.reset_index().set_index(['index', 'windcode']).unstack()
        # future_today_ic[['open', 'high', 'low', 'close']] = future_today_ic[['open', 'high', 'low', 'close']].fillna(method='ffill')
        future_today_if = today_data[today_data['windcode'].isin(future_code_need_if)]
        future_today_if['vwap'] = future_today_if['amount'] / (replace_zero(future_today_if['volume']) * 300)
        future_today_if = future_today_if.reset_index().set_index(['index', 'windcode']).unstack()
        # future_today_if[['open', 'high', 'low', 'close']] = future_today_if[['open', 'high', 'low', 'close']].fillna(method='ffill')
        
        need_columns = list(today_data.columns)
        need_columns.remove('windcode')
        need_columns.append('vwap')
        
        for i in need_columns:
            future_today_temp = future_today_ic[i]
            future_today_temp.index.name = 'dt'
            future_today_temp.columns.name = 'contract'
            future_today_temp.columns = future_code_need
            if i in ['open', 'high', 'low', 'close']:
                future_today_temp = future_today_temp.fillna(method='ffill')
            elif i in ['volume', 'amount']:
                future_today_temp = future_today_temp.fillna(0)
            future_today_temp = pd.concat([future_data[i], future_today_temp], axis=0, sort=True)
            data_dict[i] = future_today_temp
        for i in need_columns:
            i_name = i + '_if'
            future_today_temp = future_today_if[i]
            future_today_temp.index.name = 'dt'
            future_today_temp.columns.name = 'contract'
            future_today_temp.columns = future_code_need
            if i in ['open', 'high', 'low', 'close']:
                future_today_temp = future_today_temp.fillna(method='ffill')
            elif i in ['volume', 'amount']:
                future_today_temp = future_today_temp.fillna(0)
            future_today_temp = pd.concat([future_data[i_name], future_today_temp], axis=0, sort=True)
            data_dict[i_name] = future_today_temp
            
        # recent_month_mask需要特别处理
        future_mask = future_data['recent_month_mask']
        future_mask = future_mask.reindex(data_dict['open'].index)
        future_mask.loc[today_data.index] = False
        future_mask.loc[today_data.index, ticker00] = True
        data_dict['recent_month_mask'] = future_mask
        
        
        # 日频指数数据拼接
        daily_index = pd.to_datetime(today_data_spot_ic.index[0].date()) # 获取今天的日期
        daily_index_data['daily_open_spot'].loc[daily_index] = today_data_spot_ic['open_spot'].iloc[0]
        daily_index_data['daily_high_spot'].loc[daily_index] = today_data_spot_ic['high_spot'].max()
        daily_index_data['daily_low_spot'].loc[daily_index] = today_data_spot_ic['low_spot'].min()
        daily_index_data['daily_close_spot'].loc[daily_index] = today_data_spot_ic['close_spot'].iloc[-1]
        daily_index_data['daily_volume_spot'].loc[daily_index] = today_data_spot_ic['volume_spot'].sum()
        daily_index_data['daily_amount_spot'].loc[daily_index] = today_data_spot_ic['amount_spot'].sum()

        daily_index_data['daily_open_spot_if'].loc[daily_index] = today_data_spot_if['open_spot_if'].iloc[0]
        daily_index_data['daily_high_spot_if'].loc[daily_index] = today_data_spot_if['high_spot_if'].max()
        daily_index_data['daily_low_spot_if'].loc[daily_index] = today_data_spot_if['low_spot_if'].min()
        daily_index_data['daily_close_spot_if'].loc[daily_index] = today_data_spot_if['close_spot_if'].iloc[-1]
        daily_index_data['daily_volume_spot_if'].loc[daily_index] = today_data_spot_if['volume_spot_if'].sum()
        daily_index_data['daily_amount_spot_if'].loc[daily_index] = today_data_spot_if['amount_spot_if'].sum()
        
        data_dict['daily_open_spot'] = daily_index_data['daily_open_spot']
        data_dict['daily_high_spot'] = daily_index_data['daily_high_spot']
        data_dict['daily_low_spot'] = daily_index_data['daily_low_spot']
        data_dict['daily_close_spot'] = daily_index_data['daily_close_spot']
        data_dict['daily_volume_spot'] = daily_index_data['daily_volume_spot']
        data_dict['daily_amount_spot'] = daily_index_data['daily_amount_spot']
        data_dict['daily_open_spot_if'] = daily_index_data['daily_open_spot_if']
        data_dict['daily_high_spot_if'] = daily_index_data['daily_high_spot_if']
        data_dict['daily_low_spot_if'] = daily_index_data['daily_low_spot_if']
        data_dict['daily_close_spot_if'] = daily_index_data['daily_close_spot_if']
        data_dict['daily_volume_spot_if'] = daily_index_data['daily_volume_spot_if']
        data_dict['daily_amount_spot_if'] = daily_index_data['daily_amount_spot_if']
        
        # 日频期货数据拼接
        for i in future_code_need:
            i_name1 = 'IC' + i
            i_name2 = 'IF' + i
            daily_future_data['daily_open'].loc[daily_index, i] =  today_data[today_data['windcode'] == i_name1]['open'].iloc[0]
            daily_future_data['daily_high'].loc[daily_index, i] =  today_data[today_data['windcode'] == i_name1]['high'].max()
            daily_future_data['daily_low'].loc[daily_index, i] =  today_data[today_data['windcode'] == i_name1]['low'].min()
            daily_future_data['daily_close'].loc[daily_index, i] =  today_data[today_data['windcode'] == i_name1]['close'].iloc[-1]
            daily_future_data['daily_volume'].loc[daily_index, i] =  today_data[today_data['windcode'] == i_name1]['volume'].sum()
            daily_future_data['daily_amount'].loc[daily_index, i] =  today_data[today_data['windcode'] == i_name1]['amount'].sum()
            daily_future_data['daily_open_if'].loc[daily_index, i] =  today_data[today_data['windcode'] == i_name2]['open'].iloc[0]
            daily_future_data['daily_high_if'].loc[daily_index, i] =  today_data[today_data['windcode'] == i_name2]['high'].max()
            daily_future_data['daily_low_if'].loc[daily_index, i] =  today_data[today_data['windcode'] == i_name2]['low'].min()
            daily_future_data['daily_close_if'].loc[daily_index, i] =  today_data[today_data['windcode'] == i_name2]['close'].iloc[-1]
            daily_future_data['daily_volume_if'].loc[daily_index, i] =  today_data[today_data['windcode'] == i_name2]['volume'].sum()
            daily_future_data['daily_amount_if'].loc[daily_index, i] =  today_data[today_data['windcode'] == i_name2]['amount'].sum()
        
        data_dict['daily_open'] = daily_future_data['daily_open']
        data_dict['daily_high'] = daily_future_data['daily_high']
        data_dict['daily_low'] = daily_future_data['daily_low']
        data_dict['daily_close'] = daily_future_data['daily_close']
        data_dict['daily_volume'] = daily_future_data['daily_volume']
        data_dict['daily_amount'] = daily_future_data['daily_amount']
        data_dict['daily_open_if'] = daily_future_data['daily_open_if']
        data_dict['daily_high_if'] = daily_future_data['daily_high_if']
        data_dict['daily_low_if'] = daily_future_data['daily_low_if']
        data_dict['daily_close_if'] = daily_future_data['daily_close_if']
        data_dict['daily_volume_if'] = daily_future_data['daily_volume_if']
        data_dict['daily_amount_if'] = daily_future_data['daily_amount_if']
        
        # recent_month_mask需要特别处理
        daily_future_mask= daily_future_data['daily_recent_month_mask']
        daily_future_mask = daily_future_mask.reindex(daily_future_data['daily_open'].index)
        daily_future_mask.loc[daily_future_data['daily_open'].index[-1]] = False
        daily_future_mask.loc[daily_future_data['daily_open'].index[-1], ticker00] = True
        data_dict['daily_recent_month_mask'] = daily_future_mask

        save_pickle(data_dict, os.path.join('/data/user/017024/share/overnight/data/intraday/', end_date, end_date+'_future_index.pkl'))
        for key in data_dict.keys():
             data_dict[key] = data_dict[key].loc[start_date: end_date]
        

        inst.__data__ = data_dict


    def slicer(self):
        return {col:self.__data__[col].copy() for col in self.required_columns}

    def __callback__(self, start_date, end_date):
        data = self.slicer()
        savepath = self.savepath
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        factor = self.on_bar(data)
        start_date = str(start_date)
        end_date = str(end_date)
        factor = factor.loc[start_date:end_date]
        pd_writer(factor, savepath)