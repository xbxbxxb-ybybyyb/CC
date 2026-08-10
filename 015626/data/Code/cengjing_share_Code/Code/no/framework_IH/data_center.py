from xquant.factordata import FactorData
from multifactor.IO import IO
from multiprocessing import Pool
import pandas as pd
from function_tools import *
import datetime

def get_continuous_df(date, df_list, variety_list, instrument_type):
    print(date)
    data_list = []
    for i in range(len(variety_list)):
        v = variety_list[i]
        instrument_id = get_universe_contract(v, instrument_type, date)
        df_future_all = df_list[i]
        df_continuous_data = df_future_all[df_future_all['Ticker'] == instrument_id]
        df_continuous_data.columns = ['{}_cont_{}'.format(c, v) for c in df_continuous_data.columns]
        data_list.append(df_continuous_data)

    return pd.concat(data_list, axis=1, join='inner')

class DataCenter(object):

    def __init__(self, variety, data_type, instrument_type, data_dict, start_date, end_date, days_past):
        self.__data_type = data_type # Future / IndexStock
        self.__instrument_type = instrument_type # 'main' or 'recent'
        self.__start_date = start_date
        self.__end_date = end_date
        self.__data_dict = data_dict # data what you need
        self.__days_past = days_past # history days

        self.__variety = variety # kind IC/IF/IH

        self.__stock_data = {}
        self.__future_data_dict = {}
        self.__index_data_dict = {}
        self.__continuous_data_dict = {}

        self.__future_data = None
        self.__index_data = None
        self.__other_instrument_data = None
        self.__other_variety_data = None

        self.__minute_future_path = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE'
        self.__minute_index_path = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_INDEX/MINUTE'
        self.__minute_stock_path = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_STOCK/MINUTE_IH'
        self.__index_weights_path = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5'
        '''
        ARCH1数据   
        self.__minute_future_path = '/arch1/group/800466/MarketData/MD/CHINA_FUTURES/MINUTE'
        self.__minute_index_path = '/arch1/group/800466/MarketData/MD/CHINA_INDEX/MINUTE'
        self.__minute_stock_path = '/arch1/group/800466/MarketData/MD/CHINA_STOCK/MINUTE'
        self.__index_weights_path = '/arch1/group/800466/MarketData/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5'
        '''
        self._FUTURES = ['IC','IF','IH']
        self._INDEXES = ['000016.SH','000300.SH','000905.SH']
        self._INDEX_DICT = {'IC':'ZZ500','IF':'HS300', 'IH': 'SH50'}

        self.stock_time_index = self.get_standard_minute_time()

        self.load_data()

    def get_variety(self):
        return self.__variety
    def get_data_type(self):
        return self.__data_type
    def get_instrument_type(self):
        return self.__instrument_type
    def get_data_dict(self):
        return self.__data_dict
    def get_stock_data(self):
        return self.__stock_data
    def get_future_data(self):
        return self.__future_data
    def get_index_data(self):
        return self.__index_data
    def get_other_instrument_data(self):
        return self.__other_instrument_data
    def get_other_variety_data(self):
        return self.__other_variety_data
    def get_index_code(self):
        return self._INDEX_DICT.get(self.__variety)
    def get_future_data_dict(self):
        return self.__future_data_dict
    def get_index_data_dict(self):
        return self.__index_data_dict
    def get_continuous_data_dict(self):
        return self.__continuous_data_dict


    def get_standard_minute_time(self):
        date_list = get_trading_days(self.__start_date, self.__end_date)
        time_range = None
        for date in date_list:
            if time_range is None:
                time_range = pd.date_range(start='{} 09:30:00'.format(date), end='{} 11:29:00'.format(date), freq='1T') \
                    .append(pd.date_range(start='{} 13:00:00'.format(date), end='{} 14:56:00'.format(date), freq='1T'))
            else:
                time_range = time_range.append(
                    pd.date_range(start='{} 09:30:00'.format(date), end='{} 11:29:00'.format(date), freq='1T') \
                    .append(pd.date_range(start='{} 13:00:00'.format(date), end='{} 14:56:00'.format(date), freq='1T')))

        return time_range

    def load_future_data(self, variety):
        print('Loading {} data...'.format(variety))
        # self.__future_data_dict[variety] = IO.read_data([self.__start_date,self.__end_date+'235959'],alt='{}/{}_MINUTE_56.h5'.format(self.__minute_future_path,variety))
        temp = IO.read_data([self.__start_date,self.__end_date+'235959'],alt='{}/{}_MINUTE.h5'.format(self.__minute_future_path,variety))
        temp = temp.reset_index(level = 1).between_time(datetime.time(9,30), datetime.time(14,56)).reset_index().set_index(['dt','Ticker'])
        self.__future_data_dict[variety] = temp


    def load_index_data(self, index_code):
        print('Loading {} data...'.format(index_code))
        self.__index_data_dict[index_code] = IO.read_data([self.__start_date,self.__end_date+'235959'],alt='{}/{}.h5'.format(self.__minute_index_path,index_code)).reset_index(level = 1)

    def get_stock_fields(self, symbol, fields):

        try:
            df_stock = IO.read_data([self.__start_date, self.__end_date+'235959'],columns=fields,
                                    alt='{}/{}.h5'.format(self.__minute_stock_path, symbol)).reset_index(level = 1).reindex(self.stock_time_index)
        except:
            df_stock = pd.DataFrame(columns=fields).reindex(self.stock_time_index)

        data_dict = {}

        for i in fields:
            data_dict[i] = df_stock[i].values

        return data_dict

    def load_stock_data(self):
        # df_weight = pd.read_pickle(self.__index_weights_path)
        # stock_list = list(df_weight.swaplevel().loc[self._INDEX_DICT.get(self.__variety)]['stock'].unique())
        stock_list = get_all_stocklist_by_period(self.__variety, self.__start_date, self.__end_date)
        print('Loading index stock data for {}...'.format(self.__variety))

        tasks = []

        assert self.__data_dict.get('Stock') is not None
        fields = self.__data_dict.get('Stock')

        for i in fields:
            exec('data_{} = []'.format(i))

        with Pool(24) as pool:
            for symbol in stock_list:
                tasks.append([symbol, pool.apply_async(self.get_stock_fields, args=(symbol, fields))])

            for s, t in tasks:
                temp_result = t.get()
                for i in fields:
                    exec("data_{}.append(temp_result['{}'])".format(i, i))

        for i in fields:
            exec("self.get_stock_data()['{}'] = pd.DataFrame(np.transpose(data_{}),index=self.stock_time_index,columns=stock_list).astype('float')".format(i, i))

    def load_continuous_data(self):

        variety_list = list(self.__data_dict['Continuous_Data'].keys())
        trading_days = get_trading_days(self.__start_date, self.__end_date)

        tasks = []
        data_dict = dict()

        p_num  = 24

        with Pool(p_num) as pool:
            for date in trading_days:
                date_list = get_trading_days('20000101', date)[-self.__days_past - 1:]
                dt1 = date_list[0]
                dt2 = date_list[-1]
                df_list = [self.__future_data_dict.get(v).reset_index().set_index('dt').loc[dt1:dt2][['Ticker']+self.__data_dict['Continuous_Data'].get(v)] for v in variety_list]
                tasks.append([pool.apply_async(get_continuous_df,args=(date,df_list,variety_list,self.__instrument_type,)),date])


            for t,d in tasks:
                data_dict[d] = t.get()

        self.__continuous_data_dict = data_dict
        # print(data_dict.keys())

    def load_data(self):
        # load index data
        if self.__data_dict.get('Index_Id') is not None:
            index_data_list = []
            for i,v in self.__data_dict.get('Index_Id').items():
                self.load_index_data(i)
                df_temp = self.__index_data_dict[i][v]
                df_temp.columns = ['{}_{}'.format(c,i) for c in v]
                index_data_list.append(df_temp)

            self.__index_data = pd.concat(index_data_list,axis=1)

        # load future data
        if self.__data_dict.get('Future_Data') is not None:
            self.load_future_data(self.__variety)
            data_fields = self.__data_dict.get('Future_Data')
            future_data = self.__future_data_dict[self.__variety]
            self.__future_data = select_data_by_univ(data = future_data, variety = self.__variety, instrument_type = self.__instrument_type).reset_index().set_index('dt')[data_fields]

        # load other instrument
        if self.__data_dict.get('Other_Future_Instrument') is not None:

            if self.__data_dict.get('Future_Data') is None:
                self.load_future_data(self.__variety)

            df_temp = self.__future_data_dict[self.__variety]
            temp_dict = self.__data_dict.get('Other_Future_Instrument')
            other_instrument_list = []
            for k,v in temp_dict.items():
                if k == '00':
                    df_temp_instrument = df_temp.groupby(level=0).head(1).groupby(level=0).last()[v]
                    df_temp_instrument.columns = ['{}_{}'.format(i,k) for i in v]
                elif k == '01':
                    df_temp_instrument = df_temp.groupby(level=0).head(2).groupby(level=0).last()[v]
                    df_temp_instrument.columns = ['{}_{}'.format(i,k) for i in v]
                elif k == '02':
                    df_temp_instrument = df_temp.groupby(level=0).head(3).groupby(level=0).last()[v]
                    df_temp_instrument.columns = ['{}_{}'.format(i,k) for i in v]
                elif k == '03':
                    df_temp_instrument = df_temp.groupby(level=0).head(4).groupby(level=0).last()[v]
                    df_temp_instrument.columns = ['{}_{}'.format(i,k) for i in v]

                other_instrument_list.append(df_temp_instrument)

            self.__other_instrument_data = pd.concat(other_instrument_list,axis=1,join='inner')


        # load other variety
        if self.__data_dict.get('Other_Variety') is not None:
            other_variety_dict = self.__data_dict.get('Other_Variety')
            other_variety_data_list = []
            for k,v in other_variety_dict.items():
                self.load_future_data(k)
                df_temp_variety = self.__future_data_dict[k][v].groupby(level=0).head(1).groupby(level=0).last()[v]
                df_temp_variety.columns = ['{}_{}'.format(i,k) for i in v]
                other_variety_data_list.append(df_temp_variety)

            self.__other_variety_data = pd.concat(other_variety_data_list,axis=1)

        # load continuous fields
        if self.__data_dict.get('Continuous_Data') is not None:
            for k,v in self.__data_dict.get('Continuous_Data').items():
                if self.__future_data_dict.get(k) is None:
                    self.load_future_data(k)
            print('Loading continuous data...')
            self.load_continuous_data()

        # load stock data
        if self.__data_type == 'IndexStock' and self.__data_dict.get('Stock') is not None:
            self.load_stock_data()