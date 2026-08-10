from xquant.factordata import FactorData
from xquant.futuredata import FutureData

import pandas as pd
from get_data import get_trading_days, get_ZL_contract

class DataCenter(object):
    '''
    目前框架对于指数成分股历史分钟数据只支持一天的获取
    '''

    def __init__(self, variety, date):
        self.history_data = None
        self.today_data = None
        self.days_past = None
        self.data_fields = None
        self.data_type = None

        self.variety = variety
        self.date = date

        self.__variety_index_dict = {'IH':'SZ50','IF':'HS300','IC':'ZZ500'}

        self.__tick_root_path = '/data/user/015615/IndexFuture/data_center/tick_data/cleaned_data'
        self.__minute_root_path = '/data/user/015615/IndexFuture/data_center/minute_data/cleaned_data'
        self.__10s_root_path = '/data/user/015615/IndexFuture/data_center/10s_data/cleaned_data'
        self.__minute_index_root_path = '/data/user/015615/IndexFuture/data_center/index_stock_data/minute_data/'

    def load_history_data(self):

        assert isinstance(self.days_past,int) and self.days_past >= 0, 'Invalid input of days_past!!!'
        assert self.data_type in ['Minute', 'Tick', '10s', 'MinuteIndex'], 'Invalid input of data type!!!'

        date_list = sorted(self._get_trading_days('19900101',self.date)[-self.days_past-1:-1])

        dominant_instrument_id = None
        if self.date == '20180102':
            dominant_instrument_id = self.variety + '1801.CF'
        else:
            # dominant_instrument_id = FutureData().get_change_date(self.variety, self.date, 'ZL00')[0]
            dominant_instrument_id = get_ZL_contract(self.variety, self.date)

        if len(date_list) == 0: return

        if self.data_type == 'Tick':
            df_history_data = pd.concat([pd.read_pickle(self.__get_tick_path(d)) for d in date_list])
        elif self.data_type == 'Minute':
            # df_history_data = pd.concat([pd.read_pickle(self.__get_minute_path(d)) for d in date_list])
            df_history_data = pd.concat([self.merge_multi_minute_data_by_date(d,dominant_instrument_id) for d in date_list])
        elif self.data_type == '10s':
            df_history_data = pd.concat([pd.read_pickle(self.__get_10s_path(d)) for d in date_list])
        elif self.data_type == 'MinuteIndex':
            df_history_data = pd.concat([self.get_history_index_stock_df(d) for d in date_list])


        df_history_data = df_history_data[self.data_fields]

        setattr(self,'history_data',df_history_data)

    def __get_index_info(self, variety, date):

        df_index = pd.read_pickle('{}/{}ZL/minute_{}.pickle'.format(self.__minute_root_path, variety, date))

        return df_index.reset_index().set_index(['Date','Time'])


    def load_today_data(self):

        assert self.data_type in ['Minute', 'Tick', '10s', 'MinuteIndex'], 'Invalid input of data type!!!'

        dominant_instrument_id = None
        if self.date == '20180102':
            dominant_instrument_id = self.variety + '1801.CF'
        else:
            # dominant_instrument_id = FutureData().get_change_date(self.variety, self.date, 'ZL00')[0]
            dominant_instrument_id = get_ZL_contract(self.variety, self.date)

        if self.data_type == 'Tick':
            df_today_data = pd.read_pickle(self.__get_tick_path(self.date))[self.data_fields + ['Time']]
        elif self.data_type == 'Minute':
            # df_today_data = pd.read_pickle(self.__get_minute_path(self.date))[self.data_fields + ['Time']]
            df_today_data = self.merge_multi_minute_data_by_date(self.date, dominant_instrument_id).reset_index()[self.data_fields + ['Time']]
        elif self.data_type == '10s':
            df_today_data = pd.read_pickle(self.__get_10s_path(self.date))[self.data_fields + ['Time']]
        elif self.data_type == 'MinuteIndex':
            df_today_data = self.get_today_index_stock_df(self.date)[self.data_fields + ['Time']]


        setattr(self,'today_data',df_today_data)

    def merge_multi_minute_data_by_date(self, date, current_id):

        is_continue_field = False

        for i in self.data_fields:
            if 'Cont_' in i:
                is_continue_field = True
                break

        df_dominant = pd.read_pickle(self.__get_minute_path(date)).set_index('Time')

        if is_continue_field:
            df_current = pd.read_pickle('{}/{}/{}/{}_minute_{}.pickle'.format(self.__minute_root_path,self.variety,current_id,current_id,date)).set_index('Time')

            old_columns = ['OpenPx', 'ClosePx', 'HighPx', 'LowPx', 'Twap', 'AskVol', 'BidVol', 'TodayOpen', 'TodayHigh',
                           'TodayLow',
                           'AskP0', 'AskP1', 'AskP2', 'AskP3', 'AskP4', 'BidP0', 'BidP1', 'BidP2', 'BidP3', 'BidP4',
                           'OpenInterest', 'PreOpenInterest',
                           'PreClosePx', 'PreSettlePrice', 'TotalVolumeTrade', 'TotalValueTrade']

            old_columns_extra = ['Volume','Interest','Turnover']
            new_columns = ['Cont_{}'.format(i) for i in old_columns]
            new_columns_extra = ['Cont_{}'.format(i) for i in old_columns_extra]

            df_current_1 = df_current[old_columns]
            df_current_2 = df_current[old_columns_extra]

            df_current_1.columns = new_columns
            df_current_2.columns = new_columns_extra

            df_result = pd.concat([df_dominant, df_current_1],axis=1).fillna(method='ffill')
            df_result = pd.concat([df_result, df_current_2],axis=1).fillna(0)
        else:
            df_result = df_dominant

        return df_result


    def __get_tick_path(self, date):
        if date == '20180102':
            instrument_id = self.variety + '1801.CF'
        else:
            # instrument_id = FutureData().get_change_date(self.variety,date,'ZL00')[0]
            instrument_id = get_ZL_contract(self.variety, date)
        return '{}/{}/{}/{}_tick_{}.pickle'.format(self.__tick_root_path,self.variety, instrument_id, instrument_id, date)

    def __get_minute_path(self, date):
        if date == '20180102':
            instrument_id = self.variety + '1801.CF'
        else:
            # instrument_id = FutureData().get_change_date(self.variety, date, 'ZL00')[0]
            instrument_id = get_ZL_contract(self.variety, date)
        return '{}/{}/{}/{}_minute_{}.pickle'.format(self.__minute_root_path,self.variety, instrument_id, instrument_id, date)

    def __get_10s_path(self, date):
        if date == '20180102':
            instrument_id = self.variety + '1801.CF'
        else:
            # instrument_id = FutureData().get_change_date(self.variety, date, 'ZL00')[0]
            instrument_id = get_ZL_contract(self.variety, date)
        return '{}/{}/{}/{}_10s_{}.pickle'.format(self.__10s_root_path,self.variety, instrument_id, instrument_id, date)

    def today_data_generator(self):

        if self.data_type in ['MinuteIndex']:
            # df_today = self.today_data.reset_index().set_index(['Time','Symbol']).unstack()
            df_today = self.today_data
        else:
            df_today = self.today_data

        for i in range(len(df_today)):
            yield df_today.iloc[i]

    def _get_trading_days(self, start_date, end_date):
        # fa = FactorData()
        # return fa.tradingday(start_date,end_date)
        return get_trading_days(start_date, end_date)

    def get_history_field(self,field):
        assert field in self.history_data.columns, 'No such filed in history data!'

        if self.data_type in ['MinuteIndex']:
            # return self.history_data.reset_index().set_index(['Date','Time','Symbol'])[field].unstack()
            return self.history_data[field]
        else:
            return self.history_data[field].tolist()

    def get_factor_time(self):
        # if self.data_type in ['MinuteIndex']:
        #     # return self.today_data.reset_index().set_index(['Time','Symbol']).unstack().index.tolist()
        #     return self.today_data['Time'].tolist()
        # else:
        return self.today_data['Time'].tolist()

    def get_history_index_stock_df(self, date):
        symbol_list = FactorData().hset('INDEX',date,self.__variety_index_dict.get(self.variety))['stock'].tolist()
        s_adjfactor = self.get_index_adjfactor(date,True)

        data_list = []
        for symbol in symbol_list:
            df_symbol = pd.read_pickle('{}/{}/minute_{}.pickle'.format(self.__minute_index_root_path,symbol,date))
            df_symbol['Adjfactor'] = s_adjfactor.loc[symbol]
            data_list.append(df_symbol)

        df_stock = pd.concat(data_list).reset_index().set_index(['Date','Time','Symbol']).unstack()
        df_stock[['Index_ClosePx','Index_Volume','Index_Turnover']] = self.__get_index_info(self.variety,date)[['Index_ClosePx','Index_Volume','Index_Turnover']]

        return df_stock

    def get_today_index_stock_df(self, date):
        last_date = sorted(self._get_trading_days('19900101',date))[-2]
        symbol_list = FactorData().hset('INDEX',last_date,self.__variety_index_dict.get(self.variety))['stock'].tolist()
        s_adjfactor = self.get_index_adjfactor(date,False)

        data_list = []
        for symbol in symbol_list:
            df_symbol = pd.read_pickle('{}/{}/minute_{}.pickle'.format(self.__minute_index_root_path, symbol, date))
            df_symbol['Adjfactor'] = s_adjfactor.loc[symbol]
            data_list.append(df_symbol)

        df_stock = pd.concat(data_list).reset_index().set_index(['Date','Time','Symbol']).unstack()

        df_stock[['Index_ClosePx','Index_Volume','Index_Turnover']] = self.__get_index_info(self.variety,date)[['Index_ClosePx','Index_Volume','Index_Turnover']]

        return df_stock.reset_index()

    def get_index_weight(self, date=None):
        if date is None:
            date = self.date
        last_date = sorted(self._get_trading_days('19900101', date))[-2]

        return FactorData().hset('INDEX',last_date,self.__variety_index_dict.get(self.variety)).set_index('stock')['weight']

    def get_index_adjfactor(self, date, is_today):

        if is_today:
            weight_date = date
        else:
            weight_date = sorted(self._get_trading_days('19900101', date))[-2]

        stock = list(FactorData().hset('INDEX',weight_date,self.__variety_index_dict.get(self.variety)).set_index('stock')['weight'].index)
        df_adj = FactorData().get_factor_value(library_name='Basic_factor',stock=stock,mddate=[date],factor_names=['adjfactor'])

        return df_adj.reset_index().set_index('stock')['adjfactor']



