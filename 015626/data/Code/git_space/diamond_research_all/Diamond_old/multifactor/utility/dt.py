__author__="Software Authors: Xu Deyuan"
__copyright__="Copyright (C) 2019 HTSC"
__license__="Private"
__version__="1.0"
from multifactor.IO.IO import*
def get_trading_date_range(start_date,end_date,dfreq=DFreq.DAILY,dtype=DType.STOCK,mkttype=MktType.CHINA,dsource=DSource.HTSC,alt=None):
    pd_trading_dates=read_data([start_date,end_date],dfreq=dfreq,dtype=dtype,mkttype=mkttype,dsource=dsource,ftype=FType.CALENDAR,alt=alt)
    return pd_trading_dates.index.get_level_values('dt').tolist()
def get_trading_day_offset(start_date,offset_list,dfreq=DFreq.DAILY,dtype=DType.STOCK,mkttype=MktType.CHINA,dsource=DSource.HTSC,alt=None):
    if type(offset_list)is not list:
        offset_list=[offset_list]
    try:
        offset_list=[int(item)for item in offset_list]
    except:
        print('Illegal offsets found, aborting...')
    start_date=str_date_parser(start_date)
    if dfreq==DFreq.DAILY:
        temp_data=read_data([start_date+pd.tseries.offsets.DateOffset(days=min(int(min(offset_list)*5),-20)),start_date+pd.tseries.offsets.DateOffset(days=max(int(max(offset_list)*5),20))],dfreq=dfreq,dtype=dtype,mkttype=mkttype,dsource=dsource,ftype=FType.CALENDAR,alt=alt)
    elif dfreq==DFreq.WEEKLY:
        temp_data=read_data([start_date+pd.tseries.offsets.DateOffset(days=min(int(min(offset_list)*7-10),-20)),start_date+pd.tseries.offsets.DateOffset(days=max(int(max(offset_list)*7+10),20))],dfreq=dfreq,dtype=dtype,mkttype=mkttype,dsource=dsource,ftype=FType.CALENDAR,alt=alt)
    elif dfreq==DFreq.MONTHLY:
        temp_data=read_data([start_date+pd.tseries.offsets.DateOffset(months=min(int(min(offset_list)-2),-2)),start_date+pd.tseries.offsets.DateOffset(months=max(int(max(offset_list)+2),2))],dfreq=dfreq,dtype=dtype,mkttype=mkttype,dsource=dsource,ftype=FType.CALENDAR,alt=alt)
    elif dfreq==DFreq.YEARLY:
        temp_data=read_data([start_date+pd.tseries.offsets.DateOffset(years=min(int(min(offset_list)-2),-2)),start_date+pd.tseries.offsets.DateOffset(years=max(int(max(offset_list)+2),2))],dfreq=dfreq,dtype=dtype,mkttype=mkttype,dsource=dsource,ftype=FType.CALENDAR,alt=alt)
    else:
        raise ValueError
    start_date=temp_data.loc[:start_date].tail(1).index.get_level_values('dt')[0]
    temp_data_lst=temp_data.index.get_level_values('dt').tolist()
    sd_idx=temp_data_lst.index(start_date)
    return[temp_data_lst[sd_idx+item]for item in offset_list]
def get_financial_date(start_date,offset=0,mkttype=MktType.CHINA,dtype=DType.STOCK):
    start_date=str_date_parser(start_date)
    if mkttype==MktType.CHINA and dtype==DType.STOCK:
        if type(offset)is not int or offset<0:
            raise ValueError
        if offset==0:
            y,m,d=start_date.year,start_date.month,start_date.day
            if m*100+d>930:
                m,d=9,30
            elif m*100+d>630:
                m,d=6,30
            elif m*100+d>331:
                m,d=3,31
            else:
                y,m,d=y-1,12,31
            return pd.Timestamp(y,m,d)
        else:
            financial_date=get_financial_date(start_date,offset=0)
            for counter in range(offset):
                financial_date=financial_date-pd.Timedelta('1day')
                financial_date=get_financial_date(financial_date,offset=0)
            return financial_date
def get_financial_date_range(start_date,end_date,mkttype=MktType.CHINA,dtype=DType.STOCK):
    start_date=str_date_parser(start_date)
    end_date=str_date_parser(end_date)
    if mkttype==MktType.CHINA and dtype==DType.STOCK:
        financial_dates=list(set([get_financial_date(item)for item in pd.date_range(start_date,end_date)]))
        financial_dates.sort()
        return[item for item in financial_dates if item>=start_date]
        
        
class MinuteDataToDaily:
    """
    把分钟数据根据需要降频到日级别
    """

    def __init__(self, minute_data):
        self.minute_data = minute_data

    def get_trading_days(self):
        """
        获取原始分钟数据包含的所有交易日
        :return: np.ndarray
            原始分钟数据包含的所有交易日
        """
        trading_days = np.unique(self.minute_data.index.date)
        return trading_days

    def get_daily_minute_num(self):
        """
        获取原始分钟数据中的每个交易日有分钟bar
        :return: int
            每个交易日的分钟bar数量
        """
        daily_minute_num = int(self.minute_data.shape[0] / self.get_trading_days().shape[0])
        return daily_minute_num

    def truncated_time_index_num(self, truncated_time):
        """
        由于交易需要等原因，有时候每天的尾盘数据在开发因子时无法使用，需要把这部分数据截去
        这个函数用于确定要截断的时间位于当天的第几分钟
        :param truncated_time: str, e.x.{'14:59'}
            数据截断的时间
        :return:
        """
        daily_minute_num = self.get_daily_minute_num()
        temp_daily_data = self.minute_data.iloc[:daily_minute_num]
        truncated_time_index = pd.Timestamp(str(temp_daily_data.index[0].date()) + ' ' + truncated_time)
        truncated_time_index_num = np.where(temp_daily_data.index == truncated_time_index)[0][0]
        return truncated_time_index_num
