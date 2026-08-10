from multifactor.IO import IO
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import os
from SIF_Factor_Test3 import SIF_Factor_Test

# csvpath1 = '/data/user/015626/data/share/factor/factor_test/all_factor_test_20200619/all_factor_history2019/all_factor_history2019.csv'
# csvpath2 = '/data/user/015626/data/share/factor/factor_test/all_factor_test_20200619/all_factor_allhistory/all_factor_allhistory.csv'

# 根据因子测试结果筛选因子
def select_factors_from_stats(csvpath1, csvpath2, avg_bars_t = 5, rp_per_deal_t = 0.5, IC_t = 0.005,
                              self_corr_t = 0.75, sharpe_outsample_t = 0.4, sharpe_insample_t = 0.8):
    """
    :param csvpath1: 样本外因子测试结果（2019年）
    :param csvpath2: 样本内因子测试结果（全历史）
    :param avg_bars_t: 平均持仓时间阈值
    :param rp_per_deal_t: 每笔收益阈值
    :param IC_t: IC阈值
    :param self_corr_t: 自相关性阈值
    :param sharpe_outsample_t: 样本外夏普率阈值
    :param sharpe_insample_t: 样本内夏普率阈值
    :return: 符合要求的因子列表
    """
    def select_result_2019(csv):
        df = pd.read_csv(csv)
        df['avg_bars'] = (df.avg_long_bars + df.avg_short_bars) / 2
        df = df[df.avg_bars >= avg_bars_t]
        df = df[df.rp_per_deal >= rp_per_deal_t]
        df = df[df['IC-1min'] >= IC_t]
        df = df[df['self_corr-shift(5)'] >= self_corr_t]
        df = df[df['sharpe_Q3-Q0'] >= sharpe_outsample_t]
        return df

    def select_result_fullhistory(csv):
        df = pd.read_csv(csv)
        df['avg_bars'] = (df.avg_long_bars + df.avg_short_bars) / 2
        df = df[df.avg_bars >= avg_bars_t]
        df = df[df.rp_per_deal >= rp_per_deal_t]
        df = df[df['IC-1min'] >= IC_t]
        df = df[df['self_corr-shift(5)'] >= self_corr_t]
        df = df[df['sharpe_Q3-Q0'] >= sharpe_insample_t]
        return df

    df1 = select_result_2019(csvpath1)
    df2 = select_result_fullhistory(csvpath2)

    df1namelist = df1.factor_name.tolist()
    df2namelist = df2.factor_name.tolist()

    select_factors = list(set(df1namelist) & set(df2namelist))

    return select_factors

# a = select_factors_from_stats(csvpath1, csvpath2)
# print(len(a))
# print(a)
# exit()

