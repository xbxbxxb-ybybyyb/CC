from multifactor.IO import IO
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import os

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
        f = IO.read_data([start_time, end_time], alt=os.path.join(rootpath, x + '.h5')).xs('IC.CFE', level=1)
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
    return lowcorrlist, bigcorrlist