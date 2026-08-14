import numpy as np
import pandas as pd
from xquant.factordata import FactorData

import IO

s = FactorData()
import datetime as dt

path_user = '/data/user/015614/daily/灰名单生成/黑名单/'
path_group = '/data/group/800463/stock_list/'


date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]


lastdate = s.tradingday(date, -2)[0]

MD_data = IO.read_data([s.tradingday(str(lastdate), -300)[0], lastdate],
                       columns=['pre_close', 'high', 'low', 'close', 'amt'],
                       alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
is_yzdt = (MD_data['high'] == MD_data['low']) & (MD_data['high'] < MD_data['pre_close']) & (MD_data['amt'] != 0)


# -------------------------------------------------------------------------------------
def cal_cum_zt(x):
    x_cs = 1.0 * x.fillna(0).cumsum()
    cum_zt = (x_cs - x_cs[x != True].reindex(x_cs.index).fillna(method='ffill').fillna(0)).fillna(0)
    return cum_zt


# 计算暂停的日期数量
cum_yzdt = cal_cum_zt(is_yzdt.unstack())
cum_yzdt_recovery_temp = cum_yzdt.copy()
# 一字跌停规则：对于T日一字跌停的股票：
# 第1个：T+1日不交易
# 第2个：T+1至T+10日不交易
# 第3个及以上：T+1至T+N*10日不交易
# 大于250设置为250
cum_yzdt_recovery_temp[cum_yzdt == 0] = np.nan
cum_yzdt_recovery_temp[cum_yzdt == 2] = 5
cum_yzdt_recovery_temp[cum_yzdt >= 3] = cum_yzdt_recovery_temp[cum_yzdt >= 3] * 5
cum_yzdt_recovery_temp[cum_yzdt_recovery_temp >= 250] = 250
# cum_yzdt_recovery_time_old = (cum_yzdt_recovery_temp.fillna(0).rolling(250, 1).max().stack()) TODO:我注释掉了

# TODO:这个函数是计算什么因子的
def cal_indicator_value(cum_yzdt_recovery_data, cum_yzdt_data):
    res_mat = np.full(shape=(np.shape(cum_yzdt_recovery_data.fillna(0).T)), fill_value=0)
    res_mat_2 = np.full(shape=(np.shape(cum_yzdt.T)), fill_value=0)
    yzdt_values = cum_yzdt_recovery_data.fillna(0).T.values
    cum_yzdt_values = cum_yzdt_data.T.values
    for i in range(len(res_mat)):
        print(i)
        this_stock_yzdt_value = yzdt_values[i]
        this_stock_cum_yzdt_value = cum_yzdt_values[i]
        dummy_value = 0
        indicator_value = 0
        dt_value = 0
        for j in range(len(this_stock_yzdt_value)):
            current_value = this_stock_yzdt_value[j]
            cum_dt_value = this_stock_cum_yzdt_value[j]
            if current_value > (dummy_value - 1):
                indicator_value = current_value
                dummy_value = current_value
                dt_value = cum_dt_value
            else:
                dummy_value = dummy_value - 1
            res_mat[i][j] = indicator_value
            res_mat_2[i][j] = dt_value
    return pd.DataFrame(res_mat.T, columns=cum_yzdt_recovery_data.columns, index=cum_yzdt_recovery_data.index).stack(), \
           pd.DataFrame(res_mat_2.T, columns=cum_yzdt.columns, index=cum_yzdt.index).stack()


cum_yzdt_recovery_time, _ = cal_indicator_value(cum_yzdt_recovery_temp, cum_yzdt)

# 计算当前正常的日期数
non_yzdt = is_yzdt == False
cum_nonyzdt = cal_cum_zt(non_yzdt.unstack())
cum_nonyzdt_time = cum_nonyzdt.stack()

# 生成正常日期小于暂停日期的样本   TODO:这个条件是什么意思
MD_data_cut = MD_data.loc[lastdate]
MD_data_cut['688'] = MD_data_cut.reset_index()['Ticker'].apply(lambda x: x[0:3] == '688').values
MD_data_cut['BJ'] = MD_data_cut.reset_index()['Ticker'].apply(lambda x: x[-3:] == '.BJ').values
# ordinary_stock_today = MD_data_cut[(MD_data_cut['688'] == False) & (MD_data_cut['BJ'] == False)]
# ordinary_stock_today = MD_data_cut[MD_data_cut['BJ'] == False]
ordinary_stock_today = MD_data_cut
dt_list_temp = cum_nonyzdt_time[cum_nonyzdt_time < cum_yzdt_recovery_time].reindex(ordinary_stock_today.index).dropna()
out_df = dt_list_temp.reset_index()[['Ticker', 0]]

# ----------------------储存模块---------------------------------
name_data = IO.read_data([lastdate, lastdate],
                         alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
if len(name_data) == 0:
    llastdate = s.tradingday(lastdate, -3)[0]
    _name_data = IO.read_data([llastdate, llastdate], alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
stock_name = list()
for i in out_df['Ticker']:
    if i == '600077.SH':    # d20230726 name_data中没有这个个股的名字
        stock_name.append('ST宋都')
        continue
    if i == '600898.SH':    # d20250205 name_data中没有这个个股的名字
        stock_name.append('*ST美讯')
        continue
    if len(name_data) != 0:
        stock_name.append(name_data.loc[pd.Timestamp(lastdate), i]['STOCK_NAME'].values[0])
    else:
        stock_name.append(_name_data.loc[pd.Timestamp(llastdate), i]['STOCK_NAME'].values[0])
out = pd.DataFrame(stock_name, columns=['证券名称'])
out['证券代码'] = out_df['Ticker'].values
out['证券代码'] = out['证券代码'].apply(lambda x: x[:~2])
out['累计非一字跌停交易日'] = cum_nonyzdt_time.loc[dt_list_temp.index].values
out['暂停交易日数量'] = cum_yzdt_recovery_time.loc[dt_list_temp.index].values


def excel_saver(output_dict, excel_name, index):
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer, sheet_name=key, index=index)
    writer.save()
    return


print(stock_name)
excel_saver({'跌停后黑名单': out}
            , path_user + 'after_dt_list_%s.xlsx' % lastdate, index=None)
excel_saver({'跌停后黑名单':out}
            ,path_group+'after_dt_list/after_dt_list_%s.xlsx'%lastdate,index = None)


from xquant.xqutils.helper import link

lm = link.LinkMessage()
message = '跌停后黑名单上传成功：' + str(len(out)) + '只股票'
lm.sendMessage(message)
