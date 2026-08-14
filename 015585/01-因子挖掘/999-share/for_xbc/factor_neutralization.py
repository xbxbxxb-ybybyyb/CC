import numpy as np
import pandas as pd

'''
选择因子
方案1：zt2max20
方案2：zt2max20,BA_emotion_diff_sqrt,Trick_sell_rate_10000,Total_uplift_strength
train：20160101-20200930
test：20201001-20210331
fit：20210401-20211231
'''
# 读取全部因子文件
path = '/data/user/015585/01-因子挖掘/20230811-因子中性化/file/eruopa_factor_20160101_20211231.pkl'
df_factor_ori = pd.read_pickle(path)
def get_max_one_ratio(factor_df):
    res = pd.DataFrame()
    import collections
    sample_number = len(factor_df)
    for col in factor_df:
        factor_value_distribution = np.array(list(collections.Counter(factor_df[col]).values()))
        factor_value_distribution.sort()
        max_same_number = factor_value_distribution[~0]
        max_same_ratio = max_same_number / sample_number
        res.loc[col,'max_same_ratio'] = max_same_ratio
    return res
df_max_same_ratio = get_max_one_ratio(df_factor_ori)
save_list = list(df_max_same_ratio[df_max_same_ratio['max_same_ratio'] > 0.5].index)

# 剔除因子异常值,3MAD法
def func_3mad_coef(x): # 返回系数
    xm = x.median()
    dmad = abs(x-xm).median()
    return [xm - 3*dmad,xm + 3*dmad]
df_factor_ori_train = df_factor_ori.loc[pd.Timestamp('20160101'):pd.Timestamp('20200930')]
df_factor_3mad_coef = {} # 储存3mad法根据训练集得到的上下界
for col in df_factor_ori_train:
    df_factor_3mad_coef[col] = func_3mad_coef(df_factor_ori_train[col])
def func_3mad(x,x_min,x_max):
    x[x>x_max] = x_max
    x[x<x_min] = x_min
    return x
df_factor_del_abn = pd.DataFrame()
for col in df_factor_ori:
    if col in save_list:
        df_factor_del_abn[col] = df_factor_ori[col]
    else:
        df_factor_del_abn[col] = func_3mad(df_factor_ori[col].copy(),
                                           df_factor_3mad_coef[col][0],
                                           df_factor_3mad_coef[col][1])
# 因子标准化
df_factor_standard_coef = {} # 储存训练集上的因子均值和标准差
df_factor_del_abn_train = df_factor_del_abn.loc[pd.Timestamp('20160101'):pd.Timestamp('20200930')]
for col in df_factor_del_abn_train:
    df_factor_standard_coef[col] = [df_factor_del_abn_train[col].mean(),df_factor_del_abn_train[col].std()]
df_factor_standard = pd.DataFrame()
for col in df_factor_standard_coef:
    factor_mean = df_factor_standard_coef[col][0]
    factor_std = df_factor_standard_coef[col][1]
    df_factor_standard[col] = (df_factor_del_abn[col] - factor_mean) / factor_std
df_factor_standard = df_factor_standard.drop(['label_pct'],axis=1) # label列剔除
# 因子中性化
dic_del_factor = {'sol1':['zt2max20'],
                  'sol2':['zt2max20','BA_emotion_diff_sqrt','Trick_sell_rate_10000',
                         'Total_uplift_strength']
                  }
from sklearn.linear_model import LinearRegression
LR = LinearRegression()
df_factor_standard_train = df_factor_standard.loc[pd.Timestamp('20160101'):pd.Timestamp('20200930')]
dic_lr_coef = {} # 两种方法的回归系数
for sol in dic_del_factor: # 对所有方案，在训练集上求中性化系数
    dic_lr_coef[sol] = {}
    list_del_factor = dic_del_factor[sol]
    x = df_factor_standard_train[list_del_factor]
    x = np.array(x).reshape([-1,1]) if len(list_del_factor) == 1 else x
    df_factor_standard_train_y = df_factor_standard_train.drop(list_del_factor,axis=1)
    for factor_y in df_factor_standard_train_y:
        y = df_factor_standard_train_y[factor_y]
        LR.fit(x, y)
        dic_lr_coef[sol][factor_y] = [LR.coef_,LR.intercept_]

dic_sol_df_factor_neutra = {}
for sol in dic_del_factor:
    df_factor_neutra = pd.DataFrame()
    for factor in dic_lr_coef[sol]:
        del1 = df_factor_standard[dic_del_factor[sol]] * dic_lr_coef[sol][factor][0] # 系数项部分
        del2 = dic_lr_coef[sol][factor][1] # 常数部分
        df_factor_neutra[factor] = df_factor_standard[factor].copy()
        for del_factor in dic_del_factor[sol]:
            df_factor_neutra[factor] = df_factor_neutra[factor] - del1[del_factor]
        df_factor_neutra[factor] = df_factor_neutra[factor] - del2
    # 加入剔除掉的因子（完成去极值和标准化）
    df_factor_neutra = pd.concat([df_factor_neutra,df_factor_standard[dic_del_factor[sol]]],axis=1)
    dic_sol_df_factor_neutra[sol] = df_factor_neutra
import pickle
def save_pickle(result_dic, save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(result_dic, input, protocol=pickle.HIGHEST_PROTOCOL)
save_pickle(dic_sol_df_factor_neutra,
            '/data/user/015585/01-因子挖掘/20230811-因子中性化/result/europa_neutralization_new.pkl')