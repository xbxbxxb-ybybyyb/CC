from multifactor.IO import IO
import multifactor.utility.dt as udt
from multiprocessing import Pool
import pandas as pd
import datetime, os, traceback
import bottleneck as bk
import numpy as np
import time

future_universe_path = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/UNIV/CHINA_COMMODITY_MAIN_SECONDMAIN_PERDAY_NO_DAYS.h5'
commodity_data_rootpath = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD'

class TaskRunner(object):
    def __init__(self, save_factor = False, factor_root_path = None):
        if factor_root_path is None:
            OUTER_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
            self.factor_root_path = '{}/data_center/factor_data'.format(OUTER_ROOT_PATH)
        else:
            self.factor_root_path = factor_root_path
        self.save_factor = save_factor

    def prepare_data(self, data_center, days_past, date, variety):
        date = str(date)
        assert isinstance(days_past, int) and days_past >= 0, 'Invalid input of days_past!!!'
        prepared_data = data_center.get_continuous_data_dict()[variety][date]
        today_time_index = prepared_data[prepared_data.tday == int(date)].index
        return prepared_data, today_time_index

    def run_factor_single_day(self, factor, date, variety, prepared_data=None, time_index=None, data_center=None):
        date = str(date)
        # print(date)
        if data_center is not None:
            try:
                data,index = self.prepare_data(data_center,factor.days_past,date, variety)
            except Exception as e:
                return
        else:
            data = prepared_data
            index = time_index
        data_player = DataPlayer(date, factor.days_past, data, index, factor.required_columns)
        factor_value_list = []
        stime = time.time()
        for _data in data_player.pre_data_generator:
            factor.pre_calculate(_data)
        # print('pre_calculate time use: ', round((time.time() - stime) * 1000, 3), ' ms')
        time_list = []
        for _data in data_player.today_data_generator:
            stime = time.time()
            factor_value_list.append(factor.calculate(_data))
            time_list.append(time.time() - stime)
        # print('calculate per bar time use: ', round(np.nanmean(time_list) * 1000, 3), ' ms')
        df_factor = pd.DataFrame(factor_value_list, index=index, columns=[factor.factor_name])
        return df_factor

    def run_factor_single_day_wrapper(self, task):

        factor, date, variety, prepared_data, time_index, data_center= task[0], task[1], task[2], task[3], task[4], task[5]
        date = str(date)
        # print(date)
        if data_center is not None:
            try:
                data,index = self.prepare_data(data_center,factor.days_past,date, variety)
            except Exception as e:
                print('Preparation Wrong!!', e)
                return
        else:
            data = prepared_data
            index = time_index
        data_player = DataPlayer(date, factor.days_past, data, index, factor.required_columns)
        factor_value_list = []
        #stime = time.perf_counter()

        for _data in data_player.pre_data_generator:
            factor.pre_calculate(_data)
        #print(date, '  pre_calculate time use: ', round((time.perf_counter() - stime) * 1000, 3), ' ms')
        ttemp = data_player.today_data_generator
        #time_list = []

        for _data in ttemp:
            #stime = time.perf_counter()
            factor_value_list.append(factor.calculate(_data))
            #time_list.append(time.perf_counter()- stime)

        #print(date, '  calculate per bar time use: ', round(np.nansum(time_list) * 1000, 3), ' ms')
        df_factor = pd.DataFrame(factor_value_list, index=index, columns=[factor.factor_name])
        return df_factor

    def run_factor_multi_day(self, factor, variety, data_center, start_date, end_date, parallel_num=24):

        date_list = [x.strftime('%Y%m%d') for x in udt.get_trading_date_range(start_date, end_date)]
        pool = Pool(parallel_num)
        tasks = []

        for date in date_list:
            prepared_data, time_index = self.prepare_data(data_center, factor.days_past,date, variety)
            tasks.append([pool.apply_async(self.run_factor_single_day, args=(factor,date,variety,prepared_data,time_index)), factor.factor_name, variety, date])

        pool.close()

        factor_list = []
        for t,n,v,d in tasks:
            try:
                factor_list.append(t.get())
            except Exception as e:
                print(e,traceback.format_exc())

        pool.join()

        df_factor = pd.concat(factor_list)

        assert factor.normalize_type in ['ts_rank','rolling_norm'], 'Invalid normalize type!!!'
        assert isinstance(factor.normalize_size,int), 'The normalized size of factor should be integer!!!'

        df_normalized_factor = None

        if factor.normalize_size in [0, 1]:
            df_normalized_factor = df_factor.copy()
        else:
            if factor.normalize_type == 'ts_rank':
                df_normalized_factor = self.ts_rank(df_factor, factor.normalize_size)
            # elif factor.normalize_type == 'rolling_norm':
            #     df_normalized_factor = self.rolling_norm(df_factor, factor.normalize_size)

        # Save the raw/norm value of the factor
        if self.save_factor:
            self.save_to_h5(df_factor, df_normalized_factor, factor.factor_name)

        return df_factor, df_normalized_factor

    def save_to_h5(self, df_raw, df_norm, name, method = 'h5'):

        path_raw = os.path.join(self.factor_root_path,'minute_raw')
        path_norm = os.path.join(self.factor_root_path,'minute_norm')

        if not os.path.exists(path_raw):
            os.makedirs(path_raw)
        if not os.path.exists(path_norm):
            os.makedirs(path_norm)
        if method == 'h5':
            self.pd_writer(df_raw, path_raw)
            self.pd_writer(df_norm, path_norm)
        elif method == 'parquet':
            self.pq_writer(df_raw, path_raw)
            self.pq_writer(df_norm, path_norm)
        else:
            print('FUCK YOU!', method)
            assert 1 == 2


        # df_raw.to_hdf(os.path.join(path_raw, '%s.h5' % name), 'minute_data')
        # df_norm.to_hdf(os.path.join(path_norm, '%s.h5' % name), 'minute_data')

        print('Factor {} is saved.'.format(name))

    def pd_writer(self, sig, savepath):
        sig_name = sig.columns[0]
        file_name = os.path.join(savepath, sig_name + '.h5')
        if os.path.exists(file_name):
            #sigold = IO.read_data(alt = file_name)
            sigold = pd.read_hdf(file_name)
            sigold = sigold[~sigold.index.isin(sig.index)]
            signew = pd.concat([sigold,sig],axis=0).sort_index()
        else:
            signew = sig
        signew.to_hdf(file_name,key='minute_data')

    def pq_writer(self, sig, savepath):
        sig_name = sig.columns[0]
        file_name = os.path.join(savepath, sig_name + '.parquet')
        if os.path.exists(file_name):
            #sigold = IO.read_data(alt = file_name)
            sigold = pd.read_parquet(file_name)
            sigold = sigold[~sigold.index.isin(sig.index)]
            signew = pd.concat([sigold,sig],axis=0).sort_index()
        else:
            signew = sig
        signew.to_parquet(file_name)


    def ts_rank(self, df1, d=4800):
        # moving time-series rank for the past d periods
        assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
        if d == 1:
            output = df1
        else:
            if isinstance(df1, pd.DataFrame):
                output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                      index=df1.index, columns=df1.columns)
            elif isinstance(df1, pd.Series):
                output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                   index=df1.index, name=df1.name)
        return output

    def calc_zscore(self, dat1, window, min_periods = 1):
        dat = dat1.copy()
        vol = dat.rolling(window, min_periods).std()
        vol[abs(vol) < 1e-8] = np.nan
        result = (dat - dat.rolling(window, min_periods).mean()) / vol
        result[result > 5] = 5
        result[result < -5] = -5
        del dat
        return result


