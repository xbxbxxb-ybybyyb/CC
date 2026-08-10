import pandas as pd
import pickle
import datetime
from QuantFramework import HDFSFileHandler
from xquant.xqutils.xqfile import HDFSFile
from xquant.pyfile import Pyfile
from multifactor.IO import IO
import os
import numpy as np
root = '/data/user/013545/error/DATABASE/SUNTIME/'
precise_list = ['A30','A90','A180','H30','H90','H180','P30','P90','P180']

def check_data(table,mode='increment',read_mode='io',import_mode='table'):
    print('*'*50)
    print(table,mode,read_mode,import_mode)
    
    if import_mode == 'table':     
        prod_path = '/data/group/800080/warehouse/prod/DATABASE/SUNTIME/' + table + '/' + table + '.h5'
        test_path = '/data/group/800080/warehouse/test/DATABASE/SUNTIME/' + table + '/' + table + '.h5'
    if import_mode == 'path':
        prod_path = '/data/group/800080/warehouse/prod/' + table
        test_path = '/data/group/800080/warehouse/test/' + table

    if read_mode == 'io':
        df_test = IO.read_data([20000101,20250101],alt=test_path)
        df_test.reset_index(inplace=True)
        df_test.set_index('dt',inplace=True)
        
        date_list = list(set(df_test.index))
        date_list.sort()
        date_list = [int(str(i)[:10].replace('-','')) for i in date_list] #get time
        column_list = list(set(df_test.columns)) 
        # print(column_list)
        
        if mode == 'increment':
            df_prod = IO.read_data([date_list[0],date_list[-1]],alt=prod_path)
        if mode == 'overwrite':
            df_prod = IO.read_data([20000101,20250101],alt=prod_path)
        
        if 'ID' in column_list:
            print('ID')
            df_test.reset_index(inplace=True)
            df_test.set_index(['dt','ID'],inplace=True)
            df_prod.reset_index(inplace=True)
            df_prod.set_index(['dt','ID'],inplace=True)
        else:        
            for col in column_list:
                if 'ID' in col:
                    print("index name change: ",col,table)
                    df_test.reset_index(inplace=True)
                    df_test.set_index(['dt',col],inplace=True)
                    df_prod.reset_index(inplace=True)
                    df_prod.set_index(['dt',col],inplace=True)
        
    if read_mode == 'hdf':
        df_test = pd.read_hdf(test_path)
        df_prod = pd.read_hdf(prod_path)
        df_test.set_index(['ID'],inplace=True)
        df_prod.set_index(['ID'],inplace=True)
            

    column_list = list(set(df_test.columns)) 
    print(len(column_list))
 
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
            df_sub = join_data_check(table,col,df_prod,df_test)       
            df = df.append(df_sub)
    else:
        df = join_data_check(table,column_list,df_prod,df_test)
        
    df.index = range(len(df))  
         
    return df
    # return 0 
    
def join_data_check(table,col,df_prod,df_test):
    col_x = []
    col_z = []
    for column in col:
        col_x.append(column + '_xquant')
        col_z.append(column + '_z')
    df_xquant = df_test[col]
    df_xquant.columns = col_x
    df_z = df_prod[col]
    df_z.columns = col_z
    df_join = pd.concat([df_xquant, df_z], axis=1)  
    df_join.fillna('NAN',inplace=True)
    
    df_dict = {'table':[],'column':[],'error_rate':[]}
    outpath =root + table + '/'
    if not os.path.exists(outpath):
        os.makedirs(outpath) 
    
    for column in col:
        if column in precise_list:
            df_join[column + '_xquant'] = df_join[column + '_xquant'].astype(float)
            df_join[column + '_z'] = df_join[column + '_z'].astype(float)
            df_join[column + '_xquant'] = df_join[column + '_xquant'].apply(lambda x:round_up(x,4))
            df_join[column + '_z'] = df_join[column + '_z'].apply(lambda x: round_up(x, 4))
        if 'DATE' in column:
            df_join[column + '_xquant'] = df_join[column + '_xquant'].apply(lambda x:float(str(x).replace('-','').replace('/','').replace(' ','').replace(':','')))
            df_join[column + '_z'] = df_join[column + '_z'].apply(lambda x:float(str(x).replace('-','').replace('/','').replace(' ','').replace(':','')))
            df_join.fillna('NAN',inplace=True)

        df_error = df_join[df_join[column + '_xquant'] != df_join[column + '_z']]
        if 'Ticker' in col:
            df_error = df_error[[column + '_xquant', column + '_z', 'Ticker_xquant', 'Ticker_z']]
        else:
            df_error = df_error[[column + '_xquant', column + '_z']]
        
        if (len(df_error) != 0):
            print('wrong: ', column)
            df_error.to_csv(outpath + column + '.csv', encoding='utf_8_sig')
            error_rate = len(df_error) / len(df_join)
            df_dict['table'].append(table)
            df_dict['column'].append(column)
            df_dict['error_rate'].append(error_rate)
    df = pd.DataFrame.from_dict(df_dict,orient='columns')
    # print(df)
    return df


                
def round_up(number,power=0):
    """
    实现精确四舍五入，包含正、负小数多种场景
    :param number: 需要四舍五入的小数
    :param power: 四舍五入位数，支持0-∞
    :return: 返回四舍五入后的结果
    """
    if(np.isnan(number)):
        return 'NAN'
    digit = 10 ** power
    num2 = float(int(number * digit))
    # 处理正数，power不为0的情况
    if number>=0 and power !=0:
        tag = number * digit - num2 + 1 / (digit * 10)
        if tag>=0.5:
            return (num2+1)/digit
        else:
            return num2/digit
    # 处理正数，power为0取整的情况
    elif  number>=0 and power==0 :
        tag = number * digit - int(number)
        if tag >= 0.5:
            return (num2 + 1) / digit
        else:
            return num2 / digit
    # 处理负数，power为0取整的情况
    elif power==0 and number<0:
        tag = number * digit - int(number)
        if tag <= -0.5:
            return (num2 - 1) / digit
        else:
            return num2 / digit
    # 处理负数，power不为0的情况
    else:
        tag = number * digit - num2 - 1 / (digit * 10)
        if tag <= -0.5:
            return (num2-1)/digit
        else:
            return num2/digit



def main():
    df_all = pd.DataFrame(columns = ['table','column','error_rate'])
    
    table_list = os.listdir('/data/group/800080/warehouse/test/DATABASE/SUNTIME/')
    print(table_list)
    table_list = ['t_author_honor']
    overwrite_list = ['researcher_info', 'author_core', 'author_core_type', 'i_report_type', 't_author_honor',
                    'i_organ_score', 'gg_org_list', 't_great_author', 'author_pjhb'] 
    hdf_list = ['researcher_info']
    
    for table in table_list:
        mode = 'increment' 
        read_mode = 'io'
        if table in overwrite_list:
            mode = 'overwrite'    # mode = increment,overwrite
        if table in hdf_list:
            read_mode = 'hdf'
        df = check_data(table,mode,read_mode,'table')
        df_all = df_all.append(df)
    
    # suntime_path = 'FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5'
    # df = check_data(suntime_path,'increment','io','path')
    # df_all = df_all.append(df)
    
    # df_all.index = range(len(df_all))
    # print(df_all)
    # df_all.to_csv(root + 'check_result.csv', encoding='utf_8_sig')
    print('finish!')
    

if __name__=='__main__':
    # pd.set_option('display.max_columns', None)
    pd.set_option('display.width',None)
    main()