import numpy as np
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as tdt
import multifactor.utility.common as ut
from multifactor.IO.naming_config import futures_contract_info_path, futures_universe_path, private_h5root
from WindPy import w
import os
import re
w.start()


class CommodityDaily:
    def __init__(self, start_date, end_date, mode):
        self.start_date = IO.str_date_parser(start_date)
        self.end_date = IO.str_date_parser(end_date)
        assert self.end_date >= self.start_date
        self.mode = mode
        self.md_data = None  # multi-index
        self.main_contract = None  # multi-index
        self.second_main_contract = None  # multi-index
        self.universe_pd = None
        self.contract_info_pd = None
        # path related
        self.md_path = IO.path_assembler(mkttype=MktType.CHINA, dtype=DType.FUTURES, ftype=FType.MD,
                                         dfreq=DFreq.DAILY, dsource=DSource.WIND, dtable=None,
                                         alt=None, h5root=private_h5root)
        self.main_contract_path = IO.path_assembler(mkttype=MktType.CHINA, dtype=DType.FUTURES, ftype=FType.MD,
                                                    dfreq=DFreq.DAILY, dsource=DSource.MAIN, dtable=None,
                                                    alt=None, h5root=private_h5root)
        self.second_main_contract_path = IO.path_assembler(mkttype=MktType.CHINA, dtype=DType.FUTURES, ftype=FType.MD,
                                                           dfreq=DFreq.DAILY, dsource=DSource.SECONDMAIN, dtable=None,
                                                           alt=None, h5root=private_h5root)
        self.universe_path = IO.path_assembler(mkttype=MktType.CHINA, dtype=DType.FUTURES, ftype=FType.UNIV,
                                               dfreq=DFreq.DAILY, dsource=DSource.WIND, dtable=None,
                                               alt=None, h5root=private_h5root)

    @staticmethod
    def get_wind_code(date):
        date = IO.str_date_parser(date).strftime('%Y%m%d')
        cfe = 'a599010101000000'
        shf = 'a599010201000000'
        dce = 'a599010301000000'
        czc = 'a599010401000000'
        exchanges = [cfe, shf, dce, czc]
        code_list = []
        for ec in exchanges:
            try:
                data = w.wset("sectorconstituent", "date="+date+";sectorid="+ec+";field=date,wind_code,sec_name")
                data = pd.DataFrame(data.Data, index=data.Fields).T
                data=data[data['sec_name'].apply(lambda x: "仿真" not in x)]
                code_list.extend(data['wind_code'].tolist())
            except:
                continue
        assert len(code_list) != 0, 'No codes retrieved'
        return code_list

    @staticmethod
    def calculate_gap(contract):
        contract = contract.sort_index(level=0)
        gap = (contract['PRE_CLOSE'] - contract['CLOSE'].shift(1)).fillna(0)
        gap.name = 'GAP'
        return gap.cumsum()

    @staticmethod
    def expiration_days_helper(x):
        if x.cd > x.dd:
            return np.nan
        else:
            return len(tdt.get_trading_date_range(x.cd, x.dd)) - 1

    def get_daily_data(self):
        trading_days = tdt.get_trading_date_range(tdt.get_trading_day_offset(self.start_date, -1)[0], self.end_date)
        md_data_list = []
        wind_code_set = set()
        for td in trading_days:
            print(td)
            wind_code_list = self.get_wind_code(td)
            wind_code_set.update(wind_code_list)
            md_data = w.wss(wind_code_list, "pre_settle,pre_close,open,high,low,close,volume,amt,oi,settle", "tradeDate="+\
                            td.strftime('%Y%m%d')+";priceAdj=U;cycle=D")
            md_data = pd.DataFrame(np.array(md_data.Data).T.tolist(), columns=md_data.Fields, index=md_data.Codes).reset_index()
            md_data['dt'] = td
            md_data_list.append(md_data)
            md_data['PRE_CLOSE'] = md_data['PRE_CLOSE'].where(md_data['PRE_CLOSE'].notnull(),
                                                              other=md_data['OPEN'])
            md_data['PRE_SETTLE'] = md_data['PRE_SETTLE'].where(md_data['PRE_SETTLE'].notnull(),
                                                                other=md_data['OPEN'])
        md_data = pd.concat(md_data_list, axis=0)
        md_data['PROD_ID'] = md_data['index'].apply(lambda x: "".join(re.findall(r'[A-Za-z]', x.split('.')[0])) + '.' + x.split('.')[1])
        md_data['EXCHANGE'] = md_data['index'].apply(lambda x: x.split('.')[1])
        md_data = md_data.set_index(['dt', 'index']).sort_index(level=0)
        md_data.index.names = ['dt','Ticker']
        self.md_data = md_data
        # retrieve contract information
        contract_info = w.wss(list(wind_code_set), "changelt,contractmultiplier,lasttrade_date")
        contract_info_pd = pd.DataFrame(np.array(contract_info.Data).T.tolist(),
                                        columns=contract_info.Fields, index=contract_info.Codes)
        contract_info_pd['CHANGELT'] = contract_info_pd['CHANGELT'] / 100
        contract_info_pd['PROD_ID'] = contract_info_pd.index
        contract_info_pd['PROD_ID'] = contract_info_pd['PROD_ID'].apply(
                                      lambda x: "".join(re.findall(r'[A-Za-z]', x.split('.')[0])) + '.' + x.split('.')[1])
        if self.contract_info_pd is None:
            self.contract_info_pd = contract_info_pd
        else:
            self.contract_info_pd = contract_info_pd.combine_first(self.contract_info_pd)
        # add other calculated data
        self.md_data['OM'] = self.md_data['OI'].multiply(self.contract_info_pd['CONTRACTMULTIPLIER'], level=1)
        self.md_data['LIMIT_UP'] = self.md_data['PRE_SETTLE'].multiply(1 + self.contract_info_pd['CHANGELT'], level=1)
        self.md_data['LIMIT_DOWN'] = self.md_data['PRE_SETTLE'].multiply(1 - self.contract_info_pd['CHANGELT'], level=1)
        self.md_data['LIMIT_UP'] = self.md_data['HIGH'].where(self.md_data['LIMIT_UP'] <= self.md_data['HIGH'],
                                                              self.md_data['LIMIT_UP'])
        self.md_data['LIMIT_DOWN'] = self.md_data['LOW'].where(self.md_data['LIMIT_DOWN'] >= self.md_data['LOW'],
                                                               self.md_data['LIMIT_DOWN'])
        self.md_data['TURN'] = self.md_data['VOLUME'] / self.md_data['OI']
        current_date = pd.Series(self.md_data.index.get_level_values(level=0), index=self.md_data.index)
        current_date.name = 'cd'
        dummy_date = pd.Series(pd.Timedelta('0D'), index=self.md_data.index).add(self.contract_info_pd['LASTTRADE_DATE'], level=1)
        dummy_date.name = 'dd'
        self.md_data['EXPIRATION_DAYS'] = pd.concat([current_date, dummy_date], axis=1).apply(self.expiration_days_helper, axis=1)

    def calculate_main_contract(self):
        md_base_data = IO.read_data(alt=self.md_path)
        md_data = md_base_data.reset_index()
        self.main_contract = md_data.loc[md_data.groupby(['dt', 'PROD_ID'])['OI'].idxmax().dropna()].set_index(['dt', 'Ticker'])
        self.main_contract = self.main_contract.sort_index(level=0)
        md_data = md_base_data.drop(self.main_contract.index).reset_index()
        self.second_main_contract = md_data.loc[md_data.groupby(['dt', 'PROD_ID'])['OI'].idxmax().dropna()].set_index(['dt', 'Ticker'])
        self.second_main_contract = self.second_main_contract.sort_index(level=0)
        self.main_contract['GAP'] = self.main_contract.groupby('PROD_ID').apply(
                                    self.calculate_gap).reset_index(level=0, drop=True).sort_index(level=0)
        self.second_main_contract['GAP'] = self.second_main_contract.groupby('PROD_ID').apply(
                                           self.calculate_gap).reset_index(level=0, drop=True).sort_index(level=0)
        self.main_contract = self.main_contract.reset_index().rename(columns= \
                            {'Ticker': 'WIND_CODE', 'PROD_ID': 'Ticker'}).set_index(['dt', 'Ticker'])
        self.second_main_contract = self.second_main_contract.reset_index().rename(columns= \
                                   {'Ticker': 'WIND_CODE', 'PROD_ID': 'Ticker'}).set_index(['dt', 'Ticker'])

    def h5_helper(self, job, rebuild_flag=False):
        for dataset, data in job.items():
            h5_path, payload = data
            mode = self.mode if not rebuild_flag else 'create'
            append_mode, from_scratch = ut.h5_helper(h5_path, mode)
            if not rebuild_flag:
                payload = payload.loc[self.start_date:self.end_date]
            IO.pd_hdf5_writer(payload, h5_path, dataset, append=append_mode, from_scratch=from_scratch)

    def universe_contruct(self, look_back_days=20):
        main_contract = IO.read_data([self.start_date, self.end_date], columns=['WIND_CODE'],
                                      alt=self.main_contract_path).reset_index().rename(columns=\
                                     {'Ticker': 'PROD_ID', 'WIND_CODE': 'Ticker'}).set_index(['dt', 'Ticker'])
        main_codes = pd.DataFrame(True, index=main_contract.index, columns=['main_contract'])
        second_main_contract = IO.read_data([self.start_date, self.end_date], columns=['WIND_CODE'],
                                             alt=self.second_main_contract_path).reset_index().rename(columns=\
                                            {'Ticker': 'PROD_ID', 'WIND_CODE': 'Ticker'}).set_index(['dt', 'Ticker'])
        second_main_codes = pd.DataFrame(True, index=second_main_contract.index, columns=['second_main_contract'])
        # filter contracts whose average transaction amount less than certain threshold
        md_data = IO.read_data([tdt.get_trading_day_offset(self.start_date, -look_back_days)[0], self.end_date],
                                columns=['AMT', 'EXPIRATION_DAYS'], alt=self.md_path)
        liquid_codes = (md_data['AMT'].unstack().rolling(window=look_back_days,
                                                         min_periods=3).mean() >= 8e7).replace(False, np.nan).stack()
        liquid_codes.name = 'liquid_contract'
        # filter contracts which expire within certain days
        valid_codes = md_data['EXPIRATION_DAYS'] >= 15
        valid_codes = valid_codes.loc[valid_codes]
        valid_codes.name = 'valid_contract'
        universe_pd = pd.concat([main_codes, second_main_codes, liquid_codes, valid_codes], axis=1).fillna(False)
        universe_pd = universe_pd.astype('bool')
        universe_pd['alpha_contract'] = (universe_pd['main_contract'] | universe_pd['second_main_contract']) & \
                                         universe_pd['liquid_contract'] & universe_pd['valid_contract']
        self.h5_helper({'universe': (self.universe_path, universe_pd)})

    def pilot(self, contract_info_path):
        # load stale basic info
        if os.path.exists(contract_info_path) and self.mode == 'append':
            self.contract_info_pd = pd.read_hdf(contract_info_path)
        # retrieve data
        self.get_daily_data()
        self.h5_helper({'md': (self.md_path, self.md_data)})
        # calculation
        self.calculate_main_contract()
        # data dump
        self.contract_info_pd.to_hdf(contract_info_path, key='contract_info', mode='w')
        job_dict = {'main': (self.main_contract_path, self.main_contract),
                    'second_main': (self.second_main_contract_path, self.second_main_contract)}
        self.h5_helper(job_dict, rebuild_flag=True)
        self.universe_contruct()


if __name__ == '__main__':
    destination_path = IO.path_assembler(mkttype=MktType.CHINA, dtype=DType.FUTURES, ftype=FType.MD,
                                         dfreq=DFreq.DAILY, dsource=DSource.WIND, dtable=None,
                                         alt=None, h5root=private_h5root)
    start_date = None
    end_date = None
    if start_date is None:
        start_date = tdt.get_trading_day_offset(IO.dipping(1, columns='VOLUME', alt=destination_path).index[0][0], 1)[0]
    if end_date is None:
        end_date = tdt.get_trading_day_offset(pd.Timestamp.now(), 0)[0]
    if start_date > end_date:
        print('no need to update, abort...')
        exit()
    mode = 'append'
    contract_info_path = futures_contract_info_path
    commd = CommodityDaily(start_date=start_date,
                           end_date=end_date,
                           mode=mode)
    commd.pilot(contract_info_path)
    # For TDB
    univ_pd = IO.read_data(dtype=DType.FUTURES, ftype=FType.UNIV, h5root=private_h5root)
    univ_pd.to_csv(futures_universe_path)