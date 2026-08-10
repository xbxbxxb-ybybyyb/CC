import pandas as pd
import pickle
import datetime
from QuantFramework import HDFSFileHandler
from xquant.xqutils.xqfile import HDFSFile
from xquant.pyfile import Pyfile
from multifactor.IO import IO
import os

def check_data(path,mode):
    print('*'*50)
    print(path,mode)
    prod_path = '/data/group/800080/warehouse/prod/DATABASE/WIND/' + path + '/' + path + '.h5'
    test_path = '/data/group/800080/warehouse/insample/DATABASE/WIND/' + path + '/' + path + '.h5'
    
    # mode = 'overwrite'
    try:
        df_test = IO.read_data([20130101,20160101],alt=test_path)
        # df_test = IO.read_data([20190801,20190901],alt=test_path)
    except Exception as e:
        print(e)
        return pd.DataFrame(columns = ['table','column','error_rate'])
        
    df_test.reset_index('Ticker',inplace=True)
    date_list = list(set(df_test.index))
    date_list.sort()
    date_list = [int(str(i)[:10].replace('-','')) for i in date_list] #get time
    
    if mode == 'increment':
        df_prod = IO.read_data([date_list[0],date_list[-1]],alt=prod_path)
    if mode == 'overwrite':
        df_prod = IO.read_data([20000101,20200101],alt=prod_path)
     
    df_prod.reset_index(inplace=True)
    df_prod.set_index(['dt','Ticker','OBJECT_ID'],inplace=True)
    
    df_test.reset_index('dt',inplace=True)
    df_test.set_index(['dt','Ticker','OBJECT_ID'],inplace=True)
    column_list = list(set(df_test.columns)) 
    # print(column_list)
    print(len(column_list))
    # print(list(set(df_test.head(3).index)))
    
    if(len(column_list) > 50): #split columns 
        gap = 50
        time = len(column_list) // gap
        df = pd.DataFrame(columns = ['table','column','error_rate'])
        for i in range(time+1):  
            start = i*gap
            if(i != time):
                col = column_list[start:start+gap]
            else:
                col = column_list[start:] 
            # print(col)
            df_sub = join_data_check(path,col,df_prod,df_test)       
            df = df.append(df_sub)
    else:
        df = join_data_check(path,column_list,df_prod,df_test)
        
    df.index = range(len(df))  
         
    # print(df)
    return df
    
def join_data_check(path,col,df_prod,df_test):
    
    if 'OPDATE' not in col:
        col.append('OPDATE')
    if 'OPMODE' not in col:
        col.append('OPMODE')
    
    df_join = pd.merge(df_test[col],df_prod[col],how='left',left_index=True,right_index=True)   
    df_join.fillna('NAN',inplace=True)
    df_join['OPDATE_y'] = df_join['OPDATE_y'].apply(lambda x:float(str(x).replace('-','').replace('/','').replace(' ','').replace(':','')))
    df_join['OPDATE_x'] = df_join['OPDATE_x'].apply(lambda x:float(str(x).replace('-','').replace('/','').replace(' ','').replace(':','')))
    
    
    df_dict = {'table':[],'column':[],'error_rate':[]}
    outpath ='/data/user/015626/check_data/DATABASE/WIND/' + path + '/'
    if not os.path.exists(outpath):
        os.makedirs(outpath) 
    
    def helper(x,column):
        if x[column+'_y'] == 'NAN' and x['OPDATE_y'] == 'NAN':
            return 1
        return 0   
         
    for column in col:
        df_error = df_join[df_join[column+'_x'] != df_join[column+'_y']]
        df_error = df_error[[column+'_x',column+'_y','OPDATE_x','OPDATE_y','OPMODE_x','OPMODE_y']]
        if(len(df_error) != 0):
            # print(df_error)
            if(column != 'OPDATE' and column != 'OPMODE'):
                df_error['sig'] = df_error.apply(lambda x:helper(x,column),axis=1)
                df_error = df_error[df_error.sig == 0]
            if(len(df_error) != 0):
                print('wrong: ',column)
                # print(df_error)
                df_error.to_csv(outpath + column + '.csv', encoding='utf_8_sig')
        error_rate = len(df_error)/len(df_join)
        df_dict['table'].append(path)
        df_dict['column'].append(column)
        df_dict['error_rate'].append(error_rate)
    df = pd.DataFrame.from_dict(df_dict,orient='columns')
    print(df)
    return df
    
def main():
    df_all = pd.DataFrame(columns = ['table','column','error_rate'])
    # data_path_list=['DATABASE/WIND/AShareBalanceSheet/AShareBalanceSheet.h5']
    
    path_list = os.listdir('/data/group/800080/warehouse/insample/DATABASE/WIND/')
    alist = os.listdir('/data/user/015626/check_data/DATABASE/WIND/')
    path_list = list(set(path_list) - set(alist))
    
    overwrite_list = ['WIND_AShareIndustriesClassCITICS', 'WIND_AShareDescription', 'WIND_AShareIndustriesCode','WIND_AShareST',
                        'WIND_AShareCapitalization', 'WIND_AShareFreeFloat', 'WIND_AShareIPO', 'WIND_AShareAgency',
                         'WIND_AShareCOCapitaloperation', 'WIND_ASharePledgeproportion', 'WIND_AshareStockRepo', 'WIND_AShareCorporateFinance',
                         'WIND_AShareIssueCommAudit', 'WIND_AShareEquityDivision', 'WIND_AShareStaff',
                         'WIND_IPOCompRFA', 'WIND_IECMemberList', 'WIND_AShareLeadUnderwriter',
                         'WIND_AShareRightIssue', 'WIND_AShareSEO', 'WIND_IPOInquiryDetails',
                         'WIND_AShareManagement', 'WIND_AShareIncDescription', 'WIND_AShareIncQuantityPrice', 'WIND_AShareIncQuantityDetails',
                         'WIND_AShareIncExercisePct', 'WIND_AShareIncExecQtyPri', 'WIND_AShareEsopDescription', 'WIND_AShareEsopTradingInfo',
                         'WIND_AShareStaffStructure', 'WIND_AShareMajorHolderPlanHold','WIND_AShareTypeCode','WIND_htzqedbdzzbs',
                         'WIND_AShareMainandnoteitems','WIND_AIndexMembers','WIND_AShareConseption']  
    
    path_list = ['AShareMoneyFlow','AShareConsensusData','AshareintensitytrendADJ','AIndexValuation','AShareEnergyindexADJ',
            'AShareEODDerivativeIndicator']
       
    for path in path_list:
        if path in ['APIQUARTERLY','AShareConsensusRollingData']:
            continue
        mode = 'increment' 
        if 'WIND_' + path not in overwrite_list:
            df = check_data(path,mode)
            df_all = df_all.append(df)
        else:
            mode = 'overwrite'    # mode = increment,overwrite
            if not os.path.exists('/data/group/800080/warehouse/insample/DATABASE/WIND/' + path +'/' + path + '.h5'):
                os.makedirs('/data/user/015626/check_data/DATABASE/' + path)
            else:
                continue
    df_all.index = range(len(df_all))
    print(df_all)
    df_all.to_csv('/data/user/015626/check_data/DATABASE/WIND/check_result.csv', encoding='utf_8_sig')
    print('finish!')
    
if __name__=='__main__':
    # pd.set_option('display.max_columns', None)
    pd.set_option('display.width',None)
    main()