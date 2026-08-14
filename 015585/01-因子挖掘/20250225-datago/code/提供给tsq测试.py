import pandas as pd

df = pd.read_pickle('/data/user/015585/01-因子挖掘/20250225-datago/code/factor_股吧_全市场_20250228.pkl')
df = df.drop(['amt', 'pre_close', 'close', 'high', 'vwap', 'zt_price', 'is_trigger', 'is_zt', 'zcz', 'bj', 'label'], axis=1)

for col in df.columns:
    print(col)
    df[col] = df[col].unstack().shift(1).stack()

df.to_pickle('/data/user/015585/01-因子挖掘/999-share/for tsq/飞笛舆情测试/datago_guba_new.pkl')









