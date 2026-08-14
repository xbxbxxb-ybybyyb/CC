# coding: utf-8
# Author：fengchi863
# Date ：2020/5/13 14:28

import pandas as pd, numpy as np
import matplotlib as mpl
import seaborn as sns
import statsmodels.api as sm

sns.set(style="whitegrid", palette="muted", color_codes=True)
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os

myfont = mpl.font_manager.FontProperties(fname='/data/user/fengchi/ZCZY/msyh.ttf')

factor_root_path = '/data/group/800319/storeFactor/original_intrafactor/'
plot_output_path = '/data/group/800319/fengchi/factor_distribution/'
factor_name_list = sorted([os.path.splitext(x)[0] for x in os.listdir(factor_root_path)])

factor_distribution = pd.DataFrame(index=factor_name_list, columns=['first_time', 'end_time', 'max', 'min'])

for factor_name in factor_name_list:
    # factor_name = factor_name_list[0]
    # factor_name = 'boll1'
    print(factor_name)
    factor = pd.read_hdf(factor_root_path + factor_name + '.h5', factor_name)  # (242*731, 2404)

    ref_factor = factor.iloc[242:242 * 2, 0].isnull()[factor.iloc[242:242 * 2, 0].isnull() == False]

    _, first_not_nan = ref_factor.index[0]
    _, last_not_nan = ref_factor.index[-1]

    factor_array = factor.iloc[:2000].values.reshape(-1)
    factor_array = factor_array[~pd.isnull(factor_array) & ~np.isinf(factor_array)]

    fig, axes = plt.subplots(2, 2, figsize=(16, 9))
    sns.distplot(factor_array, hist=True, color="r", kde_kws={"shade": True}, ax=axes[0][0])
    plt.title('%s\n最开始有值的时间: %d\n最后有值的时间:%d' % (factor_name, first_not_nan, last_not_nan), \
              fontproperties=myfont, fontsize=14)
    sns.boxplot(y=factor_array, dodge=False, width=1, fliersize=3, ax=axes[0][1])
    sm.qqplot(factor_array, line='s', ax=axes[1][0])
    plt.savefig(plot_output_path + '%s.jpg' % factor_name, bbox_inches='tight')

    factor_distribution.loc[factor_name, 'max'] = max(factor_array)
    factor_distribution.loc[factor_name, 'min'] = min(factor_array)
    factor_distribution.loc[factor_name, 'first_time'] = first_not_nan
    factor_distribution.loc[factor_name, 'end_time'] = last_not_nan

factor_distribution.to_excel(plot_output_path + '因子描述表格.xlsx')