class DataPlayer(object):
    def __init__(self, date, days_past, data, today_index, play_columns):
        self.date = date
        self.days_past = days_past
        self.prepared_data = data
        self.today_index = today_index
        self.play_columns = play_columns

    @property
    def today_data_generator(self):
        play_data = self.prepared_data.reset_index()
        play_data = {col: play_data[col].values for col in self.play_columns}

        for i in range(len(self.today_index)-1, -1, -1):
            if i == 0:
                yield play_data
            else:
                yield {k:v[:-i] for k,v in play_data.items()}

    @property
    def pre_data_generator(self):
        date_list = sorted(np.unique(self.prepared_data.dropna(subset = ['tday']).tday))
        if len(date_list) == 1:
            history_data = pd.DataFrame()
        else:
            history_data = self.prepared_data[self.prepared_data.tday < date_list[-1]]
        if len(history_data) > 0:
            play_data = history_data.reset_index()
            yield {col: play_data[col].values for col in self.play_columns}
        else:
            yield {col: np.array([]) for col in self.play_columns}


def get_universe_contract(variety = 'IC', instrument_type = 'main', date = None):
    assert instrument_type in ['main', 'second_main'], 'instrument type must be in [main, second_main]'
    col_dict = {'main':'contract_main', 'second_main':'contract_second_main'}
    col_name = col_dict[instrument_type]
    univ = IO.read_data([date],columns=[col_name], alt = future_universe_path)
    if len(univ) == 0:
        print('the date maybe is not trading day')
        raise Exception
    return univ.xs('%s' % variety, level = 1)[col_name][0]

