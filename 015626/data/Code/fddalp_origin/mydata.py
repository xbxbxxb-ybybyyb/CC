from IO import IO,IO_enums
from utility import dt
import pandas as pd
import os
from utility import backfill
import numpy as np

class Mydata:
    def __init__(self, stDate,edDate):
        self.stDate = stDate
        self.edDate = edDate
        self.rootPath = 'W:/zhangf/data'
        self.rootPath1 = 'Z:/warehouse/prod'
        self.rootPath2 = 'S:/Quant/data'


    def getdata(self):
        self.getmddata()
        self.getfdddata(append = True)
        #self.getfcddata()
        self.getunivdata()
        #self.getriskdata()
        #self.getsecuMaindata()
        #self.getindustrydata()
        #self.getcalendardata()
        self.get_modified_size()
    
    def getmddata(self):
        data = IO.read_data([self.stDate, self.edDate], alt = os.path.join(self.rootPath1, 'MD','CHINA_STOCK','DAILY','WIND','MD_CHINA_STOCK_DAILY_WIND.h5'))
        resultPath = os.path.join(self.rootPath,'md','CHINA_STOCK','DAILY','WIND')
        if not os.path.exists(resultPath):
            os.makedirs(resultPath)
        
        resultName = os.path.join(resultPath,'MD_CHINA_STOCK_DAILY_WIND.h5')
        if os.path.exists(resultName):
            append = True
        else:
            append = None
        
        IO.pd_hdf5_writer(data, resultName, 'MD_CHINA_STOCK_DAILY_WIND', append = append)
        
        data1 = IO.read_data([self.stDate, self.edDate], alt = os.path.join(self.rootPath1, 'MD','CHINA_INDEX','DAILY','WIND','MD_CHINA_INDEX_DAILY_WIND.h5'))
        resultPath1 = os.path.join(self.rootPath,'md','CHINA_INDEX','DAILY','WIND')
        if not os.path.exists(resultPath1):
            os.makedirs(resultPath1)
        
        resultName1 = os.path.join(resultPath1,'MD_CHINA_INDEX_DAILY_WIND.h5')
        if os.path.exists(resultName1):
            append = True
        else:
            append = None
        
        IO.pd_hdf5_writer(data1, resultName1, 'MD_CHINA_INDEX_DAILY_WIND', append = append)
        return self
    
    def getfdddata(self, append = None):
        # some backfills here
        vars1 = ['grossmargin_ttm2','operatecashflow_ttm2']
        othervars = ['pe_ttm','pb_lf']
        
        vars2 = ['yoyroe','yoyprofit','yoyop','yoyocfps','yoyocf','yoynetprofit','yoyeps_basic','yoydebt','yoy_tr','qfa_yoysales','qfa_yoyprofit','qfa_yoyop','qfa_yoygr']
        vars3 = ['roic','roe_ttm2','roe_basic','roa2_ttm2','qfa_roe','qfa_roa','qfa_profittogr','qfa_operateincome','qfa_grossmargin','profit_ttm2','optogr','grossprofitmargin_ttm2']
        backfillvars = vars1+vars2+vars3
        prep_data = backfill.get_backfill_prep(self.stDate, self.edDate)
        stfdate = dt.get_financial_date(self.stDate,3)        
        edfdate = dt.get_financial_date(self.edDate,0)
        
        resultPath = os.path.join(self.rootPath,'fdd','CHINA_STOCK','DAILY','WIND')
        if not os.path.exists(resultPath):
            os.makedirs(resultPath)
        resultName = os.path.join(resultPath, 'FDD_CHINA_STOCK_DAILY_WIND.h5')
        data = IO.read_data([stfdate,edfdate],columns = backfillvars, ftype=IO_enums.FType.FDD,dfreq=IO_enums.DFreq.QUARTERLY)
        print('backfill vars!')
        data_backfilled = backfill.backfill_master(data, self.stDate, self.edDate, prep_data)
        data_backfilled = data_backfilled[IO.str_date_parser(self.stDate):IO.str_date_parser(self.edDate)]
        datadaily = IO.read_data([self.stDate,self.edDate],columns = othervars, ftype=IO_enums.FType.FDD)
        if data_backfilled.shape[0] < 100:
            raise('something wrong with backfill')
        data = pd.concat([data_backfilled,datadaily],axis = 1)
        IO.pd_hdf5_writer(data, resultName, 'dailyvars', append = append)
        return self
    
    
    def getfcddata(self):
        data = IO.read_data([self.stDate, self.edDate], alt = os.path.join(self.rootPath1, 'FCD','CHINA_STOCK','DAILY','SUNTIME','FCD_CHINA_STOCK_DAILY_SUNTIME.h5'))
        resultPath = os.path.join(self.rootPath,'fcd','CHINA_STOCK','DAILY','SUNTIME')
        if not os.path.exists(resultPath):
            os.makedirs(resultPath)
        
        resultName = os.path.join(resultPath,'FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
        if os.path.exists(resultName):
            append = True
        else:
            append = None
        
        IO.pd_hdf5_writer(data, resultName, 'FCD_CHINA_STOCK_DAILY_SUNTIME', append = append)
        return self
        
    def getunivdata(self):
        data = IO.read_data([self.stDate, self.edDate], alt = os.path.join(self.rootPath1, 'UNIV','CHINA_STOCK','DAILY','OPTM','UNIV_CHINA_STOCK_DAILY_OPTM.h5'))
        resultPath = os.path.join(self.rootPath,'univ','CHINA_STOCK','DAILY','OPTM')
        if not os.path.exists(resultPath):
            os.makedirs(resultPath)
        
        resultName = os.path.join(resultPath,'UNIV_CHINA_STOCK_DAILY_OPTM.h5')
        if os.path.exists(resultName):
            append = True
        else:
            append = None
        
        IO.pd_hdf5_writer(data, resultName, 'UNIV_CHINA_STOCK_DAILY_OPTM', append = append)
        return self
    
    def getriskdata(self):
        data = IO.read_data([self.stDate, self.edDate], columns=['Size','Industry'],
                            alt = os.path.join(self.rootPath1, 'RISK','CHINA_STOCK','DAILY','STYLEFACTOR',
                                               'risk_CHINA_STOCK_DAILY_STYLEFACTOR.h5'))
        import pdb;pdb.set_trace()
        resultPath = os.path.join(self.rootPath,'risk','CHINA_STOCK','DAILY','STYLEFACTOR')
        if not os.path.exists(resultPath):
            os.makedirs(resultPath)
        
        resultName = os.path.join(resultPath,'RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5')
        if os.path.exists(resultName):
            append = True
        else:
            append = None
        
        IO.pd_hdf5_writer(data, resultName, 'RISK_CHINA_STOCK_DAILY_STYLEFACTOR', append = append)
        return self
    
    def getsecuMaindata(self):
        data = pd.read_hdf(os.path.join(self.rootPath1, 'secuMain', 'secuMain_CHINA_STOCK_WIND.h5'))
        resultPath = os.path.join(self.rootPath, 'secuMain')
        if not os.path.exists(resultPath):
            os.makedirs(resultPath)
        
        resultName = os.path.join(resultPath, 'secuMain_CHINA_STOCK_WIND.h5')
        data.to_hdf(resultName,key='secuMain')
        return self
    
    def getindustrydata(self):
        data = IO.read_data([self.stDate, self.edDate], alt = os.path.join(self.rootPath1, 'INDUSTRY','CHINA_STOCK','DAILY','WIND','INDUSTRY_CHINA_STOCK_DAILY_WIND.h5'))
        resultPath = os.path.join(self.rootPath,'industry','CHINA_STOCK','DAILY','WIND')
        if not os.path.exists(resultPath):
            os.makedirs(resultPath)
        
        resultName = os.path.join(resultPath,'INDUSTRY_CHINA_STOCK_DAILY_WIND.h5')
        if os.path.exists(resultName):
            append = True
        else:
            append = None
        
        IO.pd_hdf5_writer(data, resultName, 'INDUSTRY_CHINA_STOCK_DAILY_WIND', append = append)
        return self
    
    def getcalendardata(self):
        dailydata = pd.read_hdf(os.path.join(self.rootPath1, 'CALENDAR', 'CHINA_STOCK','DAILY','HTSC','CALENDAR_CHINA_STOCK_DAILY_HTSC.h5'))
        weeklydata = pd.read_hdf(os.path.join(self.rootPath1, 'CALENDAR', 'CHINA_STOCK','WEEKLY','HTSC','CALENDAR_CHINA_STOCK_WEEKLY_HTSC.h5'))
        monthlydata = pd.read_hdf(os.path.join(self.rootPath1, 'CALENDAR', 'CHINA_STOCK', 'MONTHLY', 'HTSC', 'CALENDAR_CHINA_STOCK_MONTHLY_HTSC.h5'))
        yearlydata = pd.read_hdf(os.path.join(self.rootPath1, 'CALENDAR','CHINA_STOCK','YEARLY','HTSC','CALENDAR_CHINA_STOCK_YEARLY_HTSC.h5'))
        
        resultPath1 = os.path.join(self.rootPath, 'calendar', 'CHINA_STOCK', 'DAILY','HTSC')
        if not os.path.exists(resultPath1):
            os.makedirs(resultPath1)
        resultName1 = os.path.join(resultPath1,'CALENDAR_CHINA_STOCK_DAILY_HTSC.h5')
        dailydata.to_hdf(resultName1, key = 'daily')
        
        resultPath2 = os.path.join(self.rootPath, 'calendar', 'CHINA_STOCK', 'WEEKLY','HTSC')
        if not os.path.exists(resultPath2):
            os.makedirs(resultPath2)
        resultName2 = os.path.join(resultPath2,'CALENDAR_CHINA_STOCK_WEEKLY_HTSC.h5')
        weeklydata.to_hdf(resultName2, key = 'weekly')
        
        resultPath3 = os.path.join(self.rootPath, 'calendar', 'CHINA_STOCK', 'MONTHLY','HTSC')
        if not os.path.exists(resultPath3):
            os.makedirs(resultPath3)
        resultName3 = os.path.join(resultPath3,'CALENDAR_CHINA_STOCK_MONTHLY_HTSC.h5')
        monthlydata.to_hdf(resultName3, key = 'monthly')
        
        resultPath4 = os.path.join(self.rootPath, 'calendar', 'CHINA_STOCK', 'YEARLY','HTSC')
        if not os.path.exists(resultPath4):
            os.makedirs(resultPath4)
        resultName4 = os.path.join(resultPath4,'CALENDAR_CHINA_STOCK_YEARLY_HTSC.h5')
        yearlydata.to_hdf(resultName4, key = 'yearly')
        return self

    def get_modified_size(self, result_path = r'W:\zhangf\data\risk\CHINA_STOCK\DAILY\STYLEFACTOR'):
        index_wt=IO.read_data([self.stDate,self.edDate],ftype=IO_enums.FType.INDEXWEIGHT,dsource=IO_enums.DSource.CSI)
        mkt_cap = IO.read_data([self.stDate,self.edDate], columns=['mkt_cap_ard'])
        size2 = np.sqrt(mkt_cap) #size2 and size300
        size3 = mkt_cap **(1/3) #size3
        #size4 = 1-mkt_cap **(-1)*1e4
        skewed_cap = mkt_cap**(0.4)
        size2.columns = ['Size2']
        size3.columns = ['Size3']
        skewed_cap.columns=['skewed_cap']
        data = pd.concat([index_wt, size2, size3, skewed_cap],axis=1).dropna(how='all')
        zz500size2 = (data['index_weight_zz500']*data['Size2']).groupby('dt').sum()
        size2 = data['Size2'].subtract(zz500size2).divide(zz500size2)
        size2[size2 > 3] = 3
        size2[size2<-3] = -3
        size2 = pd.DataFrame(size2, columns=['Size2'])

        zz500size3 = (data['index_weight_zz500']*data['Size3']).groupby('dt').sum()
        size3 = data['Size3'].subtract(zz500size3).divide(zz500size3)
        size3[size3 > 3] = 3
        size3[size3 < -3] = -3
        size3 = pd.DataFrame(size3, columns=['Size3'])

        zz500skewedcap = (data['index_weight_zz500']*data['skewed_cap']).groupby('dt').sum()
        skewed_cap = data['skewed_cap'].subtract(zz500skewedcap).divide(zz500skewedcap)
        skewed_cap[skewed_cap > 3] = 3
        skewed_cap[skewed_cap<-3] = -3
        skewed_cap = pd.DataFrame(skewed_cap, columns=['skewed_cap'])

        modified_size = pd.concat([size2, size3, skewed_cap],axis=1)
        if not os.path.exists(result_path):
            os.makedirs(result_path)
        result_name = os.path.join(result_path, 'modified_size.h5')
        if os.path.exists(result_name):
            append = True
        else:
            append = None
        IO.pd_hdf5_writer(modified_size, result_name,'modified_size',append=append)