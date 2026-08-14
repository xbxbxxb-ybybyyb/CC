# @Time : 2022/1/25 16:35
# @Author : Zhichen Lu
# @File : weight.py
from xquant.factordata import FactorData
import pandas as pd
from dataApi.sendInfo import send_file
s = FactorData()

weight = s.get_factor_value('Basic_factor',mddate=s.tradingday('20180101','20200101'),
                            factor_names=['index_weight_sh50','index_weight_hs300','index_weight_zz500'])

with pd.ExcelWriter('./Weight.xlsx') as writer:
    for each in weight.columns:
        temp = weight[each].reset_index().pivot_table(index='mddate', columns='stock', values=each).sort_index()
        temp.to_excel(writer,sheet_name=each)
    writer.close()
send_file(['015664'],'./Weight.xlsx')