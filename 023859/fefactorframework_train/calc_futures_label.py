import pandas as pd
from tqdm import tqdm
import os
import decimal
from multiprocessing import Pool
from xquant.factordata import FactorData
s = FactorData()
from xquant.futuredata import FutureData
fd = FutureData()

strategy_path = f'/dfs/user/023859/neptune'

start_date, end_date =  20220722, 20241231
end_date_next = int(s.tradingday(end_date,5)[-1]) # 期货应该不会连着5个交易日有涨跌停
trading_days = s.tradingday(start_date, end_date_next)

# 生成md_futures数据
md_futures = []
for date in tqdm(trading_days):
    md_futures_date = fd.get_future_data_day('CF', date, 'K_Day')
    available_contracts = fd.get_instrument_all('IM', date, date)
    md_futures_date = md_futures_date[md_futures_date['HTSCSecurityID'].isin(available_contracts)]
    md_futures_date['dt'] = pd.to_datetime(md_futures_date['MDDate'])
    md_futures_date['Ticker'] = md_futures_date['HTSCSecurityID']
    md_futures.append(md_futures_date)

md_futures = pd.concat(md_futures)
md_futures = md_futures.set_index(['dt','Ticker']).sort_index()

def futures_round_(x, min_unit=0.2, method='ul'):
    x=x+1e-13
    multiple = decimal.Decimal(str(x)) / decimal.Decimal(str(min_unit))
    if method=='ul':
        rounded_multiple = multiple.quantize(decimal.Decimal('1'),rounding=decimal.ROUND_DOWN)
    elif method=='dl':
        rounded_multiple = multiple.quantize(decimal.Decimal('1'),rounding=decimal.ROUND_UP)
    else:
        raise TypeError('输入method错误')
    res = float(rounded_multiple*decimal.Decimal(str(min_unit)))
    return res

def calc_twap(date, md_futures_date):
    contract_list = list(md_futures_date.index.get_level_values(1).unique())
    for contract in contract_list:
        # tick_data = fd.get_future_data(contract, date+' 093000000', date+' 144000000', 'TICK')
        contract_ = contract.split('.')[0]
        tick_data = pd.read_pickle(f'/dfs/group/800463/data/futures_data/IM/tick/{contract_}/{date}'+'.pkl')
        pre_close = tick_data['pre_close'].iloc[-1]
        open_px = tick_data['OpenPx'].iloc[-1]
        ul_price = tick_data['MaxPx'].iloc[-1]
        dl_price = tick_data['MinPx'].iloc[-1]
        md_futures_date.loc[(pd.to_datetime(date),contract),'pre_close'] = pre_close
        md_futures_date.loc[(pd.to_datetime(date),contract),'open'] = open_px
        md_futures_date.loc[(pd.to_datetime(date),contract),'ul_price'] = ul_price
        md_futures_date.loc[(pd.to_datetime(date),contract),'dl_price'] = dl_price
        tick_data_1430 = tick_data[(tick_data['MDTime'] > 143000000)&(tick_data['MDTime'] < 144000000)]
        tick_data_931 = tick_data[(tick_data['MDTime'] > 93100000)&(tick_data['MDTime'] < 94100000)]
        tick_data_1000 = tick_data[(tick_data['MDTime'] > 100000000)&(tick_data['MDTime'] < 101000000)]

        twap_1430_1440 = tick_data_1430['LastPx'].where((tick_data_1430['LastPx']!=0) & (tick_data_1430['LastPx']<ul_price) & (tick_data_1430['LastPx']>dl_price)).mean()
        # sell_1430_1440_twap = tick_data_1430['Buy1Price'].where((tick_data_1430['Buy1Price']!=0) & (tick_data_1430['Buy1Price']<ul_price) & (tick_data_1430['Buy1Price']>=dl_price)).mean()
        twap_0931_0941 = tick_data_931['LastPx'].where((tick_data_931['LastPx']!=0) & (tick_data_931['LastPx']>dl_price) & (tick_data_931['LastPx']<ul_price)).mean()
        # sell_0930_0940_twap = tick_data_931['Buy1Price'].where((tick_data_931['Buy1Price']!=0) & (tick_data_931['Buy1Price']>=dl_price) & (tick_data_931['Buy1Price']<ul_price)).mean()
        twap_1000_1010 = tick_data_1000['LastPx'].where((tick_data_1000['LastPx']!=0) & (tick_data_1000['LastPx']>dl_price) & (tick_data_1000['LastPx']<ul_price)).mean()

        md_futures_date.loc[(pd.to_datetime(date),contract),'twap_1430_1440'] = twap_1430_1440
        # md_futures_date.loc[(pd.to_datetime(date),contract),'sell_1430_1440_twap'] = sell_1430_1440_twap
        md_futures_date.loc[(pd.to_datetime(date),contract),'twap_0931_0941'] = twap_0931_0941
        # md_futures_date.loc[(pd.to_datetime(date),contract),'sell_0930_0940_twap'] = sell_0930_0940_twap
        md_futures_date.loc[(pd.to_datetime(date),contract),'twap_1000_1010'] = twap_1000_1010

    return md_futures_date

with Pool(processes=24) as pool:
    results = pool.starmap(calc_twap, [(date, md_futures.loc[date]) for date in trading_days])

md_futures_res = []
for result in results:
    md_futures_res.append(result)

md_futures = pd.concat(md_futures_res).sort_index()
md_futures['next_0931_0941_twap'] = md_futures.groupby('Ticker')['twap_0931_0941'].apply(lambda x: x.shift(-1).bfill())
md_futures['next_1000_1010_twap'] = md_futures.groupby('Ticker')['twap_1000_1010'].apply(lambda x: x.shift(-1).bfill())
md_futures['next_1430_1440_twap'] = md_futures.groupby('Ticker')['twap_1430_1440'].apply(lambda x: x.shift(-1).bfill())
md_futures['close'] = md_futures.groupby('Ticker')['pre_close'].shift(-1)
md_futures['next_open'] = md_futures.groupby('Ticker')['open'].shift(-1)

md_futures['label_s1_short'] = md_futures['twap_1000_1010'] / md_futures['twap_0931_0941'] - 1
md_futures['label_s1_mid'] = md_futures['twap_1430_1440'] / md_futures['twap_0931_0941'] - 1
md_futures['label_s1_long'] = md_futures['next_0931_0941_twap'] / md_futures['twap_0931_0941'] - 1

md_futures['label_sc_short'] = md_futures['next_0931_0941_twap'] / md_futures['twap_1430_1440'] - 1
md_futures['label_sc_mid'] = md_futures['next_1000_1010_twap'] / md_futures['twap_1430_1440'] - 1
md_futures['label_sc_long'] = md_futures['next_1430_1440_twap'] / md_futures['twap_1430_1440'] - 1

md_futures['label_sc_mid_Tc2b10'] = md_futures['close'] / md_futures['twap_1430_1440'] - 1
md_futures['label_sc_mid_TNo2Tc'] = md_futures['next_open'] / md_futures['close'] - 1
md_futures['label_sc_mid_TNv2TNo'] = md_futures['next_1000_1010_twap'] / md_futures['next_open'] - 1

md_futures.to_pickle(os.path.join(strategy_path, f'label_df_IM_{start_date}_{end_date}.pkl'))