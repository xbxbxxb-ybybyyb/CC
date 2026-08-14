# coding: utf-8
# Author：fengchi863
# Date ：2020/5/7 8:52

import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

# notes: 该行也可以直接用在plt绘图中，使用seaborn的绘图风格
font_path = 'data'
sns.set_style("whitegrid") # darkgrid, dark, white, ticks
fig_root_path = ''
myfont = matplotlib.font_manager.FontProperties(fname='msyh.ttf')

'''
绘制单个bar的直方图
'''
def plot_single_hist():
    pass

'''
绘制多个bar的直方图
'''
def plot_multi_hist():
    pass

'''
绘制直方图和概率密度曲线，可选择是否加阴影效果
'''
def plot_kde_hist(target_list):
    # 开始绘图
    fig, ax = plt.subplots(figsize=(16, 9))
    # 方法一：使用matplotlib
    # plt.hist(corr_list, bins=100)
    # 方法二：使用seaborn
    ax.hist(target_list, bins=100, histtype="stepfilled", normed=True, alpha=0.6)
    sns.kdeplot(target_list, shade=True)
    plt.title('217个交易日以来%s与%s的相关性频率分布图', fontproperties=myfont, fontsize=18)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlabel('相关性系数', fontproperties=myfont, fontsize=16)
    plt.ylabel('频率', fontproperties=myfont, fontsize=16)
    plt.show()

'''
使用pandas绘制折线图
'''
def plot_line_use_pandas():
    pass

'''
使用plt绘制折线图
'''
def plot_line_use_plt():
    pass

'''
绘制箱体图，使用dataframe，将每一列的数字进行绘制
'''
def plot_box(data):
    sns.boxplot(data=data)

'''
绘制小提琴图，使用dataframe，将每一列的数字进行绘制
'''
def plot_violin(data):
    sns.violinplot(data=data)


'''
绘制热力图，data为因子矩阵
'''
def plot_heatmap(data):
    fig, ax = plt.subplots(figsize=(12, 12), dpi=20)
    corr = data.corr()
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    sns.heatmap(corr, xticklabels=corr.columns.values, yticklabels=corr.columns.values, annot=True, center=0,
                cmap='rainbow')
    for xtick in ax.get_xticklabels():
        xtick.set_font_properties(myfont)
    for ytick in ax.get_yticklabels():
        ytick.set_font_properties(myfont)
    #     plt.show()
    fig.savefig(fig_root_path + 'corr/corr_fig.jpg', bbox_inches='tight')

'''
for循环绘制图像
'''
def plot_multi_fig():
    watch_num_list = [1, 3, 5, 10]
    n = 1
    fig, ax = plt.subplots(figsize=(16, 9))

    for watch1_num in watch_num_list:
        corr_list = []
        year_list = [2018, 2019]
        watch1 = '所在行业%d日超额' % (watch1_num)
        watch2 = '委托时在行业内的超额分位数'
        for year in year_list:
            result = pd.read_excel('result_20200312_%d.xlsx' % year, index_col=0)
            for date in set(result['委托日期'].tolist()):
                daily_info = result.loc[result['委托日期'] == date]
                daily_info = daily_info.loc[daily_info['买卖方向'] == deal_flag]
                industry_alpha_corr_stock_alpha = daily_info.drop(['申万一级行业代码'], axis=1)
                corr = industry_alpha_corr_stock_alpha.corr()
                corr_list.append(corr.loc[watch1, watch2])

        # 开始绘图
        plt.subplot(2, 2, n)
        plt.hist(corr_list, bins=100, histtype="stepfilled", normed=True, alpha=0.6)
        sns.kdeplot(corr_list, shade=True)
        n += 1
        plt.title('%s与%s\n的相关性频率分布图' % (watch1, watch2), fontproperties=myfont, fontsize=12)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.xlabel('相关性系数, corr: %.3f' % np.mean(corr_list), fontproperties=myfont, fontsize=12)
        plt.ylabel('频率', fontproperties=myfont, fontsize=12)

    plt.subplots_adjust(hspace=0.45)  # 调整子图间距
    plt.show()