class DataCenter(object):

    def __init__(self, variety_list, data_freq, required_columns, start_date, end_date, days_past, parallel_num = 24):
        self.__data_freq = data_freq
        self.__start_date = str(start_date)
        self.__end_date = str(end_date)

        self.main_required_columns = []
        self.secmain_required_columns = []
        self._secmain_required_columns = []
        for col in required_columns:
            if col.endswith('_secmain'):
                self.secmain_required_columns.append(col)
                self._secmain_required_columns.append(col.replace('_secmain', ''))
            else:
                self.main_required_columns.append(col)

        self.__required_columns = list(set(self.main_required_columns + self._secmain_required_columns)) # data what you need
        self.__days_past = days_past # history days

        self.__variety_list = variety_list # kind IC/IF/IH

        self.__continuous_data_dict = {}

        self.__future_data = None
        self.__parallel_num = parallel_num

        self.__minute_future_path = os.path.join(commodity_data_rootpath, str.upper(data_freq), 'PER_TICKER')

        self.__trading_days = [x.strftime('%Y%m%d') for x in udt.get_trading_date_range(self.__start_date, self.__end_date)]

        self.load_data()

    def get_variety_list(self):
        return self.__variety_list

    def get_continuous_data_dict(self):
        return self.__continuous_data_dict

    def load_future_data(self, variety, columns):
        if 'tday' not in columns:
            columns += ['tday']

        columns_temp = columns.copy()
        if 'dt' in columns:
            columns_temp.remove('dt')
        future_data = IO.read_data([udt.get_trading_day_offset(self.__start_date, -(self.__days_past + 5))[0].strftime('%Y%m%d'), self.__end_date+'235959'],columns = columns_temp, alt='{}/{}.h5'.format(self.__minute_future_path,variety))
        future_data['tday'] = future_data['tday'].astype('int')
        return future_data

    def get_data_helper(self, para):
        date = para[0]
        variety = para[1]
        try:
            date_list = udt.get_trading_date_range('20000101', date)[-self.__days_past - 1:]
            dt1 = int(date_list[0].strftime('%Y%m%d'))
            dt2 = int(date_list[-1].strftime('%Y%m%d'))
            _future_data = self.future_data[(self.future_data['tday'] >= dt1) & (self.future_data['tday'] <= dt2)]
            _all_ticker_list = _future_data.index.get_level_values(1).unique().tolist()

            contract = get_universe_contract(variety, 'main', date)
            if contract in _all_ticker_list:
                select = _future_data.xs(contract, level = 1)
                select['contract'] = contract
            else:
                select = pd.DataFrame(columns = _future_data.columns)

            secmain_contract = get_universe_contract(variety, 'second_main', date)
            if secmain_contract in _all_ticker_list:
                secmain_select = _future_data.xs(secmain_contract, level = 1).add_suffix('_secmain')
                secmain_select['contract_secmain'] = secmain_contract
            else:
                secmain_select = pd.DataFrame(columns = [f'{x}_secmain' for x in _future_data.columns])

            return {date : pd.concat([select, secmain_select], axis = 1)}
        except Exception as e:
            print(para, e)
            return None

    def get_continus_data_for_variety(self, variety):
        self.future_data = self.load_future_data(variety, self.__required_columns)
        
        with Pool(self.__parallel_num) as pool:
            rlist = pool.map(self.get_data_helper, [(x, variety) for x in self.__trading_days])

        continuous_dict = {k: v for d in rlist if d is not None for k, v in d.items()}
        return continuous_dict

    def load_data(self):
        print('DataCenter initializing')
        for variety in self.__variety_list:
            self.__continuous_data_dict[variety] = self.get_continus_data_for_variety(variety)
        print('DataCenter done')

