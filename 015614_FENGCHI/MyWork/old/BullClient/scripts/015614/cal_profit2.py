# coding: utf-8
# Author：fengchi863
# Date ：2020/8/21 15:27

import pandas as pd
from tqdm import tqdm

from BullClient.RecordDataSet.RecordDataSet import RecordDataSet

rds = RecordDataSet()
entrust = rds.get_entrust_data()
deliver = rds.get_deliver_data()

stock_queue = []
stock_set = set(deliver['证券代码'].tolist())


def stats_one_stk(stk_id: int, record: pd.DataFrame):
    record_list = []
    real_mean_price = 0
    real_post_amount = 0
    date_set = sorted(list(set(record['委托日期'].tolist())))
    for date in list(date_set):
        if stk_id == 2143 and date == 20140429:
            print(1)
        one_day_deliver = record[record['委托日期'] == date]
        one_day_business_amount = one_day_deliver['成交数量'].sum()
        # 净买入
        if one_day_business_amount >= 0:
            mkt_cap = (one_day_deliver['成交数量'] * one_day_deliver['成交价格']).sum()
            real_mean_price = (real_post_amount * real_mean_price + mkt_cap) / (
                        real_post_amount + one_day_business_amount)
            real_post_amount += one_day_business_amount
        # 净卖出
        elif one_day_business_amount < 0:
            if real_post_amount + one_day_business_amount < 0:
                one_day_business_amount = -real_post_amount
            real_post_amount += one_day_business_amount
            mkt_cap = (one_day_deliver['成交数量'] * one_day_deliver['成交价格']).sum()
            mean_price = mkt_cap / one_day_business_amount
            pctchg = (mean_price - real_mean_price) / real_mean_price
            if one_day_business_amount != 0 and real_mean_price != 0:
                record_list.append([stk_id, date, one_day_business_amount, real_mean_price, mean_price, pctchg])
            if real_post_amount + one_day_business_amount == 0:
                real_post_amount = 0
                real_mean_price = 0
    return record_list


if __name__ == '__main__':
    record_list = []
    for stk_id in tqdm(sorted(list(stock_set))):
        one_stk_deliver = deliver[deliver['证券代码'] == stk_id]
        for idx in range(len(one_stk_deliver)):
            record = one_stk_deliver.iloc[idx]
            init_date, business_time, business_flag, business_amount, post_amount, business_balance = \
                record['委托日期'], record['成交时间'], record['买卖方向'], record['成交数量'], \
                record['剩余股数'], record['成交金额']
            if business_flag == '买入':
                business_list = stats_one_stk(stk_id, one_stk_deliver)
                for one_record in business_list:
                    record_list.append(one_record)
                break  # 跳出当前股票
            else:
                continue
    profit = pd.DataFrame(record_list, columns=['证券代码', '卖出日期', '卖出数量', '前均价', '当天均价', '单笔收益'])
    profit = profit.sort_values(['证券代码', '卖出日期'])
    profit.to_excel(rds.root_path + 'profit_fc_method2.xlsx')
