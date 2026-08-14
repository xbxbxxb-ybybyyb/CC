import pandas as pd
from tqdm import tqdm
from xquant.factordata import FactorData
s = FactorData()

start_date, end_date = 20170110, 20241231
trading_days = s.tradingday(start_date, 20250331)
index_df = pd.DataFrame(index=trading_days,columns=['1430_1440_twap','0931_0941_twap','1000_1010_twap'])
for date in tqdm(trading_days):
    tick_data = pd.read_pickle(f'/dfs/group/800463/data/index_data/ZZ1000/{date}'+'.pkl')
    tick_data_open = tick_data[(tick_data['MDTime'] > 143000000)&(tick_data['MDTime'] < 144000000)]
    tick_data_close_short = tick_data[(tick_data['MDTime'] > 93100000)&(tick_data['MDTime'] < 94100000)]
    tick_data_close_mid = tick_data[(tick_data['MDTime'] > 100000000) & (tick_data['MDTime'] < 101000000)]
    twap_1430_1440 = tick_data_open['LastPx'].mean()
    twap_0931_0941 = tick_data_close_short['LastPx'].mean()
    twap_1000_1010 = tick_data_close_mid['LastPx'].mean()
    pre_close = tick_data['PreClosePx'].iloc[-1]
    open_px = tick_data['OpenPx'].iloc[-1]
    index_df.loc[date,'1430_1440_twap'] = twap_1430_1440
    index_df.loc[date,'1000_1010_twap'] = twap_1000_1010
    index_df.loc[date,'0931_0941_twap'] = twap_0931_0941
    index_df.loc[date,'pre_close'] = pre_close
    index_df.loc[date, 'open'] = open_px

index_df['next_0931_0941_twap'] = index_df['0931_0941_twap'].shift(-1)
index_df['next_1000_1010_twap'] = index_df['1000_1010_twap'].shift(-1)
index_df['next_1430_1440_twap'] = index_df['1430_1440_twap'].shift(-1)
index_df['close'] = index_df['pre_close'].shift(-1)
index_df['next_open'] = index_df['open'].shift(-1)

index_df['label_pct_short_term'] = index_df['next_0931_0941_twap'] / index_df['1430_1440_twap'] - 1
index_df['label_pct_mid_term'] = index_df['next_1000_1010_twap'] / index_df['1430_1440_twap'] - 1
index_df['label_pct_long_term'] = index_df['next_1430_1440_twap'] / index_df['1430_1440_twap'] - 1
index_df['label_pct_mid_term_Tc2b10'] = index_df['close'] / index_df['1430_1440_twap'] - 1
index_df['label_pct_mid_term_TNo2Tc'] = index_df['next_open'] / index_df['close'] - 1
index_df['label_pct_mid_term_TNv2TNo'] = index_df['next_1000_1010_twap'] / index_df['next_open'] - 1

index_df = index_df.rename_axis('dt')
index_df = index_df.reset_index()

index_df['dt'] = pd.to_datetime(index_df['dt'])
index_df['Ticker'] = '000852.SH'

index_df.set_index(['dt','Ticker'])[['label_pct_short_term','label_pct_mid_term','label_pct_long_term',\
                                     'label_pct_mid_term_Tc2b10','label_pct_mid_term_TNo2Tc','label_pct_mid_term_TNv2TNo']].loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))].to_pickle(f'/dfs/user/023859/share_file/for_wys/zz1000/20250612/index_label_sc_{start_date}_{end_date}.pkl')