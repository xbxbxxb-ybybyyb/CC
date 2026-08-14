import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import decimal
from xquant.factordata import FactorData
from xquant.marketdata import MarketData
s = FactorData()
mdp = MarketData()

def round_(x, n=13):
    x = x + 1e-15
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

strategy_version = 20250528
start_date, end_date = 20170110,20241231

trading_days = s.tradingday(start_date, end_date)

strategy_path = f'/dfs/user/023859/neptune/{strategy_version}'
basic_file_path = f'/dfs/user/023859/neptune/{strategy_version}/basic_file_zz1000_20170110_20250331.pkl' # zz1000基础样本
md_path = f'/dfs/user/023859/neptune/{strategy_version}/label_0931_0940_t_1000_1010'

basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

md = []
filenames = os.listdir(md_path)
for file in filenames:
    if file.endswith('.pkl'):
        md.append(pd.read_pickle(os.path.join(md_path,file)))

md = pd.concat(md)[['pre_close','open','close','amt','adjfactor','buy_0931_0940_twap','sell_0931_0940_twap',\
                    'buy_1000_1010_twap','sell_1000_1010_twap','buy_amt_pos_ratio','buy_amt_neg_ratio']].sort_index(level=['Ticker', 'dt'])

# 处理数据集错误
if '20230905' in trading_days:
    md.loc[(pd.Timestamp('20230905'),'601100.SH'),'adjfactor'] = np.nan
    md.loc[(pd.Timestamp('20230905'),'603338.SH'),'adjfactor'] = np.nan
    md.loc[(pd.Timestamp('20230905'),'605500.SH'),'adjfactor'] = np.nan
    md.loc[(pd.Timestamp('20230905'),'301349.SZ'),'adjfactor'] = np.nan
    md['adjfactor'] = md.groupby('Ticker')['adjfactor'].ffill()

md['buy_0931_0940_twap_adj'] = md['buy_0931_0940_twap']*md['adjfactor']
md['sell_1000_1010_twap_adj'] = md['sell_1000_1010_twap']*md['adjfactor']
md['sell_1000_1010_twap_adj'] = md['sell_1000_1010_twap_adj'].groupby('Ticker').apply(lambda x: x.bfill())

md['sell_0931_0940_twap_adj'] = md['sell_0931_0940_twap']*md['adjfactor']
md['buy_1000_1010_twap_adj'] = md['buy_1000_1010_twap']*md['adjfactor']
md['buy_1000_1010_twap_adj'] = md['buy_1000_1010_twap_adj'].groupby('Ticker').apply(lambda x: x.bfill())

md['label_t2o9d1_pos'] = 1 - md['buy_1000_1010_twap_adj']/md['sell_0931_0940_twap_adj']
md['label_t2o9d1_neg'] = md['sell_1000_1010_twap_adj']/md['buy_0931_0940_twap_adj'] - 1

md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))&(md.reset_index()['dt'] >= '2020-08-24')) | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md['ul_price'] = md['pre_close'].apply(lambda x: round_(x * 1.1, 2))
md['dl_price'] = md['pre_close'].apply(lambda x: round_(x * 0.9, 2))
md.loc[md['zcz'],'ul_price'] = md.loc[md['zcz'],'pre_close'].apply(lambda x: round_(x * 1.2, 2))
md.loc[md['zcz'],'dl_price'] = md.loc[md['zcz'],'pre_close'].apply(lambda x: round_(x * 0.8, 2))

md['label_T_close_is_zt'] = (md['close']==md['ul_price']).astype(float)
md = md[md['amt']>0]
md = md.sort_index(level=['Ticker', 'dt'])
md['label_Next_close_is_zt'] = md.groupby('Ticker')['label_T_close_is_zt'].shift(-1)
label_df = basic_file.join(md[['label_t2o9d1_neg', 'label_t2o9d1_pos', 'label_T_close_is_zt','label_Next_close_is_zt','buy_amt_pos_ratio','buy_amt_neg_ratio']])

ZZ1000_weight = []
for date in tqdm(trading_days):
    df_ZZ1000 = s.hset('INDEX',date,'ZZ1000',weightType=1) # 选择预估权重，避免回测用到未来数据
    ZZ1000_weight_date = pd.DataFrame(index = df_ZZ1000['stock'])
    ZZ1000_weight_date.index.names = ['stock']
    ZZ1000_weight_date['weight'] = df_ZZ1000.set_index('stock')['weight']/100
    ZZ1000_weight_date = ZZ1000_weight_date.reset_index()
    ZZ1000_weight_date['dt'] = pd.Timestamp(date)
    ZZ1000_weight_date = ZZ1000_weight_date.rename(columns={'stock':'Ticker'})
    ZZ1000_weight_date = ZZ1000_weight_date.set_index(['dt','Ticker'])[['weight']]
    ZZ1000_weight.append(ZZ1000_weight_date)

ZZ1000_weight = pd.concat(ZZ1000_weight, axis=0)

label_df['weight'] = ZZ1000_weight['weight']
label_df['buy_amt'] = 5e8 * label_df['weight'] * label_df['buy_amt_neg_ratio']# 每天5e规模
# IO.pd_hdf5_writer(label_df[['buy_amt']], hdf5='/dfs/user/023859/share_file/for_skk/neptune/20250513/zz1000_profit_interval.h5', dataset='neptune', override=True)
label_df = label_df.dropna()
label_df = label_df.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]

# 存储数据，分享标签文件
label_df[['buy_amt','weight','label_t2o9d1_neg', 'label_t2o9d1_pos', 'label_T_close_is_zt','label_Next_close_is_zt']].to_pickle(os.path.join(strategy_path, f'label_df_s1_{start_date}_{end_date}.pkl'))
