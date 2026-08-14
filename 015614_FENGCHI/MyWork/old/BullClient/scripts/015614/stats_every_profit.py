# coding: utf-8
# Author：fengchi863
# Date ：2020/8/26 19:33
import pandas as pd, numpy as np
from tqdm import tqdm
from BullClient.RecordDataSet.RecordDataSet import RecordDataSet
from StrongStockModel.dataApi.getData import get_daily_1factor, get_date_range
from StrongStockModel.dataApi.tradeDate import get_trade_date_interval
from BullClient.conf.path_conf import fc_out_path

date_list = get_date_range(20140401, 20151231)
rds = RecordDataSet()
deliver = rds.get_clean_deliver_data()

len_deliver = len(deliver)
record = []
for idx in tqdm(range(len_deliver)):
    tmp_deliver = deliver.iloc[idx]
    if tmp_deliver['成交数量'] == tmp_deliver['剩余股数']:
        # 找到一笔新建仓的股票
        start_date, stk_id, stk_name = tmp_deliver['委托日期'], tmp_deliver['证券代码'], tmp_deliver['证券名称']
        stk_deliver = deliver[(deliver['证券代码'] == stk_id) & (deliver['委托日期'] >= start_date) &
                              (deliver.index >= idx)]
        full_flag = False
        for ii in range(len(stk_deliver)):
            tmp_stk_deliver = stk_deliver.iloc[ii]
            if tmp_stk_deliver['剩余股数'] == 0:
                full_flag = True
                all_sell_ii = ii
                end_date = tmp_stk_deliver['委托日期']
                break
        if full_flag:
            full_stk_deliver = stk_deliver.iloc[:all_sell_ii+1]  # 这里没有考虑一种盘中清仓然后再盘中建仓的情况
            total_buy_amt = full_stk_deliver[full_stk_deliver['买卖方向']=='买入']['成交金额'].sum()
            total_sell_amt = full_stk_deliver[full_stk_deliver['买卖方向']=='卖出']['成交金额'].sum()
            profit = total_sell_amt - total_buy_amt
            record.append([stk_id, stk_name, start_date, end_date, total_buy_amt, total_sell_amt, profit])

res = pd.DataFrame(record)
res.columns = ['证券代码', '证券名称', '建仓日期', '平仓日期', '总买入金额', '总卖出金额', '持仓阶段总收益']
res['持仓天数'] = res[['平仓日期', '建仓日期']].apply(lambda x: 1 + get_trade_date_interval(x['平仓日期'], x['建仓日期']), axis=1)
res['是否盈利'] = res['持仓阶段总收益'].apply(lambda x: '是' if x > 0 else '否')
res.to_excel(fc_out_path + '单笔持仓收益计算.xlsx')