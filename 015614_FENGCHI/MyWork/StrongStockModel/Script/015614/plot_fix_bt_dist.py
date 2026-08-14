# coding: utf-8
# Author：fengchi863
# Date ：2020/8/18 15:55

'''
此文件作废，见jupyter目录下
'''

from StrongStockModel.conf.path_config import root_path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

sns.set_style("whitegrid") # darkgrid, dark, white, ticks
fig_root_path = '/data/user/fengchi/MyWork/MyTest/msyh.ttf'
myfont = matplotlib.font_manager.FontProperties(fname=fig_root_path)

def plot_kde_hist(target_list):
    # 开始绘图
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.hist(target_list, bins=100, histtype="stepfilled", normed=True, alpha=0.6)
    sns.kdeplot(target_list, shade=True)
    plt.title('217个交易日以来%s与%s的相关性频率分布图', fontproperties=myfont, fontsize=18)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlabel('相关性系数', fontproperties=myfont, fontsize=16)
    plt.ylabel('频率', fontproperties=myfont, fontsize=16)
    plt.show()

data = pd.read_excel(root_path + 'stats_fix.xlsx', index_col=0)
ic = data['ic'].tolist()
plot_kde_hist(ic)