import pandas as pd
import numpy as np
import IO

df_ori = IO.read_data([20120101,20241231], alt='/data/group/800080/warehouseJG/prod/DATABASE/SUNTIME/DWD_EXP_FORECASTSECUDERIVED/DWD_EXP_FORECASTSECUDERIVED.h5')

raise
def cal_ul_price(pre_close_dataframe, ratio=0.1):
    pre_close_dataframe = pre_close_dataframe.reset_index()
    after_824 = pre_close_dataframe['dt'] >= pd.Timestamp('20200824')
    cyb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2] == '30')
    kcb = pre_close_dataframe['Ticker'].apply(lambda x: x[:2] == '68')
    pre_close_dataframe['ul_price'] = np.floor(
        pre_close_dataframe['pre_close'] * 100 * (1 + ratio) + 0.5) / 100
    pre_close_dataframe.loc[(after_824 & cyb) | kcb, 'ul_price'] = np.floor(
        pre_close_dataframe['pre_close'] * 100 * (1 + 2 * ratio) + 0.5) / 100
    return pre_close_dataframe.set_index(['dt', 'Ticker'])['ul_price']


df_ori['ul_price'] = cal_ul_price(df_ori, ratio=0.1)
df_ori['touch_zt'] = (df_ori['high'] >= df_ori['ul_price']).apply(int)
df_ori['is_zt'] = (df_ori['close'] == df_ori['ul_price']).apply(int)
df_ori['destroy'] = df_ori['touch_zt'] - df_ori['is_zt']


import pandas as pd
from sklearn.linear_model import LinearRegression
df = pd.DataFrame({
    'A': [1, 2, 3, 4, 5],
    'B': [10, 4, np.nan, 2, 1],
    'C': [5, 25, 30, 40, 60]
})
# 假设 df 是原始 DataFrame，包含列 A、B、C
X = df[['A', 'B']]  # 自变量：A、B
y = df['C']  # 因变量：C

# 拟合回归模型
model = LinearRegression(fit_intercept=True).fit(X, y)

# 计算残差
df['D'] = y - model.predict(X)
df