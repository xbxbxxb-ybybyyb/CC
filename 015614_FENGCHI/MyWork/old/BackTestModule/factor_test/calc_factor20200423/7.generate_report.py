# coding: utf-8
# Author：fengchi863
# Date ：2020/4/29 14:40

import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import seaborn as sns
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

date = str(20200428)
all_result_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_%s/' % date
top_n_result_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/bt_top_n_%s/' % date
combine_result_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/bt_combine_factor_%s/' % date
all_result_description_file = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/因子全量测试专用.xlsx'
top_n_factor_manual_file = all_result_path + '因子组合-topN对应表.xlsx'
combine_factor_manual_file = all_result_path + '因子组合-全组合对应表.xlsx'

def plot_diff_turnover():
    '''
    统计不同换手率的走势
    '''
    # ax, fig = plt.subplot(figsize=(16,9))
    # 拼接三份换手率下的结果
    df1 = pd.read_excel(all_result_path + '日内因子净值回测结果(%s全量)_(0.1, 200, 400).xlsx' % date, sheet_name='全量测试结果', index_col=0)
    df2 = pd.read_excel(all_result_path + '日内因子净值回测结果(%s全量)_(0.3, 200, 400).xlsx' % date, sheet_name='全量测试结果', index_col=0)
    df3 = pd.read_excel(all_result_path + '日内因子净值回测结果(%s全量)_(0.5, 200, 400).xlsx' % date, sheet_name='全量测试结果', index_col=0)
    df_desc = pd.read_excel(all_result_description_file, index_col=0)
    df = pd.concat([df_desc, df1['累计收益率'], df2['累计收益率'], df3['累计收益率']], axis=1)
    df.columns = df.columns.tolist()[:-3] + ['0.1', '0.3', '0.5']
    df.set_index('因子名称', inplace=True)
    df['0.1'].plot()
    plt.show()
    print(mpl.get_backend())

if __name__ == '__main__':
    plot_diff_turnover()


