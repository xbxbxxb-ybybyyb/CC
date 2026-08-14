# @Time : 2021/12/7 9:44
# @Author : Zhichen Lu
# @File : HavedStockAnalysis.py
import pandas as pd
from online_conf import  local_config_path
from dataApi.sendInfo import send_file
from dataApi.tradeDate import get_pre_trade_date,get_date_range
from tqdm import tqdm
def get_halved_profit_detail_buy(today,out=False):
    target_stk = pd.read_pickle(f'{local_config_path}half_stk/{today}.pkl')
    fix_detail = pd.read_excel(f'/data/user/015664/AFuckingTrigger/实盘/{today}/成交明细及收盘持仓情况{today}.xlsx',sheet_name='收益明细')
    all_buy = fix_detail[fix_detail['类型'].eq('当日买入')]
    all_buy['成交金额'] = all_buy['成交价格']*all_buy['累计成交数量']

    halved_fix_detail = all_buy[all_buy['证券代码'].isin(target_stk)]
    detail_930 = pd.read_excel(f'/data/user/015664/AFuckingTrigger/对比930/{today}/逐笔收益930_{today}.xlsx', index_col=0)
    if detail_930.shape[0]>0:
        detail_930 = detail_930[detail_930['tag'].eq('当日买入')]
        inter_stk = list(set(detail_930.index).intersection(target_stk))
        halved_detail_930 = detail_930.loc[inter_stk]
        halved_detail_930['成交金额'] = halved_detail_930['买入成交价']*halved_detail_930['量']
    else:
        halved_detail_930 = pd.DataFrame(columns=['成交金额','费后收益'])
    return halved_fix_detail,halved_detail_930,all_buy['成交金额'].sum(),all_buy['费后收益'].sum()

def get_halved_profit_detail_sell(today,out=False):
    target_stk = pd.read_pickle(f'{local_config_path}half_stk/{get_pre_trade_date(today)}.pkl')
    fix_detail = pd.read_excel(f'/data/user/015664/AFuckingTrigger/实盘/{today}/成交明细及收盘持仓情况{today}.xlsx',sheet_name='收益明细')
    halved_fix_detail = fix_detail[fix_detail['证券代码'].isin(target_stk) & (~fix_detail['类型'].eq('当日买入'))]
    halved_fix_detail['成交金额'] = halved_fix_detail['成交价格']*halved_fix_detail['累计成交数量']
    detail_930 = pd.read_excel(f'/data/user/015664/AFuckingTrigger/对比930/{today}/逐笔收益930_{today}.xlsx', index_col=0)
    if detail_930.shape[0]>0:
        detail_930 = detail_930[~detail_930['tag'].eq('当日买入')]
        inter_stk = list(set(detail_930.index).intersection(target_stk))
        halved_detail_930 = detail_930.loc[inter_stk]
        halved_detail_930['成交金额'] = halved_detail_930['买入成交价']*halved_detail_930['量']
    else:
        halved_detail_930 = pd.DataFrame(columns=['成交金额','费后收益'])
    return halved_fix_detail,halved_detail_930,fix_detail['费后收益'].sum()

date_list = get_date_range(20210802,20211130)

buy_amt,buy_profit, all_trade_amt,pre_date_buy_profit,profit = {},{},{},{},{}

for idx,date in tqdm(enumerate(date_list)):
    buy_fix,buy_930,all_trade_amt[date],all_buy_profit = get_halved_profit_detail_buy(date)
    buy_amt[date] = buy_fix['成交金额'].sum() + buy_930['成交金额'].sum()
    buy_profit[date] = buy_fix['费后收益'].sum() + buy_930['费后收益'].sum()
    if idx==0:
        profit[date] = all_buy_profit
        continue
    sell_fix,sell_930,pre_day_profit = get_halved_profit_detail_sell(date)
    pre_date_buy_profit[date] = sell_fix['费后收益'].sum() + sell_930['费后收益'].sum()
    profit[date] = all_buy_profit+pre_day_profit

stat = pd.DataFrame({
    '当日减半买入带来收益':-1*pd.Series(buy_profit),
    '前日减半买入带来收益':-1*pd.Series(pre_date_buy_profit),
    '当日减半买入金额':buy_amt,
    '当日总买入金额':all_trade_amt,
    '当日收益':profit
})

stat['当日减半部分收益'] = stat['当日减半买入带来收益']+stat['前日减半买入带来收益']

stat.index = pd.to_datetime(stat.index.astype(str))
stat = stat.resample('1m').sum()
stat.index = stat.index.map(lambda x : x.strftime('%Y%m'))
stat.loc['8月以来'] = stat.sum()
stat['减半交易额占比'] = stat['当日减半买入金额']/( stat['当日减半买入金额']+ stat['当日总买入金额'])

out_file = './减半行业统计.xlsx'
stat.to_excel(out_file)
send_file(['015664'],out_file)


