from IO import IO
from IO.IO_enums import *
import utility.dt as tdt
import pandas as pd
import datetime as dt
import numpy as np
from functools import lru_cache

@lru_cache()
def round_to_trading_date(x):
    if pd.isna(x):
        return x
    else:
        try:
            return get_trading_day_offset(x, 0)[0]
        except:
            return x

def get_qtr_list(sdate,edate,num_qtr=None):
    if isinstance(sdate,pd.Timestamp):
        sdate = int(dt.datetime.strftime(sdate,'%Y%m%d'))
    if isinstance(edate,pd.Timestamp):
        edate = int(dt.datetime.strftime(edate,'%Y%m%d'))
    if not isinstance(sdate,int):
        raise Exception
    year_list = [str(i) for i in range(2000,2050)]
    month_date = ['0331','0630','0930','1231']
    date_list_complete = [int(i+j) for i in year_list for j in month_date]
    qtr_list = [i for i in date_list_complete if i<=edate and i>=sdate]
    if len(qtr_list)==0:
        qtr_list = [i for i in date_list_complete if i<=edate][-1:]
    if num_qtr is not None:
        if isinstance(num_qtr,int):
            start_idx = date_list_complete.index(qtr_list[0])
            pre_qtr = date_list_complete[start_idx-num_qtr:start_idx]
            qtr_list = pre_qtr + qtr_list
            qtr_list.sort()
        else:
            print ('input error: num_qtr not integer')
            raise Exception
    return qtr_list

def issuing_date_checker(issuing_date_ps):
    # remove issuing dates not in the ascending order
    # eg: annual report later than 1st quarter report, remove annual report issuing date
    # caution: DataFrame & timedelta comparison is buggy
    lookup_dict = {3: pd.Timestamp(1900, 4, 30) - pd.Timestamp(1900, 3, 31),
                   6: pd.Timestamp(1900, 8, 31) - pd.Timestamp(1900, 6, 30),
                   9: pd.Timestamp(1900, 10, 31) - pd.Timestamp(1900, 9, 30),
                   12: pd.Timestamp(1901, 4, 30) - pd.Timestamp(1900, 12, 31)}
    if not isinstance(issuing_date_ps.iloc[0], pd.Timestamp):
        issuing_date_ps = pd.to_datetime(issuing_date_ps)
    data = issuing_date_ps.unstack()
    report_dead_line = pd.DataFrame(data.index, index=data.index)
    report_dead_line['dead_line'] = [i+lookup_dict[i.month] for i in report_dead_line['dt']]
    # check for non-ascending issuing date
    _days = (data - data.shift(-1)).apply(lambda x: x.dt.days)
    _mask_1 =  (_days > 0) & (_days < 1000)
    # check for issuing date later than dead line
    _mask_2 = (data.subtract(report_dead_line['dead_line'], axis=0)).apply(lambda x: x.dt.days) >= 30
    # check for wrong issuing date
    _mask_3 = (data.subtract(report_dead_line['dt'], axis=0)).apply(lambda x: x.dt.days) <= -1
    _mask = _mask_1 | _mask_2 | _mask_3
    data[_mask] = np.nan
    return data.stack()

def create_listing_delisting_filter(start_date,  end_date, merged_mask=True,
                                    h5_path=r'Z:\warehouse\prod\ETC\CHINA_STOCK\WIND\STOCK_LISTING_DELISTING_DATE.h5'):
    
    start_date = IO.str_date_parser(start_date)
    end_date = IO.str_date_parser(end_date)
    full_day_range = pd.date_range(start=start_date, end=end_date, freq='1D')
    trading_dates = tdt.get_trading_date_range(start_date, end_date)
    list_delist_data = pd.read_hdf(h5_path)
    list_date = list_delist_data.ipo_date
    delist_date = list_delist_data.delist_date

    #with pd.HDFStore(h5_path) as hdf_store:
    #    delist_date = hdf_store.SecDate.delist_date
    #    list_date = hdf_store.SecDate.ipo_date
    # process delisting date filter
    delist_date = delist_date.reset_index()
    delist_date['Filter'] = True
    delist_date_pd = delist_date.set_index(['delist_date', 'Ticker'])['Filter'].unstack().reindex(index=full_day_range)
    delist_date_pd = delist_date_pd.fillna(method='ffill')
    delist_date_pd = delist_date_pd.reindex(index=trading_dates)
    delist_date_pd = delist_date_pd.fillna(False).astype('bool')
    # process listing date filter
    list_date = list_date.reset_index()
    list_date['Filter'] = True
    list_date_pd = list_date.set_index(['ipo_date', 'Ticker'])['Filter'].unstack().reindex(index=full_day_range)
    list_date_pd = list_date_pd.fillna(method='bfill')
    list_date_pd = list_date_pd.reindex(index=trading_dates)
    list_date_pd = list_date_pd.fillna(False).astype('bool')
    if merged_mask:
        return delist_date_pd | list_date_pd
    else:
        return delist_date_pd, list_date_pd

# fdd factor must be update at the end of the week

