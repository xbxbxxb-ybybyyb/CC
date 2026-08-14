import pandas as pd
from xquant.factordata import FactorData
s = FactorData()
from xquant.marketdata import MarketData
mdp = MarketData()

start_date, end_date = 20201201, 20221230 # 策略的重合区间
trading_days = s.tradingday(start_date, end_date)

print('交易日个数：%s'%(len(trading_days)))

# 读取指数行情
index_md = pd.read_pickle('/data/user/023859/Hedging/index_price_20200701_20230531.pkl')
index_md['next_0931']=index_md.groupby('Ticker')['price_0931'].shift(-1)
index_md['label_0931_next_0931'] = index_md['next_0931']/index_md['price_0931']-1
index_md_unstack = index_md.unstack()
index_md_unstack = index_md_unstack.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

# 读取指数成分股行业、权重、分钟价格数据
ZZ1000_sw_weight_and_price = pd.read_pickle('/data/user/023859/Hedging/ZZ1000_sw_weight_and_price_20200701_20230531.pkl')
ZZ1000_sw_weight_and_price = ZZ1000_sw_weight_and_price.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

ZZ1000_groupby_industry = ZZ1000_sw_weight_and_price.reset_index().groupby(['dt','sw_industry_code_1','sw_industry_name_1'])['weight'].sum().to_frame() # 按日期和行业统计zz1000成分股权重

df_strategy_sign_sw1 = pd.read_pickle('/data/user/023859/Hedging/df_strategy_sign_sw1_%s_%s.pkl'%(start_date, end_date))
print(df_strategy_sign_sw1)

