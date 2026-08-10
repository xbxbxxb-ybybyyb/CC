# -*- coding: utf-8 -*-
"""
Created on Wed May 16 13:45:23 2018

@author: 013160
"""
import pandas as pd
import numpy as np
import subprocess

def fall_back_all():
    matlab_path = '\"D:\\013160\\matlab\\MATLAB_Production_Server\\R2015a\\bin\\matlab.exe"'
    matlab_code_path = 'D:\\013160\\data\\data\\'
    matlab_function = 'run_sql'
    factor_table = pd.read_excel('documents\\mapping.xlsx',header=0)
    col_names = factor_table.columns.tolist()
    row_len = factor_table.shape[0]
    for i in range(row_len):    
        table_name = factor_table.loc[i][col_names[1]]
        factor_name = factor_table.loc[i][col_names[2]]
        if pd.isnull(table_name) or pd.isnull(factor_name):
            print(factor_table.loc[i][col_names[0]])
            print('No backup')
            continue
        print(table_name, factor_name)
        arguments = "( '20170630', "+ "'" + table_name +"'," + "'" + factor_name + "')"
        run_matlab = matlab_path + " -nodesktop -nosplash -r -wait \""+matlab_function + arguments +"\""+";quit;"
        print(run_matlab)
        subprocess.call(run_matlab,cwd=matlab_code_path)

def fall_back(factor, date):
    # factor = 'roe_basic'
    # date = 20170630
    matlab_path = '\"D:\\013160\\matlab\\MATLAB_Production_Server\\R2015a\\bin\\matlab.exe"'
    matlab_code_path = 'D:\\013160\\data\\data\\'
    matlab_function = 'run_sql'
    factor_table = pd.read_excel('documents\\mapping.xlsx',header=0)
    col_names = factor_table.columns.tolist()
    factor_list = factor_table[col_names[0]].dropna().values.tolist()
    if factor in factor_list:
        index = factor_list.index(factor)
        table_name = factor_table.iloc[index][col_names[1]]
        factor_name = factor_table.iloc[index][col_names[2]]
        arguments = "('" + str(date) + "', "+ "'" + table_name +"','" + factor_name + "','" + factor + "')"
        run_matlab = matlab_path + " -nodesktop -nosplash -r -wait \""+matlab_function + arguments +"\""+";quit;"
        # print(run_matlab)
        subprocess.call(run_matlab,cwd=matlab_code_path)

        if pd.isnull(table_name) or pd.isnull(factor_name):
            logger.info(factor + ' is not in the backup list')
            print('No backup')
    else:
        fall_back_htsc(factor, date)


def fall_back_htsc(factor, date):
    matlab_path = '\"D:\\013160\\matlab\\MATLAB_Production_Server\\R2015a\\bin\\matlab.exe"'
    matlab_code_path = 'D:\\013160\\data\\data\\'
    matlab_function = 'run_htsc'
    factor_table = pd.read_excel('documents\\exclude_list.xlsx')
    col_names = factor_table.columns.tolist()
    factor_list = factor_table[col_names[0]].dropna().values.tolist()
    if factor in factor_list:
        index = factor_list.index(factor)
        if factor_table.iloc[index][col_names[1]]:
            factor_new = factor_table.iloc[index][col_names[1]]
            factor_name = 'Factors.' + factor_new
            arguments = "(" +str(date) + ", "+ factor_name + ", '" + factor_new+ "', '" + factor +"')"
            run_matlab = matlab_path + " -nodesktop -nosplash -r -wait \""+matlab_function + arguments +"\""+";quit;"
            print(run_matlab)
            subprocess.call(run_matlab,cwd=matlab_code_path)
        else:
            print('No kind of data in htsc right now')
    else:
        factor_name = 'Factors.' + factor
        arguments = "(" +str(date) + ", "+ factor_name + ", '" + factor +"', '" + factor +"')"
        run_matlab = matlab_path + " -nodesktop -nosplash -r -wait \""+matlab_function + arguments +"\""+";quit;"
        print(run_matlab)
        subprocess.call(run_matlab,cwd=matlab_code_path)
if __name__ == '__main__':
    fall_back_htsc('assetsturn1','20170630')
