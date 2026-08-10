year_list = [x*10000+101 for x in range(1995,2022,1)] + [20210701,20220101,20221001]
data_list = []
for i in range(1, len(year_list)):
    print(year_list[i-1],year_list[i])
    data = s.get_factor_value('WIND_CCommodityFuturesEODPrices', TRADE_DT=['>%s' % year_list[i-1],'<=%s' % year_list[i]])
    data.columns = [str.lower(x.replace('S_DQ_','')) for x in data.columns]
    data = data.drop(['object_id','change','oichange','opdate','opmode'], axis = 1)
    data = data[data.fs_info_type == '2'].rename(columns = {'s_info_windcode':'Ticker','trade_dt':'dt','presettle':'pre_settle'})
    data['dt'] = pd.to_datetime(data['dt'])
    data_list.append(data)
data = pd.concat(data_list).set_index(['dt', 'Ticker']).sort_index()

data = data.reset_index()

data['prod_id'] = data['Ticker'].apply(lambda x: "".join(re.findall(r'[A-Za-z]', x.split('.')[0])) + '.' + x.split('.')[1])
data['exchange'] = data['Ticker'].apply(lambda x: x.split('.')[1])

CFuturesDescription = s.get_factor_value('WIND_CFuturesDescription')[['S_INFO_WINDCODE', 'S_INFO_DELISTDATE']].rename(columns = {'S_INFO_WINDCODE':'Ticker'})
CFuturesDescription['S_INFO_DELISTDATE'] = pd.to_datetime(CFuturesDescription['S_INFO_DELISTDATE'])

data = pd.merge(data, CFuturesDescription, how = 'left')

data = data[data.fs_info_type == '2']

@functools.lru_cache(maxsize=None)
def expiration_days_helper(a,b):
    if a > b:
        return np.nan
    elif a != a or b != b:
        return np.nan
    else:
        return len(udt.get_trading_date_range(a, b)) - 1
    
dt_list = data['dt'].tolist()
ex_list = data['S_INFO_DELISTDATE'].tolist()
expiration_list = []
for i in tqdm(range(len(ex_list))):
    expiration_list.append(expiration_days_helper(dt_list[i], ex_list[i]))

data['expiration_days'] = expiration_list

data = data.set_index(['dt','Ticker'])
data['pre_close'] = data['close'].unstack().shift(1).stack()

data['amount'] = data['amount'].astype('float')
data = data.drop(['S_INFO_DELISTDATE'], axis = 1)
data = data[data['exchange'] != 'IB']
IO.pd_hdf5_writer(data, '/arch1/group/800466/warehouse/prod/MD/CHINA_FUTURE/DAILY/MD_CHINA_FUTURE_DAILY.h5', dataset='MD_CHINA_FUTURE_DAILY', data_columns=['dt', 'Ticker'], override=True)


def calculate_gap(contract):
    contract = contract.sort_index(level=0)
    gap = (contract['pre_close'] - contract['close'].shift(1)).fillna(0)
    gap.name = 'gap'
    return gap.cumsum()
    
# 以下为制作主力次主力合约数据    
md_base_data = IO.read_data(alt='/arch1/group/800466/warehouse/prod/MD/CHINA_COMMODITY/DAILY/MD_CHINA_COMMODITY_DAILY.h5')
md_data = md_base_data.reset_index()
main_contract = md_data.loc[md_data.groupby(['dt', 'prod_id'])['oi'].idxmax().dropna()].set_index(['dt', 'Ticker'])
main_contract = main_contract.sort_index(level=0)
md_data = md_base_data.drop(main_contract.index).reset_index()
second_main_contract = md_data.loc[md_data.groupby(['dt', 'prod_id'])['oi'].idxmax().dropna()].set_index(['dt', 'Ticker'])
second_main_contract = second_main_contract.sort_index(level=0)
main_contract['gap'] = main_contract.groupby('prod_id').apply(calculate_gap).reset_index(level=0, drop=True).sort_index(level=0)
second_main_contract['gap'] = second_main_contract.groupby('prod_id').apply(calculate_gap).reset_index(level=0, drop=True).sort_index(level=0)
main_contract = main_contract.reset_index().rename(columns= {'Ticker': 'wind_code', 'prod_id': 'Ticker'}).set_index(['dt', 'Ticker'])
second_main_contract = second_main_contract.reset_index().rename(columns= {'Ticker': 'wind_code', 'prod_id': 'Ticker'}).set_index(['dt', 'Ticker'])

IO.pd_hdf5_writer(main_contract, '/arch1/group/800466/warehouse/prod/MD/CHINA_COMMODITY/DAILY/MD_MAIN_CHINA_COMMODITY_DAILY.h5', dataset='MD_MAIN_CHINA_COMMODITY_DAILY', data_columns=['dt','Ticker'])
IO.pd_hdf5_writer(second_main_contract, '/arch1/group/800466/warehouse/prod/MD/CHINA_COMMODITY/DAILY/MD_SECONDMAIN_CHINA_COMMODITY_DAILY.h5', dataset='MD_SECONDMAIN_CHINA_COMMODITY_DAILY', data_columns=['dt','Ticker'])


# 增加计算gap
main = IO.read_data(alt = '/arch1/group/800466/warehouse/prod/MD/CHINA_COMMODITY/DAILY/MD_MAIN_CHINA_COMMODITY_DAILY.h5')
second_main = IO.read_data(alt = '/arch1/group/800466/warehouse/prod/MD/CHINA_COMMODITY/DAILY/MD_SECONDMAIN_CHINA_COMMODITY_DAILY.h5')

def calculate_gap(contract):
    contract = contract.sort_index(level=0)
    gap = (contract['pre_close'] - contract['close'].shift(1)).fillna(0)
    gap.name = 'gap'
    return gap.cumsum()

main['gap'] = main.groupby('Ticker').apply(calculate_gap).reset_index(level=0, drop=True).sort_index(level=0)
second_main['gap'] = second_main.groupby('Ticker').apply(calculate_gap).reset_index(level=0, drop=True).sort_index(level=0)

IO.pd_hdf5_writer(main, '/arch1/group/800466/warehouse/prod/MD/CHINA_COMMODITY/DAILY/MD_MAIN_CHINA_COMMODITY_DAILY.h5', dataset='MD_MAIN_CHINA_COMMODITY_DAILY', data_columns=['dt','Ticker'], override=True)
IO.pd_hdf5_writer(second_main, '/arch1/group/800466/warehouse/prod/MD/CHINA_COMMODITY/DAILY/MD_SECONDMAIN_CHINA_COMMODITY_DAILY.h5', dataset='MD_SECONDMAIN_CHINA_COMMODITY_DAILY', data_columns=['dt','Ticker'], override=True)