class FutureFactor(object):

    def __init__(self):
        self.days_past = 0
        self.required_columns = ['close', 'volume', 'low']
        self.normalize_size = 20 * 240
        self.normalize_type = 'ts_rank'

        self.factor_name = self.__class__.__name__
        self.bars_dict = {'A.DCE': 345,
                 'AG.SHF': 555,
                 'AL.SHF': 465,
                 'AO.SHF': 465,
                 'AP.ZCE': 225,
                 'AU.SHF': 555,
                 'B.DCE': 345,
                 'BB.DCE': 225,
                 'BC.INE': 465,
                 'BR.SHF': 345,
                 'BU.SHF': 345,
                 'C.DCE': 345,
                 'CF.ZCE': 345,
                 'CJ.ZCE': 225,
                 'CS.DCE': 345,
                 'CU.SHF': 465,
                 'CY.ZCE': 345,
                 'EB.DCE': 345,
                 'EC.INE': 225,
                 'EG.DCE': 345,
                 'FB.DCE': 225,
                 'FG.ZCE': 345,
                 'FU.SHF': 345,
                 'HC.SHF': 345,
                 'I.DCE': 345,
                 'IC.CFE': 240,
                 'IF.CFE': 240,
                 'IH.CFE': 240,
                 'IM.CFE': 240,
                 'J.DCE': 345,
                 'JD.DCE': 225,
                 'JM.DCE': 345,
                 'JR.ZCE': 225,
                 'L.DCE': 345,
                 'LC.GFE': 225,
                 'LH.DCE': 225,
                 'LR.ZCE': 225,
                 'LU.INE': 345,
                 'M.DCE': 345,
                 'MA.ZCE': 345,
                 'NI.SHF': 465,
                 'NR.INE': 345,
                 'OI.ZCE': 345,
                 'P.DCE': 345,
                 'PB.SHF': 465,
                 'PF.ZCE': 345,
                 'PG.DCE': 345,
                 'PK.ZCE': 225,
                 'PM.ZCE': 225,
                 'PP.DCE': 345,
                 'PR.ZCE': 345,
                 'PX.ZCE': 345,
                 'RB.SHF': 345,
                 'RI.ZCE': 225,
                 'RM.ZCE': 345,
                 'RR.DCE': 345,
                 'RS.ZCE': 225,
                 'RU.SHF': 345,
                 'SA.ZCE': 345,
                 'SC.INE': 555,
                 'SF.ZCE': 225,
                 'SH.ZCE': 345,
                 'SI.GFE': 225,
                 'SM.ZCE': 225,
                 'SN.SHF': 465,
                 'SP.SHF': 345,
                 'SR.ZCE': 345,
                 'SS.SHF': 465,
                 'T.CFE': 255,
                 'TA.ZCE': 345,
                 'TF.CFE': 255,
                 'TL.CFE': 255,
                 'TS.CFE': 255,
                 'UR.ZCE': 225,
                 'V.DCE': 345,
                 'WH.ZCE': 225,
                 'WR.SHF': 225,
                 'Y.DCE': 345,
                 'ZC.ZCE': 375,
                 'ZN.SHF': 465,
                 'PS.GFE': 225,
                 'LG.DCE': 225}
        self.tick_size_dict = {'A.DCE': 1.0,
                 'AG.SHF': 1.0,
                 'AL.SHF': 5.0,
                 'AO.SHF': 1.0,
                 'AP.ZCE': 1.0,
                 'AU.SHF': 0.02,
                 'B.DCE': 1.0,
                 'BB.DCE': 0.05,
                 'BC.INE': 10.0,
                 'BR.SHF': 5.0,
                 'BU.SHF': 1.0,
                 'C.DCE': 1.0,
                 'CF.ZCE': 5.0,
                 'CJ.ZCE': 5.0,
                 'CS.DCE': 1.0,
                 'CU.SHF': 10.0,
                 'CY.ZCE': 5.0,
                 'EB.DCE': 1.0,
                 'EC.INE': 0.1,
                 'EG.DCE': 1.0,
                 'FB.DCE': 0.5,
                 'FG.ZCE': 1.0,
                 'FU.SHF': 1.0,
                 'HC.SHF': 1.0,
                 'I.DCE': 0.5,
                 'IC.CFE': 0.2,
                 'IF.CFE': 0.2,
                 'IH.CFE': 0.2,
                 'IM.CFE': 0.2,
                 'J.DCE': 0.5,
                 'JD.DCE': 1.0,
                 'JM.DCE': 0.5,
                 'JR.ZCE': 1.0,
                 'L.DCE': 1.0,
                 'LC.GFE': 50.0,
                 'LG.DCE': 0.5,
                 'LH.DCE': 5.0,
                 'LR.ZCE': 1.0,
                 'LU.INE': 1.0,
                 'M.DCE': 1.0,
                 'MA.ZCE': 1.0,
                 'NI.SHF': 10.0,
                 'NR.INE': 5.0,
                 'OI.ZCE': 1.0,
                 'P.DCE': 2.0,
                 'PB.SHF': 5.0,
                 'PF.ZCE': 2.0,
                 'PG.DCE': 1.0,
                 'PK.ZCE': 2.0,
                 'PM.ZCE': 1.0,
                 'PP.DCE': 1.0,
                 'PR.ZCE': 2.0,
                 'PS.GFE': 5.0,
                 'PX.ZCE': 2.0,
                 'RB.SHF': 1.0,
                 'RI.ZCE': 1.0,
                 'RM.ZCE': 1.0,
                 'RR.DCE': 1.0,
                 'RS.ZCE': 1.0,
                 'RU.SHF': 5.0,
                 'SA.ZCE': 1.0,
                 'SC.INE': 0.1,
                 'SF.ZCE': 2.0,
                 'SH.ZCE': 1.0,
                 'SI.GFE': 5.0,
                 'SM.ZCE': 2.0,
                 'SN.SHF': 10.0,
                 'SP.SHF': 2.0,
                 'SR.ZCE': 1.0,
                 'SS.SHF': 5.0,
                 'T.CFE': 0.005,
                 'TA.ZCE': 2.0,
                 'TF.CFE': 0.005,
                 'TL.CFE': 0.01,
                 'TS.CFE': 0.002,
                 'UR.ZCE': 1.0,
                 'V.DCE': 1.0,
                 'WH.ZCE': 1.0,
                 'WR.SHF': 1.0,
                 'Y.DCE': 2.0,
                 'ZC.ZCE': 0.2,
                 'ZN.SHF': 5.0}




    def calculate(self, data):

        factor_result = None

        return factor_result

    def pre_calculate(self, data):
        pass
