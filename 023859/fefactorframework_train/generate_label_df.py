import pandas as pd
from h5data.IO import IO
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

strategy_version = 20250513
start_date, end_date = 20170110,20250331

trading_days = s.tradingday(start_date, end_date)
start_date_ = int(s.tradingday(start_date,-250)[0])
end_date_ = int(s.tradingday(end_date,250)[-1])

strategy_path = f'/dfs/user/023859/neptune/{strategy_version}'
basic_file_path = '/dfs/user/023859/neptune/20250428/basic_file_zz1000_20160101_20250331.pkl' # zz1000基础样本
# md_path = '/dfs/user/023859/Neptune/label_1430_1440_next_0930_0940'
md_path_long = '/dfs/user/023859/neptune/label_1430_1440_next_0930_0940_long' # 计算标签所需价格数据
md_path_short = '/dfs/user/023859/neptune/label_1430_1440_next_0930_0940_short' # 计算标签所需价格数据

basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

md_long = []
filenames = os.listdir(md_path_long)
for file in filenames:
    if file.endswith('.pkl'):
        md_long.append(pd.read_pickle(os.path.join(md_path_long,file)))

md_short = []
filenames = os.listdir(md_path_short)
for file in filenames:
    if file.endswith('.pkl'):
        md_short.append(pd.read_pickle(os.path.join(md_path_short,file)))

md = pd.concat(md_long)[['pre_close','open','close','amt','adjfactor','buy_1430_1440_twap','sell_0930_0940_twap']].sort_index()
md['sell_1430_1440_twap'] = pd.concat(md_short)['sell_1430_1440_twap']
md['buy_0930_0940_twap'] = pd.concat(md_short)['buy_0930_0940_twap']

# 处理数据集错误
if '20230905' in trading_days:
    md.loc[(pd.Timestamp('20230905'),'601100.SH'),'adjfactor'] = np.nan
    md.loc[(pd.Timestamp('20230905'),'603338.SH'),'adjfactor'] = np.nan
    md.loc[(pd.Timestamp('20230905'),'605500.SH'),'adjfactor'] = np.nan
    md.loc[(pd.Timestamp('20230905'),'301349.SZ'),'adjfactor'] = np.nan
    md['adjfactor'] = md.groupby('Ticker')['adjfactor'].ffill()

md['close_adj'] = md['close']*md['adjfactor']
md['open_adj'] = md['open']*md['adjfactor']
md['next_open_adj'] = md.groupby('Ticker')['open_adj'].apply(lambda x: x.shift(-1).bfill())

md['buy_1430_1440_twap_adj'] = md['buy_1430_1440_twap']*md['adjfactor']
md['sell_0930_0940_twap_adj'] = md['sell_0930_0940_twap']*md['adjfactor']
md['next_sell_0930_0940_twap_adj'] = md.groupby('Ticker')['sell_0930_0940_twap_adj'].apply(lambda x: x.shift(-1).bfill())

md['sell_1430_1440_twap_adj'] = md['sell_1430_1440_twap']*md['adjfactor']
md['buy_0930_0940_twap_adj'] = md['buy_0930_0940_twap']*md['adjfactor']
md['next_buy_0930_0940_twap_adj'] = md.groupby('Ticker')['buy_0930_0940_twap_adj'].apply(lambda x: x.shift(-1).bfill())

# md['next_3_sell_931_1000_twap_adj'] = md.groupby('Ticker')['sell_931_1000_twap_adj'].apply(lambda x: x.shift(-3).bfill())
# md['next_5_sell_931_1000_twap_adj'] = md.groupby('Ticker')['sell_931_1000_twap_adj'].apply(lambda x: x.shift(-5).bfill())

md['label_t2o10dc_pos'] = 1 - md['next_buy_0930_0940_twap_adj']/md['sell_1430_1440_twap_adj']
md['label_Tc2b10_pos'] = 1 - md['close_adj']/md['sell_1430_1440_twap_adj']
md['label_TNo2Tc_pos'] = 1 - md['next_open_adj']/md['close_adj']
md['label_TNv2TNo_pos'] = 1 - md['next_buy_0930_0940_twap_adj']/md['next_open_adj']