def backfill(start_date, end_date, factor_qtr_pd, issuing_date_ps=None, trading_date_list=None,
             issue_date_reformed=False, listing_delisting_filter=None):
    assert len(factor_qtr_pd.columns) == 1
    start_date = IO.str_date_parser(start_date)
    end_date = IO.str_date_parser(end_date)
    qtr_list = get_qtr_list(start_date,end_date,num_qtr=3)
    if issuing_date_ps is None:
        issuing_date_ps = IO.read_data([qtr_list[0], qtr_list[-1]], ftype=FType.FDD, dsource=DSource.WIND,
                                        dfreq=DFreq.QUARTERLY, columns=['stm_issuingdate'])['stm_issuingdate']
        issuing_date_ps = issuing_date_checker(issuing_date_ps)
    else:
        if not issue_date_reformed:
            issuing_date_ps = issuing_date_checker(issuing_date_ps)
    issuing_date_ps = issuing_date_ps.apply(lambda x: round_to_trading_date(x))
    data = factor_qtr_pd.copy()
    data['issuing_date'] = issuing_date_ps
    data = data.reset_index().sort_values(by='dt').dropna()
    data = data.drop_duplicates(subset=['issuing_date', 'Ticker'], keep='last')
    data = data.set_index(['issuing_date', 'Ticker'])
    data = data[factor_qtr_pd.columns[0]].unstack()
    _start_date = start_date - pd.Timedelta('365d')
    full_day_range = pd.date_range(start=_start_date, end=end_date, freq='1D')
    data = data.reindex(index=full_day_range).fillna(method='ffill',limit = 210)
    if trading_date_list is None:
        data = data.reindex(index=tdt.get_trading_date_range(start_date, end_date))
    else:
        data = data.reindex(index=trading_date_list)
    if listing_delisting_filter is None:
        listing_delisting_filter = create_listing_delisting_filter(start_date, end_date)
    listing_delisting_filter = listing_delisting_filter.reindex(columns=data.columns).fillna(False).astype('bool')
    data[listing_delisting_filter] = np.nan
    res = pd.DataFrame(data.stack(), columns=factor_qtr_pd.columns)
    res.index.names = ['dt', 'Ticker']
    return res

def ticker_filter(stk_list):
    stk_list_filter = [i for i in stk_list if not i[0].isalpha()]
    return stk_list_filter


def get_backfill_prep(sdate,edate,announce_date=None):
    prep_data = {}
    qtr_list = get_qtr_list(sdate,edate,num_qtr=3)
    listing_delisting_filter = create_listing_delisting_filter(sdate,edate)
    # list(set([type(i) for i in announce_date.values[:10]]))
    if announce_date is not None:
        issuing_date_ps = announce_date
    else:
        issuing_date_ps = IO.read_data([qtr_list[0], qtr_list[-1]], ftype=FType.FDD, dsource=DSource.WIND, dfreq=DFreq.QUARTERLY, columns=['stm_issuingdate'])['stm_issuingdate']
        issuing_date_ps = issuing_date_checker(issuing_date_ps)
    trading_date_list = tdt.get_trading_date_range(sdate,edate)
    prep_data['qtr_list'], prep_data['listing_delisting_filter'] = \
    qtr_list,listing_delisting_filter
    prep_data['issuing_date_ps'], prep_data['trading_date_list'] = \
    issuing_date_ps,trading_date_list
    return prep_data


def backfill_master(fac_qtr,sdate,edate,prep_data=None):
    fac_daily_dict = {}
    fac_qtr_mi = fac_qtr.copy()
    if len(fac_qtr_mi.columns)>300:
        fac_qtr_mi = pd.DataFrame(fac_qtr_mi.stack(),columns=['anonymous'])
    fac_list = list(fac_qtr_mi.columns)
    print ('backfill qtr2daily: %s'%str(fac_list))
    if prep_data is None:
        print ('getting prep_data')
        qtr_list = get_qtr_list(sdate,edate,num_qtr=3)
        listing_delisting_filter = create_listing_delisting_filter(sdate,edate)
        issuing_date_ps = IO.read_data([qtr_list[0], qtr_list[-1]], ftype=FType.FDD, dsource=DSource.WIND, dfreq=DFreq.QUARTERLY, columns=['stm_issuingdate'])['stm_issuingdate']
        issuing_date_ps = issuing_date_checker(issuing_date_ps)
        trading_date_list = tdt.get_trading_date_range(sdate,edate)
    elif prep_data is not None:
        qtr_list,listing_delisting_filter = prep_data['qtr_list'], prep_data['listing_delisting_filter']
        issuing_date_ps,trading_date_list = prep_data['issuing_date_ps'], prep_data['trading_date_list']
        
    for fac in fac_list:
        print (fac)
        fac_daily_mi = backfill(sdate,edate,fac_qtr_mi[[fac]],issuing_date_ps,trading_date_list,True,listing_delisting_filter)
        fac_daily_dict[fac] = fac_daily_mi.unstack()[fac]
    tmplist = []
    for fac in fac_list:
        print (fac)
        fac_daily_mi = backfill(sdate,edate,fac_qtr_mi[[fac]],issuing_date_ps,trading_date_list,True,listing_delisting_filter)
        #fac_daily_dict[fac] = fac_daily_mi.unstack()[fac]
        tmplist.append(fac_daily_mi)
    data = pd.concat(tmplist,axis = 1)
    data = data[IO.str_date_parser(sdate):IO.str_date_parser(edate)]
    return data

"""
    if fac_list == ['anonymous']:
        return fac_daily_dict[fac]
    else:
        return fac_daily_dict
"""

