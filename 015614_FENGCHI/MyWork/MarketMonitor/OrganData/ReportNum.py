# coding: utf-8
# Author：fengchi863
# Date ：2021/11/12 17:54

from xquant.factordata import FactorData
from ShortTermTrading.dataApi import getData, tradeDate, stockList
from FaaMonitor.Util.DtUtil import DtUtil
from MarketMonitor.Tool.Ind import Ind
from FaaMonitor.Util.MyUtil import MyUtil
import time
import pandas as pd

fd = FactorData()
today_date = DtUtil.get_today_date()
t = time.time()
date_predict = fd.get_factor_value('WIND_AShareEarningEst',
                                   COLLECT_TIME=['>=20211101'],
                                   # S_INFO_WINDCODE=['600519.SH']
                                   )
                                   # COLLECT_TIME=['>=20140101', '<=20201231'])
col = ['S_INFO_WINDCODE',
       'EST_DT',
       'ANN_DT',
       'REPORTING_PERIOD',
       'COLLECT_TIME',
       'RESEARCH_INST_NAME',
       'FIRST_OPTIME',
       'REPORT_TYPECODE',
       'REPORT_NAME']
date_predict = date_predict[col]
date_predict = date_predict.sort_values(['REPORT_NAME'])
date_predict = date_predict.drop_duplicates(['S_INFO_WINDCODE', 'REPORT_NAME'])
report_count = date_predict.groupby('S_INFO_WINDCODE')['REPORT_NAME'].count().sort_values(ascending=False)
report_count.index = report_count.index.map(stockList.trans_windcode2int)
report_organ = date_predict.groupby('S_INFO_WINDCODE')['RESEARCH_INST_NAME'].apply(lambda x: ','.join(x.tolist()))
report_organ.index = report_organ.index.map(stockList.trans_windcode2int)
stk_code_list = report_count.index.tolist()
stk_id_list = report_count.index.map(stockList.trans_windcode2int)
ret = pd.DataFrame(index=stk_id_list, columns=['股票名称'])
ret['股票名称'] = ret.index.map(lambda x: MyUtil.get_1stock_name(x))
ret['行业'] = ret.index.map(lambda x: Ind.get_sw1_name(x))
ret['研报数'] = ret.index.map(lambda x: report_count[x])
ret['研报券商'] = ret.index.map(lambda x: report_organ[x])
print('消耗时间:', time.time() - t)

date_predict = date_predict[col]