md['label_t2o10dc_neg'] = md['next_sell_0930_0940_twap_adj']/md['buy_1430_1440_twap_adj'] - 1
md['label_Tc2b10_neg'] = md['close_adj']/md['buy_1430_1440_twap_adj'] - 1
md['label_TNo2Tc_neg'] = md['next_open_adj']/md['close_adj'] - 1
md['label_TNv2TNo_neg'] = md['next_sell_0930_0940_twap_adj']/md['next_open_adj'] - 1

# md['label_t4o30d1'] = md['next_3_sell_931_1000_twap_adj']/md['buy_931_1000_twap_adj'] - 1
# md['label_t6o30d1'] = md['next_5_sell_931_1000_twap_adj']/md['buy_931_1000_twap_adj'] - 1

md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))&(md.reset_index()['dt'] >= '2020-08-24')) | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md['ul_price'] = md['pre_close'].apply(lambda x: round_(x * 1.1, 2))
md['dl_price'] = md['pre_close'].apply(lambda x: round_(x * 0.9, 2))
md.loc[md['zcz'],'ul_price'] = md.loc[md['zcz'],'pre_close'].apply(lambda x: round_(x * 1.2, 2))
md.loc[md['zcz'],'dl_price'] = md.loc[md['zcz'],'pre_close'].apply(lambda x: round_(x * 0.8, 2))

md['label_T_close_is_zt'] = (md['close']==md['ul_price']).astype(float)
md = md[md['amt']>0]
md = md.sort_index(level=['Ticker', 'dt'])
md['label_Next_close_is_zt'] = md.groupby('Ticker')['label_T_close_is_zt'].shift(-1)
label_df = basic_file.join(md[['label_t2o10dc_neg','label_Tc2b10_neg','label_TNo2Tc_neg','label_TNv2TNo_neg',\
                                  'label_t2o10dc_pos','label_Tc2b10_pos','label_TNo2Tc_pos','label_TNv2TNo_pos',\
                                  'label_T_close_is_zt','label_Next_close_is_zt']])


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
label_df['buy_amt'] = 5e8 * label_df['weight'] # 每天5e规模

# IO.pd_hdf5_writer(label_df[['buy_amt']], hdf5='/dfs/user/023859/share_file/for_skk/neptune/20250513/zz1000_profit_interval.h5', dataset='neptune', override=True)
label_df = label_df.dropna()

# 存储数据，分享标签文件
label_df[['buy_amt','label_t2o10dc_neg','label_Tc2b10_neg','label_TNo2Tc_neg','label_TNv2TNo_neg',\
          'label_t2o10dc_pos','label_Tc2b10_pos','label_TNo2Tc_pos','label_TNv2TNo_pos',\
          'label_T_close_is_zt','label_Next_close_is_zt']].to_pickle(os.path.join(strategy_path, f'label_df_{start_date}_{end_date}.pkl'))

# IO.pd_hdf5_writer(label_df[['label_t2o10dc_pos','label_Tc2b10_pos','label_TNo2Tc_pos','label_TNv2TNo_pos',\
#           'label_T_close_is_zt','label_Next_close_is_zt']].rename(columns={'label_t2o10dc_pos':'label_t2o10dc','label_Tc2b10_pos':'label_Tc2b10',\
#                                                                            'label_TNo2Tc_pos':'label_TNo2Tc','label_TNv2TNo_pos':'label_TNv2TNo'}), \
#                   hdf5=f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/zz1000_labels_file_pos.h5', dataset='neptune')
#
# IO.pd_hdf5_writer(label_df[['label_t2o10dc_neg','label_Tc2b10_neg','label_TNo2Tc_neg','label_TNv2TNo_neg',\
#           'label_T_close_is_zt','label_Next_close_is_zt']].rename(columns={'label_t2o10dc_neg':'label_t2o10dc','label_Tc2b10_neg':'label_Tc2b10',\
#                                                                            'label_TNo2Tc_neg':'label_TNo2Tc','label_TNv2TNo_neg':'label_TNv2TNo'}), \
#                   hdf5=f'/dfs/user/023859/share_file/for_wj/neptune/{strategy_version}/zz1000_labels_file_neg.h5', dataset='neptune')
