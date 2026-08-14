import pandas as pd
from h5data.IO import IO
from tqdm import tqdm
import statsmodels.api as sm
from xquant.factordata import FactorData
s = FactorData()

def get_risk_data(start_date, end_date):
    risk_df = IO.read_data([start_date, end_date], alt='/data/group/800080/warehouse/prod/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5')

    return risk_df

def get_sw_info(data_df):
    df_stock_list = data_df.reset_index().groupby('dt')['Ticker'].agg(lambda x: list(set(x)))
    data_sw_info = []
    for dt in tqdm(df_stock_list.index):
        date = dt.strftime('%Y%m%d')
        if date < '20211213':
            flag = 'SW'
        else:
            flag = 'SW2021'
        sw_index_date = pd.DataFrame(index=df_stock_list.loc[dt], columns=['sw_industry_code_1', 'sw_industry_name_1'])
        sw_index_date.index.names = ['stock']
        sw1 = s.hsi(df_stock_list.loc[dt], date, flag, 1).set_index('stock')
        sw2 = s.hsi(df_stock_list.loc[dt], date, flag, 2).set_index('stock')

        sw_index_date[['sw_industry_code_1', 'sw_industry_name_1']] = sw1[['industry_code', 'industry_name']]
        sw_index_date[['sw_industry_code_2', 'sw_industry_name_2']] = sw2[['industry_code', 'industry_name']]
        sw_index_date = sw_index_date.reset_index()
        sw_index_date['dt'] = dt
        sw_index_date = sw_index_date.rename(columns={'stock': 'Ticker'})
        sw_index_date = sw_index_date.set_index(['dt', 'Ticker'])[['sw_industry_code_1', 'sw_industry_name_1', 'sw_industry_code_2', 'sw_industry_name_2']]

        data_sw_info.append(sw_index_date)

    data_sw_info = pd.concat(data_sw_info, axis=0)
    data_df = data_df.reset_index().merge(data_sw_info.reset_index(), on=['dt', 'Ticker'], how='left').set_index(['dt', 'Ticker']).sort_index()  # 策略信号样本收益信号及所属申万一级行业
    # data_df['sw_industry_code'] = data_df['sw_industry_code_1']
    data_df['sw_industry_code'] = data_df.apply(lambda row: row['sw_industry_code_2'] if row['sw_industry_name_1'] == '非银金融' else row['sw_industry_code_1'],axis=1)
    data_df['sw_industry_name'] = data_df.apply(lambda row: row['sw_industry_name_2'] if row['sw_industry_name_1'] == '非银金融' else row['sw_industry_name_1'],axis=1)
    return data_df

# 用行业中位数填充缺失值
def fill_na_by_industry_median(data_df, style_factor_cols=None, industry_col='Industry'):
    data_df = data_df.copy()
    if style_factor_cols is None:
        style_factor_cols = ['Beta', 'BookToPrice', 'DividendYield','EarningsQuality',
        'EarningsVariability', 'EarningsYield', 'Growth', 'InvestmentQuality', 'Leverage', 'Liquidity',
        'LongTermReversal', 'MidCapitalization', 'Momentum', 'Profitability', 'ResidualVolatility', 'Size']
    for col in style_factor_cols:
        missing_mask = data_df[col].isna()

        median_vals = (
            data_df.groupby(['dt', industry_col])[col].transform('median')
        )

        data_df.loc[missing_mask, col] = median_vals[missing_mask]
    return data_df

# 用全部样本中位数填充缺失值
def fill_na_by_all_median(data_df, style_factor_cols=None):
    data_df = data_df.copy()
    if style_factor_cols is None:
        style_factor_cols = ['Beta', 'BookToPrice', 'DividendYield','EarningsQuality',
        'EarningsVariability', 'EarningsYield', 'Growth', 'InvestmentQuality', 'Leverage', 'Liquidity',
        'LongTermReversal', 'MidCapitalization', 'Momentum', 'Profitability', 'ResidualVolatility', 'Size']
    for col in style_factor_cols:
        missing_mask = data_df[col].isna()

        median_vals = (
            data_df.groupby('dt')[col].transform('median')
        )

        data_df.loc[missing_mask, col] = median_vals[missing_mask]
    return data_df

def mad_clip_series(series, k=5):
    median = series.median()
    mad = (series - median).abs().median()
    upper = median + k * mad
    lower = median - k * mad
    return series.clip(lower, upper)

