import pandas as pd
import pickle
import datetime
from QuantFramework import HDFSFileHandler
from xquant.xqutils.xqfile import HDFSFile
from xquant.pyfile import Pyfile
from multifactor.IO import IO
from multifactor.data.utils import *
import os
import datetime as dt 
import pickle
import zipfile
from xquant.xqutils.xqfile import FTPFile
ftp = FTPFile()

def get_sub_df(table,mode,freq):
    print('*'*50)
    print(table,mode,freq)
    prod_path = '/data/group/800080/warehouse/prod/DATABASE/WIND/' + table + '/' + table + '.h5'
    
    if mode == 'increment':
        if freq == 'daily':
            sdate,edate,cdate_list = check_update_date()
            df_prod = IO.read_data([sdate,edate],alt=prod_path)
        if freq == 'quartly':
            df_prod = IO.read_data([20180601,20250101],alt=prod_path)
    if mode == 'overwrite':
        df_prod = IO.read_data([20000101,20250101],alt=prod_path)

    return df_prod
    

def main():
    # date = str(time.strftime("%Y%m%d"))
    xdate, date, _ = check_update_date()
    date = str(date)
    print(date)
    root = '/data/user/015626/slice_data/slice_data_wind/'
    slice_path = root + date + '/'
    if not os.path.exists(slice_path):
        os.makedirs(slice_path)
    
    qtr_list = ['WIND_AShareBalanceSheet','WIND_AShareCashFlow','WIND_AShareIncome','WIND_AShareProfitExpress',
                    'WIND_AShareProfitNotice','WIND_AShareFinancialIndicator','WIND_AShareTTMHis', 'WIND_AShareAFIndicator', 
                    'WIND_AShareIssuingDatePredict','WIND_AShareDividend','WIND_AIndexFinancialderivative']

    first_daily_list = ['WIND_AShareDescription','WIND_AShareIndClassCITICS', 'WIND_AShareManagement',
                        'WIND_AShareMonRepBrokers','WIND_Ashareeoddindicator','WIND_AShareEODPrices','WIND_AIndexEODPrices',
                        'WIND_AShareMgHoldReward','WIND_AShareMoneyFlow','WIND_AShareL2Indicators','WIND_AIndexMembers','WIND_AShareConseption','WIND_AShareST']
                        
    name_mapping_dict = {'WIND_AShareAFIndicator': 'AShareANNFinancialIndicator', 'WIND_Ashareeoddindicator': 'AShareEODDerivativeIndicator',
                    'WIND_ASharePledgepro':  'ASharePledgeproportion','WIND_AShareFFCalendar': 'AShareFreeFloatCalendar',
                    'WIND_CMFundAssetPortfolio': 'ChinaMutualFundAssetPortfolio','WIND_CMFundIndPortfolio': 'ChinaMutualFundIndPortfolio',
                    'WIND_CMFundStockPortfolio': 'ChinaMutualFundStockPortfolio', 'WIND_CMFundBondPortfolio': 'ChinaMutualFundBondPortfolio',
                    'WIND_AShareIndClassCITICS': 'AShareIndustriesClassCITICS', 'WIND_AShareMgHoldReward': 'AShareManagementHoldReward', 
                    'WIND_AShareEXRightDivRecord': 'AShareEXRightDividendRecord', 'WIND_AShareswingRevADJ':'AShareswingReversetrendADJ',
                    'WIND_AShareMonRepBrokers' : 'AShareMonthlyReportsofBrokers', 'WIND_AShareFinExpense': 'AShareFinancialExpense',
                    'WIND_AshareOthreceivables': 'AshareOtherreceivables', 'WIND_Top5ByAccReceivable': 'Top5ByAccountsReceivable',
                    'WIND_AshareFinaccounts': 'AshareFinancialaccounts'}
    
    overwrite_list = ['WIND_AShareIndClassCITICS', 'WIND_AShareDescription', 'WIND_AShareIndustriesCode','WIND_AShareST',
                        'WIND_AShareCapitalization', 'WIND_AShareFreeFloat', 'WIND_AShareIPO', 'WIND_AShareAgency',
                         'WIND_AShareCOCapitaloperation', 'WIND_ASharePledgepro', 'WIND_AshareStockRepo', 'WIND_AShareCorporateFinance',
                         'WIND_AShareIssueCommAudit', 'WIND_AShareEquityDivision', 'WIND_AShareStaff',
                         'WIND_IPOCompRFA', 'WIND_IECMemberList', 'WIND_AShareLeadUnderwriter',
                         'WIND_AShareRightIssue', 'WIND_AShareSEO', 'WIND_IPOInquiryDetails',
                         'WIND_AShareManagement', 'WIND_AShareIncDescription', 'WIND_AShareIncQuantityPrice', 'WIND_AShareIncQuantityDetails',
                         'WIND_AShareIncExercisePct', 'WIND_AShareIncExecQtyPri', 'WIND_AShareEsopDescription', 'WIND_AShareEsopTradingInfo',
                         'WIND_AShareStaffStructure', 'WIND_AShareMajorHolderPlanHold','WIND_AShareTypeCode','WIND_htzqedbdzzbs',
                         'WIND_AShareMainandnoteitems','WIND_AIndexMembers','WIND_AShareConseption']
    
    
    for table in first_daily_list:
        mode = 'increment' 
        if table in overwrite_list:
            mode = 'overwrite' 
        if table in name_mapping_dict.keys():
            table = name_mapping_dict[table]
        else:
            table = table[5:]
        df_sub = get_sub_df(table,mode,'daily')
        df_sub.to_pickle(slice_path  + table + '.pkl')
    
       
    for table in qtr_list:
        if table in name_mapping_dict.keys():
            table = name_mapping_dict[table]
        else:
            table = table[5:]
        mode = 'increment' 
        df_sub = get_sub_df(table,mode,'quartly')
        df_sub.to_pickle(slice_path + table + '.pkl')
    
    upload_path = root + 'data_upload/'
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    
    with zipfile.ZipFile(upload_path + date + '_sliced_data.zip','w') as z: 
        for i in os.listdir(slice_path):
            z.write(slice_path + i,i)    
    
    
    ftp.uploadFile(upload_path + date + '_sliced_data.zip', '/015626/check_data/wind/'+ date + '_sliced_data.zip')
    
    print('finish!')
    

if __name__=='__main__':
    main()
    