# 从因子库中筛选低相关性因子, 需先使用get_factor_report得到所有因子报告的dataframe，存为csv后传入factor_report_csv_path参数
def filter_factors(library_path, factor_report_csv_path, factorslist=None, corr_threshold=0.95, start_time=20100101,
                   end_time=21000101):
    """
    :param library_path: 因子库路径
    :param factor_report_csv_path: 所有因子的测试结果汇总的csv
    :param factorslist: 需要特定筛选的因子列表，不传入则对因子库所有因子进行筛选
    :param corr_threshold: 筛选的相关性阈值
    :param start_time: 读取因子开始时间
    :param end_time: 读取因子结束时间
    :return: 筛选出的低相关性因子列表
    """
    if factorslist == None:
        alist = os.listdir(library_path)
        factorslist = [x[:-3] for x in alist]

    print('read all factors')
    fullfactors = pd.DataFrame()
    for x in factorslist:
        f = IO.read_data([start_time, end_time], alt=os.path.join(library_path, x + '.h5')).xs('IC.CFE', level=1)
        if len(fullfactors) == 0:
            fullfactors = f
        else:
            fullfactors = fullfactors.join(f)

    print('calculate corr between all factors')
    corrdf = pd.DataFrame()
    count = 0
    for i in range(len(factorslist) - 1):
        for j in range(i + 1, len(factorslist)):
            corrdf.loc[count, 'factor1'] = factorslist[i]
            corrdf.loc[count, 'factor2'] = factorslist[j]
            corrdf.loc[count, 'corr'] = fullfactors[factorslist[i]].corr(fullfactors[factorslist[j]])
            count += 1

    corrdf = corrdf.sort_values(by='corr', ascending=False)
    # corrdf.to_csv(
    #     '/data/user/015626/data/share/factor/factor_test/all_factor_test_20200619/select_factors_20200619_corr.csv',
    #     index=False)
    print('select high corr factors')
    bigcorr = corrdf[corrdf['corr'] > corr_threshold]
    if len(bigcorr) == 0:
        print('all factors are in low correlation')
        return
    bigcorrlist = list(set(bigcorr.factor1.tolist()) | set(bigcorr.factor2.tolist()))
    lowcorrlist = list(set(factorslist) - set(bigcorrlist))

    # 将相关性高的因子按夏普率从大到小排序
    all_factor_report = pd.read_csv(factor_report_csv_path)
    df2bigcorrdf = all_factor_report[all_factor_report.factor_name.isin(bigcorrlist)]
    df2bigcorrdf = df2bigcorrdf.sort_values(by='sharpe_Q3-Q0', ascending=False)

    waitlist = df2bigcorrdf.factor_name.tolist()

    print('start select factors whose correlation is high')
    inlist = []
    for x in waitlist:
        maxcorr = 0
        for y in lowcorrlist:
            corr = fullfactors[x].corr(fullfactors[y])
            maxcorr = max(maxcorr, corr)
        if maxcorr <= 0.95:
            lowcorrlist.append(x)
            inlist.append(x)

    print('finish!')
    return lowcorrlist

start_date = 20140101
end_date = 20200608

origindata = IO.read_data([start_date,end_date], columns = ['close'], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/MINUTE/MAIN/MD_CHINA_FUTURES_MINUTE_MAIN.h5')
origindata = origindata.xs('IC.CFE', level = 1)
origindata['return_points'] = origindata['close'].shift(-2) - origindata['close'].shift(-1)
origindata = origindata[['return_points']]

# 遍历因子库进行因子测试
def get_factor_report(rootpath, save_path, start_time = 20100101, end_time = 20210101, save_image = True):
    """
    :param rootpath: 因子库路径
    :param save_path: 因子测试结果图片保存的路径
    :param start_time: 读取因子开始时间
    :param end_time: 读取因子结束时间
    :param save_image: 是否保存因子结果图片
    :return: 所有因子测试结果的汇总dataframe
    """
    resultdf = pd.DataFrame()
    count = 0
    for x in os.listdir(rootpath):
        print(count)
        factorname = x[:-3]
        df = IO.read_data([start_time, end_time], alt=os.path.join(rootpath, x)).xs('IC.CFE', level=1)

        sif = SIF_Factor_Test(df.join(origindata, how='inner'), factorname, threshold=0.5, save_image=save_image,
                              show_image=False, starttime=start_time, endtime=end_time, signal_lims=(-1, 1),
                              savepath=save_path)
        stats = sif.draw_result()

        resultdf.loc[count, 'factor_name'] = factorname
        for key in stats.keys():
            resultdf.loc[count, key] = round(stats[key], 3)
        count += 1
    return resultdf

# rootpath = '/data/user/012398/data/alpha/CHINA_FUTURES/MINUTE/IC_all/'
# csvpath2 = '/data/user/015626/data/share/factor/factor_test/all_factor_test_20200619/all_factor_allhistory/all_factor_allhistory.csv'
# lowcorrlist = filter_factors(rootpath, csvpath2, factorslist=None, start_time=20190601, end_time=20200101)
# print(len(lowcorrlist))
# print(lowcorrlist)

# factorpath = '/data/user/012398/data/alpha/CHINA_FUTURES/MINUTE/IC_prod/'
# savepath='/data/user/015626/data/share/factor/factor_test/all_factor_test_20200619/IC_prod/'
# df = get_factor_report(factorpath, savepath, start_time = 20100101, end_time = 20210101, save_image = False)