def mad_clip_by_day(data_df, cols, k=5):
    data_df = data_df.copy()
    for col in cols:
        data_df[col] = (
            data_df.groupby('dt')[col].transform(lambda x: mad_clip_series(x,k=k))
        )
    return data_df

def standardize_data(data_df, style_factors = ['Beta', 'BookToPrice', 'DividendYield','EarningsQuality',
        'EarningsVariability', 'EarningsYield', 'Growth', 'InvestmentQuality', 'Leverage', 'Liquidity',
        'LongTermReversal', 'MidCapitalization', 'Momentum', 'Profitability', 'ResidualVolatility', 'Size']):
    def standardize_(group):
        mkt_weight = group['Circu_Mkt']
        weight_sum = mkt_weight.sum()
        weight = mkt_weight / weight_sum
        result = {}
        for factor in style_factors:
            x = group[factor]
            weighted_mean = (x * weight).sum()
            equal_weight_std = x.std(ddof=0)
            result[factor] = (x - weighted_mean) / equal_weight_std
        return pd.DataFrame(result, index=group.index)

    standardized_df = data_df.groupby('dt').apply(standardize_)
    data_df = data_df[['list_len','Circu_Mkt','sw_industry_code','sw_industry_code_1','sw_industry_name','sw_industry_name_1','Industry']].join(standardized_df)
    return data_df

def orthogonalize_data(data_df, target_col, factor_cols):
    data_df = data_df.copy()
    def orthogonalize_group(group):
        X = group[factor_cols]
        X = sm.add_constant(X)
        y = group[target_col]
        model = sm.OLS(y,X,missing='drop')
        result = model.fit()
        return y - result.predict(X)

    data_df[target_col] = data_df.groupby('dt').apply(orthogonalize_group).reset_index(level=0,drop=True)
    return data_df

def get_barra_factors(data_df):
    data_df['VALUE'] = 0.3 * data_df['BookToPrice'] + 0.6 * data_df['EarningsYield'] + 0.1 * data_df['LongTermReversal']
    data_df['SIZE'] = 0.1 * data_df['MidCapitalization'] + 0.9 * data_df['Size']
    data_df['MOMENTUM'] = data_df['Momentum']
    data_df['QUALITY'] = 0.125 * data_df['Leverage'] + 0.25 * data_df['InvestmentQuality'] + 0.125 * data_df['EarningsVariability'] + 0.25 * data_df['EarningsQuality'] + 0.25 * data_df['Profitability']
    data_df['YIELD'] = data_df['DividendYield']
    data_df['VOLATILITY'] = 0.6 * data_df['Beta'] + 0.4 * data_df['ResidualVolatility']
    data_df['GROWTH'] = data_df['Growth']
    data_df['LIQUIDITY'] = data_df['Liquidity']
    # 生成行业哑变量
    data_df = data_df.join(pd.get_dummies(data_df['sw_industry_code_1']))
    return data_df

start_date, end_date = 20160101, 20201231
start_date_ = int(s.tradingday(start_date,-250)[0]) #追溯到上一年/上个季度

# 读取Neptune基础样本数据
df_strategy_basic = IO.read_data([start_date, end_date], alt='/data/user/023859/factor_zooZZ/factor_lib/Basic_closed_hf_finish_20160101_20201231.h5')

# 读取基础样本申万行业
df_strategy_basic = get_sw_info(df_strategy_basic)

# 读取风险因子数据
risk_df = get_risk_data(start_date_, end_date)
df_strategy_basic = df_strategy_basic.join(risk_df.groupby('Ticker').shift(1))

# 填充缺失值
df_strategy_basic = fill_na_by_industry_median(df_strategy_basic)
df_strategy_basic = fill_na_by_all_median(df_strategy_basic)

# 标准化处理
df_strategy_basic = standardize_data(df_strategy_basic)

# 正交化处理
df_strategy_basic = orthogonalize_data(df_strategy_basic,target_col='ResidualVolatility', factor_cols=['Beta','Size'])
df_strategy_basic = orthogonalize_data(df_strategy_basic,target_col='LongTermReversal', factor_cols=['Momentum'])

# 加权得到barra大类因子
df_strategy_basic = get_barra_factors(df_strategy_basic)
df_strategy_basic.to_pickle('/dfs/user/023859/Neptune/df_neptune_basic_barra_%s_%s.pkl'%(start_date, end_date))