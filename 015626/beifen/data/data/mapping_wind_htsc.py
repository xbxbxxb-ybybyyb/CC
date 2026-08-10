# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:17:25 2018

@author: 012315  013160
"""

import sys
from WindPy import w
import datetime as dt
import pandas as pd
import os
import numpy as np
import json
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import operator
from functools import reduce
from log import Log
import config_reader
from utils import *
# import utils
from concurrent.futures import ProcessPoolExecutor as Pool
from concurrent.futures import as_completed
import multifactor.utility.dt as tdt

logger = Log('update_wind')

w.start()

#############


def save_industry(date_list,save_path,industry_dict,use_wind_list=False,stock_code=None):
    wind_stock_path = config_reader.getConfig('root_path', 'wind_stock_path')
    fail_dict ={}

    save_folder = save_path + 'industry_citiccode'+'\\'
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    fail_dict['industry_citiccode'] = []

    for date in date_list:
        logger.info('industry_citiccode:' + str(date))
        if use_wind_list == True:
            stock_code_df = pd.read_csv(wind_stock_path+str(date)+'.csv',header=0)
            stock_code = stock_code_df['Ticker'].values.tolist()
        #所属中信行业代码
        dat1 = w.wss(stock_code,'industry_citiccode', 'tradeDate='+str(date)+';industryType=1')
        citic_ind1 =  [i[:4]=='b10m' if type(i)==str else False for i in dat1.Data[0]]
        non_bank_fin = np.array(dat1.Codes)[citic_ind1].tolist()
        dat2 = w.wss(non_bank_fin,'industry_citiccode','tradeDate='+str(date)+';industryType=2')

        if len(dat1.Data[0]) ==1 or len(dat2.Data[0]) ==1:
            logger.warning(dat1.Data[0][0])
            logger.warning('industry_citiccode tradeDate= ' + str(date))
            fail_dict['industry_citiccode'].append(date)
            raise AssertionError
        else:
            df = pd.DataFrame(dat1.Data,columns=dat1.Codes,index=['code']).T
            df['code'].loc[dat2.Codes] = dat2.Data[0]
            df.index.names= ['Ticker']
            df = df.dropna()
            df['industry_citiccode'] = df['code'].apply(lambda x:industry_dict[x])
            
            logger.info(df)
            df = df.drop(['code'],axis=1)
            df.to_csv(save_folder+str(date)+'.csv')

    return fail_dict


def get_wind_secu_status():
    logger.info('Get all stocks IPO date and delisting date')
    h5_root = config_reader.getConfig('root_path', 'h5_root')
    h5_path = h5_root + config_reader.getConfig('get_wind_secu_status', 'h5_path')
    if not os.path.exists(os.path.dirname(h5_path)):
        os.makedirs(os.path.dirname(h5_path))
    logger.debug('get_wind_secu_status: ' + h5_path)
    dat = w.wset("delistsecurity","field=wind_code,delist_date")
    #退市资料
    dat2 = w.wset("listedsecuritygeneralview","sectorid=a001010100000000;field=wind_code,ipo_date")
    #上市股票一览
    if  dat.Data[0][0]== 'CWSSService: quota exceeded.' or dat2.Data[0][0] == 'CWSSService: quota exceeded.':
        logger.warning(dat.Data[0][0])
        logger.warning(stock_need)
        raise AssertionError
    secu_status = pd.DataFrame([dat2.Data[1]],columns= dat2.Data[0],index=['ipo_date']).T
    secu_delist = pd.DataFrame([dat.Data[1]],columns= dat.Data[0],index=['delist_date']).T
    stock_take = [code for code in dat.Data[0] if code[-2:]!='OC' ]
    stock_need = list((set(dat.Data[0])-set(dat2.Data[0])).intersection(set(stock_take)))
    #首发上市日期
    dat3 = w.wss(stock_need,'ipo_date')
    if dat3.Data[0][0]== 'CWSSService: quota exceeded.':
        logger.warning(dat3.Data[0][0])
        logger.warning(stock_need)
        raise AssertionError
    secu_status2 = pd.DataFrame([dat3.Data[0]],columns= dat3.Codes,index=['ipo_date']).T
    secu_status_full = pd.concat([secu_status,secu_status2],axis=0)
    secu_status_full['delist_date'] = secu_delist.loc[stock_take]
    secu_status_full = secu_status_full.sort_index()
    secu_status_full.index.names = ['Ticker']
    # drop T and 9xxxxxxxx
    # fill delisting date with dummy large one
    secu_status_full['delist_date']= secu_status_full['delist_date'].fillna(dt.datetime.strptime('20991231','%Y%m%d'))
    final_take = [i[0] not in ['9','T'] for i in secu_status_full.index.values]
    secu_status_full = secu_status_full[final_take]

    logger.info('Create new h5: '+h5_path)
    os.remove(h5_path) if os.path.exists(h5_path) else None
    with pd.HDFStore(h5_path) as h5_store:
        h5_store.append('SecDate',secu_status_full)
    logger.info('Done')
    return





class Factor(object):
    def __init__(self, start_date, end_date, dtype, dfreq, dsource, mkttype, ftype, factor_list, operation='append', factor_scale = None, stock_list= None, max_process=5):
        self.stock_list = stock_list
        self.factor_scale = factor_scale
        self.factor_list = factor_list
        self.dtype = dtype
        self.dfreq = dfreq
        self.dsource = dsource
        self.mkttype = mkttype
        self.ftype = ftype
        self.start_date = start_date
        self.end_date = end_date
        self.operation = 'append'
        self.max_process = max_process
        self.sdate_prev,self.edate,self.cdate_list = check_update_date(self.start_date,self.end_date)
        self.csv_path = config_reader.getConfig('root_path', 'csv_path')
        if self.dtype.name is INDEX:
            self.csv_path = self.csv_path + 'index\\'
        self.h5_root = config_reader.getConfig('root_path', 'h5_root')
        self.h5_path = IO.path_assembler(mkttype=mkttype, dtype=dtype, ftype=ftype, dfreq=dfreq, dsource=dsource, alt=None, h5root=self.h5_root)
        print(self.h5_path)
        if not os.path.exists(os.path.dirname(self.h5_path)):
            os.makedirs(os.path.dirname(self.h5_path))
        if not os.path.exists(os.path.dirname(self.csv_path)):
            os.makedirs(os.path.dirname(self.csv_path))
        self.fail_dict_master = {}
        self.fail_dict_master['stock_list'] = get_stock_list(self.cdate_list)

    def retriever(self, checker=None):
        pass

    def csv_to_database(self, h5_checker = None):
        pass

    def cronb(self):
        self.retriever()
        self.csv_to_database()


class DailyFactor(Factor):
    def retriever(self, checker=None):
        dict_name = self.ftype.name + '_' + self.dfreq.name
        if self.stock_list:
            self.fail_dict_master[dict_name] = save_one_factor(self.factor_list,self.cdate_list,self.csv_path, stock_code=self.stock_list)
        else:
            self.fail_dict_master[dict_name] = save_one_factor(self.factor_list,self.cdate_list,self.csv_path, use_wind_list=True)

    def csv_to_database(self, h5_checker = None):
        dict_name = self.ftype.name + '_' + self.dfreq.name + '_h5'
        self.fail_dict_master[dict_name] = update_wind_daily_h5(self.cdate_list, self.factor_list, self.csv_path,
                                                            self.h5_path, operation=self.operation, factor_scale=self.factor_scale)

class QuarterlyFactor(Factor):
    def retriever(self, checker=None):
        # print('pass')
        dict_name = self.ftype.name + '_' + self.dfreq.name
        self.fail_dict_master[dict_name] = get_wind_qtr_csv(self.cdate_list,self.csv_path,self.factor_list)

    def csv_to_database(self, h5_checker = None):
        dict_name = self.ftype.name + '_' + self.dfreq.name + '_h5'
        qtr_list, stock_code = get_qtr_list(self.cdate_list, num_qtr=3)
        self.fail_dict_master['fdd_qtr_h5'] = update_wind_qtr_h5(qtr_list,self.factor_list,self.csv_path,self.h5_path, operation=self.operation)
        h5_daily_fdd_path = IO.path_assembler(mkttype=self.mkttype, dtype=self.dtype, ftype=self.ftype, dfreq=DFreq.DAILY, dsource=self.dsource, alt=None, h5root=self.h5_root)
        self.fail_dict_master['fdd_qtr2daily_h5']  = update_wind_qtr2daily(self.cdate_list[0], self.cdate_list[-1],self.h5_path,h5_daily_fdd_path,operation=self.operation, max_process=self.max_process)

class INDEX(DailyFactor):
    def __init__(self, start_date, end_date):
        index_list = ['000016.SH','000300.SH','000905.SH','000906.SH','399005.SZ','399006.SZ']
        factor_list = ['close', 'pre_close']
        super(INDEX, self).__init__(start_date=start_date, end_date=end_date, dtype=DType.INDEX,
                dfreq=DFreq.DAILY, dsource=DSource.WIND, mkttype=MktType.CHINA, ftype=FType.MD, factor_list=factor_list, stock_list=index_list)


class MD(DailyFactor):
    def __init__(self, start_date, end_date):
        md_list = ['close','open','high','low','vwap','adjfactor','turn','volume','pct_chg',
                        'pre_close','total_shares','amt','free_float_shares','mkt_cap_ard']
        factor_scale ={'amt':10**3,'free_float_shares':10**4,'mkt_cap_ard':10**4,'total_shares':10**4,'volume':10**2}
        super(MD, self).__init__(start_date=start_date, end_date=end_date, dtype=DType.STOCK,
                dfreq=DFreq.DAILY, dsource=DSource.WIND, mkttype=MktType.CHINA, ftype=FType.MD, factor_list=md_list,
                factor_scale=factor_scale)


class FDD_qtr(QuarterlyFactor):
    def __init__(self, start_date, end_date):
        csv_path = config_reader.getConfig('root_path', 'csv_path')
        # caution
        factor_table = pd.read_excel('find_indicators.xlsx',header=0)
        factor_name_dict = {}
        for factor_type in factor_table:
            factor_name_dict[factor_type] = factor_table[factor_type].dropna().values.tolist()
        super(FDD_qtr, self).__init__(start_date=start_date, end_date=end_date, dtype=DType.STOCK, dfreq=DFreq.QUARTERLY,
            dsource=DSource.WIND, mkttype=MktType.CHINA, ftype=FType.FDD, factor_list=factor_name_dict)

class FDD_daily(DailyFactor):
    def __init__(self, start_date, end_date):
        fdd_list = ['dividendyield2','pe_ttm','pb_lf']
        super(FDD_daily, self).__init__(start_date=start_date, end_date=end_date, dtype=DType.STOCK, dfreq=DFreq.DAILY,
            dsource=DSource.WIND, mkttype=MktType.CHINA, ftype=FType.FDD, factor_list=fdd_list)

class FDD:
    def __init__(self, start_date, end_date):
        self.sdate = start_date
        self.edate = end_date

    def cronb(self):
        update_fdd_qtr = FDD_qtr(self.sdate, self.edate)
        update_fdd_qtr.cronb()
        update_fdd_daily = FDD_daily(self.sdate, self.edate)
        update_fdd_daily.cronb()


class INDUSTRY(DailyFactor):
    def __init__(self, start_date, end_date):
        super(INDUSTRY, self).__init__(start_date=start_date, end_date=end_date, dtype=DType.STOCK, dfreq=DFreq.DAILY,
            dsource=DSource.WIND, mkttype=MktType.CHINA, ftype=FType.INDUSTRY, factor_list=['industry_citiccode'])

    def retriever(self, checker=None):
        industry_code = ['b101000000000000','b102000000000000','b103000000000000','b104000000000000','b105000000000000',
                            'b106000000000000', 'b107000000000000', 'b108000000000000', 'b109000000000000','b10a000000000000',
                            'b10b000000000000', 'b10c000000000000', 'b10d000000000000', 'b10e000000000000', 'b10f000000000000',
                             'b10g000000000000', 'b10h000000000000','b10i000000000000', 'b10j000000000000', 'b10k000000000000',
                             'b10l000000000000', 'b10n000000000000', 'b10o000000000000', 'b10p000000000000', 'b10q000000000000',
                             'b10r000000000000','b10s000000000000', 'b10t000000000000', 'b10m010000000000', 'b10m020000000000',
                              'b10m030000000000']
        industry_num = [i+1 for i in range(len(industry_code))]
        industry_dict = dict(zip(industry_code,industry_num))
        print(industry_dict)
        self.fail_dict_master['industry_csv']  = save_industry(self.cdate_list, self.csv_path,industry_dict,use_wind_list=True)


if __name__ == '__main__':
    # get_wind_secu_status()
    sdate = 20180630
    edate = 20180710
    sdate,edate,cdate_list = check_update_date(sdate=sdate,edate=edate)

    for _type in [FDD, INDEX, MD, INDUSTRY]:
    # for _type in [INDUSTRY]:
        _type(sdate, edate).cronb()
