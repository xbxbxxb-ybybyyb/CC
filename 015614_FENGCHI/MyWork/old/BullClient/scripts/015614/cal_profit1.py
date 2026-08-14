# coding: utf-8
# Author：fengchi863
# Date ：2020/8/20 10:02

import pandas as pd
from tqdm import tqdm

from BullClient.RecordDataSet.RecordDataSet import RecordDataSet

rds = RecordDataSet()
entrust = rds.get_entrust_data()
deliver = rds.get_deliver_data()

stock_queue = []
stock_set = set(deliver['证券代码'].tolist())


def stats_one_stk(stk_id: int, record: pd.DataFrame):
    fifo_df = pd.DataFrame(columns=['委托日期', '成交价格', '成交数量'])
    record_list = []
    real_mean_price = 0
    real_post_amount = 0
    first_buy_time = None
    date_set = sorted(list(set(record['委托日期'].tolist())))
    for date in list(date_set):
        one_day_deliver = record[record['委托日期'] == date]
        for idx in range(len(one_day_deliver)):
            one_deal_record = one_day_deliver.iloc[idx]  # 加入到FIFO队列
            init_date, business_flag, business_price, business_amount, business_balance = \
                one_deal_record['委托日期'], one_deal_record['买卖方向'], \
                one_deal_record['成交价格'], one_deal_record['成交数量'], one_deal_record['成交金额']
            if business_flag == '买入':
                fifo_df = fifo_df.append(pd.DataFrame([[init_date, business_price, business_amount]],
                                                      columns=['委托日期', '成交价格', '成交数量']))
                real_mean_price = (real_mean_price * real_post_amount + business_price * business_amount) / (
                            real_post_amount + business_amount)
                if real_post_amount == 0:
                    first_buy_time = init_date
                real_post_amount += business_amount
            if business_flag == '卖出':
                # 未知卖出信息，不参与统计
                if real_post_amount == 0:
                    continue
                business_time = one_deal_record['成交时间']
                pctchg = (business_price - real_mean_price) / real_mean_price
                if real_post_amount + business_amount <= 0:
                    business_amount = real_post_amount
                    real_post_amount = 0
                    real_mean_price = 0

                has_deal_flag = False
                for idx in range(len(fifo_df)):
                    tmp_df = fifo_df.iloc[idx]
                    buy_date, buy_amount, buy_price = tmp_df['委托日期'], tmp_df['成交数量'], tmp_df['成交价格']
                    if buy_amount + business_amount >= 0:
                        if not has_deal_flag:
                            first_buy_time = buy_date
                        fifo_df.iloc[idx, 2] += business_amount
                        break
                    else:
                        # 继续往后匹配
                        first_buy_time = buy_date
                        has_deal_flag = True
                        fifo_df.iloc[idx, 2] = 0
                        continue
                record_list.append([stk_id, first_buy_time, init_date, business_time,
                                    business_amount, business_balance, pctchg])
    return record_list

if __name__ == '__main__':
    record_list = []
    for stk_id in tqdm(sorted(list(stock_set))[:100]):
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
    profit = pd.DataFrame(record_list, columns=['证券代码', '首次买入日期', '卖出日期', '卖出时间', '卖出数量', '成交金额', '单笔收益'])
    profit['tmp'] = profit['成交金额'] * profit['单笔收益']
    group = profit.groupby(['证券代码', '卖出日期'])['tmp'].sum() / profit.groupby(['证券代码', '卖出日期'])['成交金额'].sum()
    profit = profit.sort_values(['证券代码', '卖出日期', '卖出时间'])
    profit.to_excel(rds.root_path + 'group_fc.xlsx')
