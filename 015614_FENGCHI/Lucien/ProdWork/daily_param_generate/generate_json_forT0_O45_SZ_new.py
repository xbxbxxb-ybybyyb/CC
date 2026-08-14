# -*- coding: utf-8 -*-
import pandas as pd
import json
import os
import datetime

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, bytes):
                return str(obj, encoding='utf-8')
            return json.JSONEncoder.default(self, obj)
        except UnicodeDecodeError:
            pass
    
def generate_paramsJson():
    today = datetime.date.today()
    date = today.strftime('%Y%m%d')
    
    commonPath = r'/data/group/800463/xiely/daily/'
    filepath = commonPath + 'excels/param-'+date+'-prod-O45-SZ-new.xlsx'
    
    param_df = pd.read_excel(filepath,sheet_name='InitialBasicParam',encoding='gbk')
    param_df['symbol'] = param_df['股票代码']
    param_df.set_index('symbol',inplace=True)
  
    choose_param_df = param_df.astype(str)
    choose_param_df  = choose_param_df[choose_param_df['期初可用仓位']!='0']
    
    commonPath = commonPath+'daily-param/'
    big_param_dict = {}
    for stock in choose_param_df.index:
        stock_param = {}
        stock_param['涨停板封单覆盖量'] = choose_param_df[choose_param_df['股票代码']==stock]['涨停板封单覆盖量'].values[0]
        stock_param['交易所监控的巨大额度'] = choose_param_df[choose_param_df['股票代码']==stock]['交易所监控的巨大额度'].values[0]
        stock_param['交易所监控的巨大股数'] = choose_param_df[choose_param_df['股票代码']==stock]['交易所监控的巨大股数'].values[0]       
        print(stock, stock_param)
        big_param_dict[stock] = stock_param
    with open(commonPath+'/'+date+'_forT0_O45_SZ_new.json','w',encoding='utf-8') as f:
        jsonObj = json.dumps(big_param_dict,cls = MyEncoder, ensure_ascii=False,indent=2)
        f.write(jsonObj)
            
generate_paramsJson()