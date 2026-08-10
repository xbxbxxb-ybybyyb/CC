import matplotlib
matplotlib.use('Agg')
import json,datetime,os,glob
import pandas as pd
import numpy as np
from pandas.plotting import  table
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
# 计算策略评价指标
import itertools

def kzz_evaluate(pnl):
    """
    :param trade: 每笔交易的df
    :return:
    """

    # ===新建一个dataframe保存回测指标
    results = pd.DataFrame()

    win_ratio = len(pnl[pnl >= 0]) / len(pnl) # 胜率
    wl_ratio = pnl[pnl >= 0].mean() / abs(pnl[pnl < 0].mean()) # 盈亏比
    kelly = (wl_ratio * win_ratio - (1 - win_ratio)) / wl_ratio
    
    pnl = pnl.to_frame()
    pnl.columns = ['change']
    pnl['equity_curve'] = pnl['change'].cumsum() + 1
    pnl = pnl.reset_index()
    # ===计算累积净值
    results.loc[0, 'Accunulative Net'] = round(pnl['equity_curve'].iloc[-1], 3)

    # 计算夏普比率
    pnl['date'] = pnl['dt'].apply(lambda x: x.date())
    sharpedailyreturn = pnl.groupby('date')['change'].sum().to_frame()
    tradedays = len(sharpedailyreturn)
    sharpe_ratio = round(sharpedailyreturn['change'].mean() / sharpedailyreturn['change'].std() * np.sqrt(252), 3)
    results.loc[0, 'Sharpe Ratio'] = sharpe_ratio

    # ===计算年化收益
    annual_return = (pnl['equity_curve'].iloc[-1] / pnl['equity_curve'].iloc[0] - 1) * (
            '365 days 00:00:00' / (pnl['dt'].iloc[-1] - pnl['dt'].iloc[0]))

    results.loc[0, 'Annual Return'] = format(round(annual_return, 3), '.2%')

    sharpedailyreturn['equity_curve'] = sharpedailyreturn['change'].cumsum()
    sharpedailyreturn = sharpedailyreturn.reset_index()
    # ===计算最大回撤
    # 计算当日之前的资金曲线的最高点
    sharpedailyreturn['max2here'] = sharpedailyreturn['equity_curve'].expanding().max()
    # 计算到历史最高值到当日的跌幅，drowdwon
    sharpedailyreturn['dd2here'] = sharpedailyreturn['equity_curve'] - sharpedailyreturn['max2here']
    # 计算最大回撤，以及最大回撤结束时间
    end_date, max_draw_down = tuple(sharpedailyreturn.sort_values(by=['dd2here']).iloc[0][['date', 'dd2here']])
    # 计算最大回撤开始时间
    start_date = sharpedailyreturn[sharpedailyreturn['date'] <= end_date].sort_values(by='equity_curve', ascending=False).iloc[0][
        'date']
    # 将无关的变量删除
    sharpedailyreturn.drop(['max2here', 'dd2here'], axis=1, inplace=True)
    sharpedailyreturn = sharpedailyreturn.set_index('date')
    results.loc[0, 'Max Drawdown'] = format(max_draw_down, '.2%')
    results.loc[0, 'MDD starttime'] = str(start_date)
    results.loc[0, 'MDD endtime'] = str(end_date)

    # ===年化收益/回撤比
    results.loc[0, 'Calmar Ratio'] = round(abs(annual_return / max_draw_down), 2)

    results.loc[0, 'Win Ratio'] = round(win_ratio, 2)
    results.loc[0, 'WinLoss Ratio'] = round(wl_ratio, 2)
    results.loc[0, 'Kelly'] = round(kelly, 2)

    # ===连续盈利亏算
    results.loc[0, 'Max Num Cons Profit'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(pnl['change'] > 0, 1, np.nan))])  # 最大连续盈利笔数
    results.loc[0, 'Max Num Cons Loss'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(pnl['change'] < 0, 1, np.nan))])  # 最大连续亏损笔数

    results = results.T
    results.columns = ['num']
    return results

def get_something(some_ret):
    winratio = round(len(some_ret[some_ret>0]) / len(some_ret),3)
    plratio = round(some_ret[some_ret>0].mean() / some_ret[some_ret<0].mean() * -1, 3)
    r = pd.DataFrame()
    r.loc['Win Ratio','num'] = winratio
    r.loc['Profit Loss Ratio','num'] = plratio
    return r

def layer_chopper(ps_raw, layers, rank=True):
    # return pd.Series with categorical tags representing bins to which raw data has been assigned
    # use rank to ensure that each bin contains equal numbers of samples at best situation
    if isinstance(layers, int):
        _labels = range(layers)
    else:
        _labels = range(len(layers) - 1)
    if rank:
        return pd.cut(ps_raw.rank(), layers, retbins=False, labels=_labels)
    else:
        return pd.cut(ps_raw, layers, retbins=False, labels=_labels)
        
def ts_segment_test( ps_raw, ps_return, layers, layer_lims=None, normalize=False,
                        return_segment_time_series=False,
                        **kwargs):
    assert isinstance(ps_raw, pd.Series)
    assert isinstance(ps_return, pd.Series)
    if layer_lims is not None:
        _up, _down = max(layer_lims), min(layer_lims)
        bins = [i for i in np.arange(_down, _up, (_up - _down) / layers)]
        bins[0] = -np.inf
        bins.append(np.inf)
        ps_bin = layer_chopper(ps_raw, layers=bins, rank=False)
    else:
        ps_bin = layer_chopper(ps_raw, layers=layers, rank=False)
    ps_bin.name = 'bins'
    ps_return.name = ps_return.name if ps_return.name is not None else 'return'
    _magic = pd.DataFrame(ps_bin).merge(pd.DataFrame(ps_return), how='left', left_index=True,
                                        right_index=True).dropna()
    if not return_segment_time_series:
        pd_res = _magic.groupby('bins').mean()
        pd_res.index = ['Q' + str(int(col)) for col in pd_res.index]
        return pd_res, _magic
    else:
        segment_dict = dict()
        for nbin, group in _magic.groupby('bins'):
            _ = group[ps_return.name]
            _.name = 'Q' + str(nbin)
            segment_dict[_.name] = _
        return segment_dict

def median_filter(factor_pd, mad=3, winsor=False, inplace=False):
    if not inplace:
        factor_pd = factor_pd.copy()
    dm = factor_pd.median(axis=1)
    # caution of symmetric uppper & lower bounds
    dist_dm = (factor_pd.subtract(dm, axis=0)).abs().median(axis=1)
    date_num, stock_num = factor_pd.shape
    fac_ub = pd.DataFrame(np.tile(dm + mad * dist_dm, [stock_num, 1]).T, index=factor_pd.index,
                          columns=factor_pd.columns)
    fac_lb = pd.DataFrame(np.tile(dm - mad * dist_dm, [stock_num, 1]).T, index=factor_pd.index,
                          columns=factor_pd.columns)
    if winsor:
        factor_pd[factor_pd > fac_ub] = np.nan
        factor_pd[factor_pd < fac_lb] = np.nan
    else:
        factor_pd[factor_pd > fac_ub] = fac_ub
        factor_pd[factor_pd < fac_lb] = fac_lb
    return factor_pd

def test_kzz_overnight_super(factor, y = None, universe = None, factor_name = None, seg_num = 5, select_topnum = 30,up_quantile = 0.05, down_quantile = 0.95, 
                             isrank = True, layer_lims = None,  save_path=None, save_image = False, show_image = False):
    # is_rank本来默认为false
    assert y is not None 
    assert universe is not None
    ref_score = factor.copy()
    ref_score.index.names = ['dt','Ticker']
    # ref_score = median_filter(ref_score.unstack(), mad = 3).stack()
    ref_score = ref_score.reindex(ref_score.index & y.index).sort_index()
    temp_ref = ref_score.reindex(ref_score.index & universe.index).sort_index()
    temp_y = y.reindex(temp_ref.index) 
    IC = round(temp_ref.corr(temp_y), 3)

    y_copy = y.reindex(ref_score.index)
    # IC = round(ref_score.unstack().corrwith(y_copy.unstack(), axis = 1).mean(), 3)
    if isrank == True:
        ref_score = ref_score.unstack().rank(axis = 1, pct = True).stack()
        up_quantile = 0
        down_quantile = 1
    if layer_lims is None:
        layer_lims = [ref_score.quantile(up_quantile), ref_score.quantile(down_quantile)]
    seg = ts_segment_test(ref_score, y_copy, seg_num, layer_lims, return_segment_time_series=True)
    seg = pd.DataFrame(seg)
    _ = seg.groupby(pd.Grouper(level=0))
    profit_pergroup = _.mean().cumsum()
    
    # 选出全样本最强的多少个最差的多少个
    topn = ref_score.groupby(ref_score.index.get_level_values(0)).nlargest(select_topnum).reset_index(level = 0, drop = True)
    botn = ref_score.groupby(ref_score.index.get_level_values(0)).nsmallest(select_topnum).reset_index(level = 0, drop = True)
    topy = y.reindex(y.index & topn.index).sort_index()
    boty = y.reindex(y.index & botn.index).sort_index()
    topy_daily = topy.groupby(topy.index.get_level_values(0)).mean()
    boty_daily = boty.groupby(boty.index.get_level_values(0)).mean()
    select_y = pd.concat([topy_daily.cumsum(),boty_daily.cumsum()], axis = 1)
    select_y.columns = ['top_%d' % select_topnum, 'bottom_%d' % select_topnum]
    
    ref_score_univ = ref_score.reindex(ref_score.index & universe.index).sort_index()
    y_univ = y.reindex(ref_score_univ.index)
    ref_score_univ = ref_score_univ.unstack().rank(axis = 1, pct = True).stack()
    seg_univ = ts_segment_test(ref_score_univ, y_univ, seg_num, layer_lims, return_segment_time_series=True)
    seg_univ = pd.DataFrame(seg_univ)
    _ = seg_univ.groupby(pd.Grouper(level=0))
    profit_pergroup_univ = _.mean().cumsum()
    
    topn_univ = ref_score_univ.groupby(ref_score_univ.index.get_level_values(0)).nlargest(select_topnum).reset_index(level = 0, drop = True)
    botn_univ = ref_score_univ.groupby(ref_score_univ.index.get_level_values(0)).nsmallest(select_topnum).reset_index(level = 0, drop = True)
    topy_univ = y_univ.reindex(y_univ.index & topn_univ.index).sort_index()
    boty_univ = y_univ.reindex(y_univ.index & botn_univ.index).sort_index()
    topy_daily_univ = topy_univ.groupby(topy_univ.index.get_level_values(0)).mean()
    boty_daily_univ = boty_univ.groupby(boty_univ.index.get_level_values(0)).mean()
    select_y_univ = pd.concat([topy_daily_univ.cumsum(),boty_daily_univ.cumsum()], axis = 1)
    select_y_univ.columns = ['top_%d' % select_topnum, 'bottom_%d' % select_topnum]

    result = pd.concat([kzz_evaluate(topy_daily),kzz_evaluate(boty_daily),kzz_evaluate(topy_daily_univ),kzz_evaluate(boty_daily_univ)], axis = 1)
    result.columns = ['full_top_%d' % select_topnum, 'full_bottom_%d' % select_topnum, 'univ_top_%d' % select_topnum, 'univ_bottom_%d' % select_topnum]
    
    result2 = pd.concat([get_something(topy),get_something(boty),get_something(topy_univ),get_something(boty_univ)], axis = 1)
    result2.columns = ['full_top_%d' % select_topnum, 'full_bottom_%d' % select_topnum, 'univ_top_%d' % select_topnum, 'univ_bottom_%d' % select_topnum]
    
    result = result.append(result2)

    fig = plt.figure(figsize=(15, 20), dpi = 200)

    ax = fig.add_subplot(5, 1, 1)
    plt.text(0.2, 1.2, factor_name, fontsize=28)
    plt.text(0.7, 1.2, 'IC: %s' % str(IC), fontsize=18)
    plt.text(0.1, 1.1, 'full_top_%d_winratio: ' % select_topnum + str(result.loc['Win Ratio', 'full_top_%d' % select_topnum]), fontsize=18)
    plt.text(0.5, 1.1, 'full_top_%d_plratio: ' % select_topnum + str(result.loc['Profit Loss Ratio', 'full_top_%d' % select_topnum]), fontsize=18)
    plt.text(0.1, 1.0, 'univ_top_%d_winratio: ' % select_topnum + str(result.loc['Win Ratio', 'univ_top_%d' % select_topnum]), fontsize=18)
    plt.text(0.5, 1.0, 'univ_top_%d_plratio: ' % select_topnum + str(result.loc['Profit Loss Ratio', 'univ_top_%d' % select_topnum]), fontsize=18)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    table(ax, result, loc='center')
    plt.subplots_adjust(top=0.95, hspace=0.3)

    # 图：全样本分组
    ax2 = fig.add_subplot(5, 1, 2)
    profit_pergroup.plot(ax=ax2, legend=True)
    # ax2.plot(profit_pergroup)
    plt.title('full sample segment', fontsize='large')
    plt.xlabel('Date', fontsize='medium')
    plt.ylabel('Cumulative Ret', fontsize='medium')
    plt.subplots_adjust(top=0.95, hspace=0.3)

    # 图：全样本top
    ax2 = fig.add_subplot(5, 1, 3)
    select_y['top_%d' % select_topnum].plot(ax=ax2, legend=False)
    # ax2.plot(select_y['top_%d' % select_topnum])
    plt.title('full sample top %d' % select_topnum, fontsize='large')
    plt.xlabel('Date', fontsize='medium')
    plt.ylabel('Top Cumulative Ret', fontsize='medium')
    color = 'tab:orange'
    ax3 = ax2.twinx()
    select_y['bottom_%d' % select_topnum].plot(ax=ax3, legend=False, color = color)
    # ax3.plot(select_y.index.tolist(), select_y['bottom_%d' % select_topnum].values, color = color)
    ax3.tick_params(axis = 'y', labelcolor = color)
    ax3.set_ylabel('Bottom Cumulative Ret', color = color)
    plt.subplots_adjust(top=0.95, hspace=0.3)

    # 图：univ分组
    ax2 = fig.add_subplot(5, 1, 4)
    profit_pergroup_univ.plot(ax=ax2, legend=True)
    # ax2.plot(profit_pergroup_univ)
    plt.title('univ sample segment', fontsize='large')
    plt.xlabel('Date', fontsize='medium')
    plt.ylabel('Cumulative Ret', fontsize='medium')
    plt.subplots_adjust(top=0.95, hspace=0.3)

    # 图：univ top
    ax2 = fig.add_subplot(5, 1, 5)
    select_y_univ['top_%d' % select_topnum].plot(ax=ax2, legend=False)
    # ax2.plot(select_y_univ['top_%d' % select_topnum])
    plt.title('univ sample top %d' % select_topnum, fontsize='large')
    plt.xlabel('Date', fontsize='medium')
    plt.ylabel('Top Cumulative Ret', fontsize='medium')
    color = 'tab:orange'
    ax3 = ax2.twinx()
    select_y_univ['bottom_%d' % select_topnum].plot(ax=ax3, legend=False, color = color)
    # ax3.plot(select_y_univ.index.tolist(), select_y_univ['bottom_%d' % select_topnum].values, color = color)
    ax3.tick_params(axis = 'y', labelcolor = color)
    ax3.set_ylabel('Bottom Cumulative Ret', color = color)
    plt.subplots_adjust(top=0.95, hspace=0.3)

    if save_image:
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        plt.savefig(os.path.join(save_path, factor_name + '.png'), format='png')  # 存储图片
    if show_image:
        plt.show()
    plt.close()
    
    result = result.unstack().to_frame().T
    result.index = [factor_name]
    # result.index.name = 'factor_name'
    result.columns = [result.columns.map('{0[1]}_{0[0]}'.format)]
    result['IC'] = IC
    # 调整列的顺序
    univ_top_list = ['IC']
    res_list = []
    for x in result.columns.tolist():
        x = x[0]
        if x == 'IC':
            continue
        elif 'univ_top' in x:
            univ_top_list.append(x)
        else:
            res_list.append(x)
    result = result[univ_top_list + res_list]

    r = result.T
    ind = [x[0] for x in r.index.tolist()]
    value = r[r.columns[0]].tolist()
    result = dict(zip(ind, value))
    result['factor_name'] = r.columns[0]

    return result, topy, topy_univ

def test_kzz_overnight_ratio(factor, y = None, universe = None, factor_name = None, seg_num = 5, select_topnum = 0.7,up_quantile = 0.05, down_quantile = 0.95, 
                             isrank = True, layer_lims = None,  save_path=None, save_image = False, show_image = False):
    # is_rank本来默认为false
    assert y is not None 
    assert universe is not None
    ref_score = factor.copy()
    ref_score.index.names = ['dt','Ticker']
    # ref_score = median_filter(ref_score.unstack(), mad = 3).stack()
    ref_score = ref_score.reindex(ref_score.index & y.index).sort_index()
    temp_ref = ref_score.reindex(ref_score.index & universe.index).sort_index()
    temp_y = y.reindex(temp_ref.index) 
    IC = round(temp_ref.corr(temp_y), 3)

    y_copy = y.reindex(ref_score.index)
    # IC = round(ref_score.unstack().corrwith(y_copy.unstack(), axis = 1).mean(), 3)
    if isrank == True:
        ref_score = ref_score.unstack().rank(axis = 1, pct = True).stack()
        up_quantile = 0
        down_quantile = 1
    if layer_lims is None:
        layer_lims = [ref_score.quantile(up_quantile), ref_score.quantile(down_quantile)]
    seg = ts_segment_test(ref_score, y_copy, seg_num, layer_lims, return_segment_time_series=True)
    seg = pd.DataFrame(seg)
    _ = seg.groupby(pd.Grouper(level=0))
    profit_pergroup = _.mean().cumsum()
    
    # 选出全样本最强的多少个最差的多少个
    topn = ref_score.groupby(ref_score.index.get_level_values(0)).apply(lambda x:x[x>=x.quantile(select_topnum)]).reset_index(level = 0, drop = True)
    botn = ref_score.groupby(ref_score.index.get_level_values(0)).apply(lambda x:x[x<=x.quantile(1 - select_topnum)]).reset_index(level = 0, drop = True)
    # topn = ref_score.groupby(ref_score.index.get_level_values(0)).nlargest(select_topnum).reset_index(level = 0, drop = True)
    # botn = ref_score.groupby(ref_score.index.get_level_values(0)).nsmallest(select_topnum).reset_index(level = 0, drop = True)
    topy = y.reindex(y.index & topn.index).sort_index()
    boty = y.reindex(y.index & botn.index).sort_index()
    topy_daily = topy.groupby(topy.index.get_level_values(0)).mean()
    boty_daily = boty.groupby(boty.index.get_level_values(0)).mean()
    select_y = pd.concat([topy_daily.cumsum(),boty_daily.cumsum()], axis = 1)
    select_y.columns = ['top_%d' % select_topnum, 'bottom_%d' % select_topnum]
    
    ref_score_univ = ref_score.reindex(ref_score.index & universe.index).sort_index()
    y_univ = y.reindex(ref_score_univ.index)
    ref_score_univ = ref_score_univ.unstack().rank(axis = 1, pct = True).stack()
    seg_univ = ts_segment_test(ref_score_univ, y_univ, seg_num, layer_lims, return_segment_time_series=True)
    seg_univ = pd.DataFrame(seg_univ)
    _ = seg_univ.groupby(pd.Grouper(level=0))
    profit_pergroup_univ = _.mean().cumsum()
    
    topn_univ = ref_score_univ.groupby(ref_score_univ.index.get_level_values(0)).apply(lambda x:x[x>=x.quantile(select_topnum)]).reset_index(level = 0, drop = True)
    botn_univ = ref_score_univ.groupby(ref_score_univ.index.get_level_values(0)).apply(lambda x:x[x<=x.quantile(1 - select_topnum)]).reset_index(level = 0, drop = True)
    # topn_univ = ref_score_univ.groupby(ref_score_univ.index.get_level_values(0)).nlargest(select_topnum).reset_index(level = 0, drop = True)
    # botn_univ = ref_score_univ.groupby(ref_score_univ.index.get_level_values(0)).nsmallest(select_topnum).reset_index(level = 0, drop = True)
    topy_univ = y_univ.reindex(y_univ.index & topn_univ.index).sort_index()
    boty_univ = y_univ.reindex(y_univ.index & botn_univ.index).sort_index()
    topy_daily_univ = topy_univ.groupby(topy_univ.index.get_level_values(0)).mean()
    boty_daily_univ = boty_univ.groupby(boty_univ.index.get_level_values(0)).mean()
    select_y_univ = pd.concat([topy_daily_univ.cumsum(),boty_daily_univ.cumsum()], axis = 1)
    select_y_univ.columns = ['top_%d' % select_topnum, 'bottom_%d' % select_topnum]

    result = pd.concat([kzz_evaluate(topy_daily),kzz_evaluate(boty_daily),kzz_evaluate(topy_daily_univ),kzz_evaluate(boty_daily_univ)], axis = 1)
    result.columns = ['full_top_%d' % select_topnum, 'full_bottom_%d' % select_topnum, 'univ_top_%d' % select_topnum, 'univ_bottom_%d' % select_topnum]
    
    result2 = pd.concat([get_something(topy),get_something(boty),get_something(topy_univ),get_something(boty_univ)], axis = 1)
    result2.columns = ['full_top_%d' % select_topnum, 'full_bottom_%d' % select_topnum, 'univ_top_%d' % select_topnum, 'univ_bottom_%d' % select_topnum]
    
    result = result.append(result2)

    fig = plt.figure(figsize=(15, 20), dpi = 200)

    ax = fig.add_subplot(5, 1, 1)
    plt.text(0.2, 1.2, factor_name, fontsize=28)
    plt.text(0.7, 1.2, 'IC: %s' % str(IC), fontsize=18)
    plt.text(0.1, 1.1, 'full_top_%d_winratio: ' % select_topnum + str(result.loc['Win Ratio', 'full_top_%d' % select_topnum]), fontsize=18)
    plt.text(0.5, 1.1, 'full_top_%d_plratio: ' % select_topnum + str(result.loc['Profit Loss Ratio', 'full_top_%d' % select_topnum]), fontsize=18)
    plt.text(0.1, 1.0, 'univ_top_%d_winratio: ' % select_topnum + str(result.loc['Win Ratio', 'univ_top_%d' % select_topnum]), fontsize=18)
    plt.text(0.5, 1.0, 'univ_top_%d_plratio: ' % select_topnum + str(result.loc['Profit Loss Ratio', 'univ_top_%d' % select_topnum]), fontsize=18)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    table(ax, result, loc='center')
    plt.subplots_adjust(top=0.95, hspace=0.3)

    # 图：全样本分组
    ax2 = fig.add_subplot(5, 1, 2)
    profit_pergroup.plot(ax=ax2, legend=True)
    # ax2.plot(profit_pergroup)
    plt.title('full sample segment', fontsize='large')
    plt.xlabel('Date', fontsize='medium')
    plt.ylabel('Cumulative Ret', fontsize='medium')
    plt.subplots_adjust(top=0.95, hspace=0.3)

    # 图：全样本top
    ax2 = fig.add_subplot(5, 1, 3)
    select_y['top_%d' % select_topnum].plot(ax=ax2, legend=False)
    # ax2.plot(select_y['top_%d' % select_topnum])
    plt.title('full sample top %d' % select_topnum, fontsize='large')
    plt.xlabel('Date', fontsize='medium')
    plt.ylabel('Top Cumulative Ret', fontsize='medium')
    color = 'tab:orange'
    ax3 = ax2.twinx()
    select_y['bottom_%d' % select_topnum].plot(ax=ax3, legend=False, color = color)
    # ax3.plot(select_y.index.tolist(), select_y['bottom_%d' % select_topnum].values, color = color)
    ax3.tick_params(axis = 'y', labelcolor = color)
    ax3.set_ylabel('Bottom Cumulative Ret', color = color)
    plt.subplots_adjust(top=0.95, hspace=0.3)

    # 图：univ分组
    ax2 = fig.add_subplot(5, 1, 4)
    profit_pergroup_univ.plot(ax=ax2, legend=True)
    # ax2.plot(profit_pergroup_univ)
    plt.title('univ sample segment', fontsize='large')
    plt.xlabel('Date', fontsize='medium')
    plt.ylabel('Cumulative Ret', fontsize='medium')
    plt.subplots_adjust(top=0.95, hspace=0.3)

    # 图：univ top
    ax2 = fig.add_subplot(5, 1, 5)
    select_y_univ['top_%d' % select_topnum].plot(ax=ax2, legend=False)
    # ax2.plot(select_y_univ['top_%d' % select_topnum])
    plt.title('univ sample top %d' % select_topnum, fontsize='large')
    plt.xlabel('Date', fontsize='medium')
    plt.ylabel('Top Cumulative Ret', fontsize='medium')
    color = 'tab:orange'
    ax3 = ax2.twinx()
    select_y_univ['bottom_%d' % select_topnum].plot(ax=ax3, legend=False, color = color)
    # ax3.plot(select_y_univ.index.tolist(), select_y_univ['bottom_%d' % select_topnum].values, color = color)
    ax3.tick_params(axis = 'y', labelcolor = color)
    ax3.set_ylabel('Bottom Cumulative Ret', color = color)
    plt.subplots_adjust(top=0.95, hspace=0.3)

    if save_image:
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        plt.savefig(os.path.join(save_path, factor_name + '.png'), format='png')  # 存储图片
    if show_image:
        plt.show()
    plt.close()
    
    result = result.unstack().to_frame().T
    result.index = [factor_name]
    # result.index.name = 'factor_name'
    result.columns = [result.columns.map('{0[1]}_{0[0]}'.format)]
    result['IC'] = IC
    # 调整列的顺序
    univ_top_list = ['IC']
    res_list = []
    for x in result.columns.tolist():
        x = x[0]
        if x == 'IC':
            continue
        elif 'univ_top' in x:
            univ_top_list.append(x)
        else:
            res_list.append(x)
    # print(result.shape)
    # print(len(univ_top_list + res_list))
    # result = result[univ_top_list + res_list]

    r = result.T
    ind = [x[0] for x in r.index.tolist()]
    value = r[r.columns[0]].tolist()
    result = dict(zip(ind, value))
    result['factor_name'] = r.columns[0]

    return result, topy, topy_univ

def test_kzz_overnight_ratio_with_longshortret(factor, y = None, universe = None, factor_name = None, seg_num = 5, select_topnum = 0.7,up_quantile = 0.05, down_quantile = 0.95, 
                             isrank = True, layer_lims = None,  save_path=None, save_image = False, show_image = False):
    # is_rank本来默认为false
    assert y is not None 
    assert universe is not None
    ref_score = factor.copy()
    ref_score.index.names = ['dt','Ticker']
    # ref_score = median_filter(ref_score.unstack(), mad = 3).stack()
    ref_score = ref_score.reindex(ref_score.index & y.index).sort_index()
    temp_ref = ref_score.reindex(ref_score.index & universe.index).sort_index()
    temp_y = y.reindex(temp_ref.index) 
    IC = round(temp_ref.corr(temp_y), 3)

    y_copy = y.reindex(ref_score.index)
    # IC = round(ref_score.unstack().corrwith(y_copy.unstack(), axis = 1).mean(), 3)
    if isrank == True:
        ref_score = ref_score.unstack().rank(axis = 1, pct = True).stack()
        up_quantile = 0
        down_quantile = 1
    if layer_lims is None:
        layer_lims = [ref_score.quantile(up_quantile), ref_score.quantile(down_quantile)]
    seg = ts_segment_test(ref_score, y_copy, seg_num, layer_lims, return_segment_time_series=True)
    seg = pd.DataFrame(seg)
    _ = seg.groupby(pd.Grouper(level=0))
    profit_pergroup = _.mean().cumsum()
    
    # 选出全样本最强的多少个最差的多少个
    topn = ref_score.groupby(ref_score.index.get_level_values(0)).apply(lambda x:x[x>=x.quantile(select_topnum)]).reset_index(level = 0, drop = True)
    botn = ref_score.groupby(ref_score.index.get_level_values(0)).apply(lambda x:x[x<=x.quantile(1 - select_topnum)]).reset_index(level = 0, drop = True)
    # topn = ref_score.groupby(ref_score.index.get_level_values(0)).nlargest(select_topnum).reset_index(level = 0, drop = True)
    # botn = ref_score.groupby(ref_score.index.get_level_values(0)).nsmallest(select_topnum).reset_index(level = 0, drop = True)
    topy = y.reindex(y.index & topn.index).sort_index()
    boty = y.reindex(y.index & botn.index).sort_index()
    topy_daily = topy.groupby(topy.index.get_level_values(0)).mean()
    boty_daily = boty.groupby(boty.index.get_level_values(0)).mean()
    select_y = pd.concat([topy_daily.cumsum(),boty_daily.cumsum()], axis = 1)
    select_y.columns = ['top_%d' % select_topnum, 'bottom_%d' % select_topnum]
    
    ref_score_univ = ref_score.reindex(ref_score.index & universe.index).sort_index()
    y_univ = y.reindex(ref_score_univ.index)
    ref_score_univ = ref_score_univ.unstack().rank(axis = 1, pct = True).stack()
    seg_univ = ts_segment_test(ref_score_univ, y_univ, seg_num, layer_lims, return_segment_time_series=True)
    seg_univ = pd.DataFrame(seg_univ)
    _ = seg_univ.groupby(pd.Grouper(level=0))
    profit_pergroup_univ = _.mean().cumsum()

    seg3_univ = ts_segment_test(ref_score_univ, y_univ, 3, layer_lims, return_segment_time_series=True)
    seg3_univ = pd.DataFrame(seg3_univ)
    _3 = seg3_univ.groupby(pd.Grouper(level=0))
    profit_pergroup_univ3 = _3.mean().cumsum()
    profit_pergroup_univ3['Q2-Q0'] = profit_pergroup_univ3['Q2'] - profit_pergroup_univ3['Q0']

    topn_univ = ref_score_univ.groupby(ref_score_univ.index.get_level_values(0)).apply(lambda x:x[x>=x.quantile(select_topnum)]).reset_index(level = 0, drop = True)
    botn_univ = ref_score_univ.groupby(ref_score_univ.index.get_level_values(0)).apply(lambda x:x[x<=x.quantile(1 - select_topnum)]).reset_index(level = 0, drop = True)
    # topn_univ = ref_score_univ.groupby(ref_score_univ.index.get_level_values(0)).nlargest(select_topnum).reset_index(level = 0, drop = True)
    # botn_univ = ref_score_univ.groupby(ref_score_univ.index.get_level_values(0)).nsmallest(select_topnum).reset_index(level = 0, drop = True)
    topy_univ = y_univ.reindex(y_univ.index & topn_univ.index).sort_index()
    boty_univ = y_univ.reindex(y_univ.index & botn_univ.index).sort_index()
    topy_daily_univ = topy_univ.groupby(topy_univ.index.get_level_values(0)).mean()
    boty_daily_univ = boty_univ.groupby(boty_univ.index.get_level_values(0)).mean()
    select_y_univ = pd.concat([topy_daily_univ.cumsum(),boty_daily_univ.cumsum()], axis = 1)
    select_y_univ.columns = ['top_%d' % select_topnum, 'bottom_%d' % select_topnum]

    result = pd.concat([kzz_evaluate(topy_daily),kzz_evaluate(boty_daily),kzz_evaluate(topy_daily_univ),kzz_evaluate(boty_daily_univ)], axis = 1)
    result.columns = ['full_top_%d' % select_topnum, 'full_bottom_%d' % select_topnum, 'univ_top_%d' % select_topnum, 'univ_bottom_%d' % select_topnum]
    
    result2 = pd.concat([get_something(topy),get_something(boty),get_something(topy_univ),get_something(boty_univ)], axis = 1)
    result2.columns = ['full_top_%d' % select_topnum, 'full_bottom_%d' % select_topnum, 'univ_top_%d' % select_topnum, 'univ_bottom_%d' % select_topnum]
    
    result = result.append(result2)

    fig = plt.figure(figsize=(15, 20), dpi = 200)

    ax = fig.add_subplot(5, 1, 1)
    plt.text(0.2, 1.2, factor_name, fontsize=28)
    plt.text(0.7, 1.2, 'IC: %s' % str(IC), fontsize=18)
    plt.text(0.1, 1.1, 'full_top_%d_winratio: ' % select_topnum + str(result.loc['Win Ratio', 'full_top_%d' % select_topnum]), fontsize=18)
    plt.text(0.5, 1.1, 'full_top_%d_plratio: ' % select_topnum + str(result.loc['Profit Loss Ratio', 'full_top_%d' % select_topnum]), fontsize=18)
    plt.text(0.1, 1.0, 'univ_top_%d_winratio: ' % select_topnum + str(result.loc['Win Ratio', 'univ_top_%d' % select_topnum]), fontsize=18)
    plt.text(0.5, 1.0, 'univ_top_%d_plratio: ' % select_topnum + str(result.loc['Profit Loss Ratio', 'univ_top_%d' % select_topnum]), fontsize=18)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    table(ax, result, loc='center')
    plt.subplots_adjust(top=0.95, hspace=0.3)

    # 图：全样本分组
    ax2 = fig.add_subplot(5, 1, 2)
    profit_pergroup.plot(ax=ax2, legend=True)
    # ax2.plot(profit_pergroup)
    plt.title('full sample segment', fontsize='large')
    # plt.xlabel('Date', fontsize='medium')
    plt.ylabel('Cumulative Ret', fontsize='medium')
    plt.subplots_adjust(top=0.95, hspace=0.3)

    # 图：分3组 top-bottom
    ax2 = fig.add_subplot(5, 1, 3)
    profit_pergroup_univ3['Q2-Q0'].plot(ax=ax2, legend=True)
    plt.title('Q2 - Q0 in univ', fontsize='large')
    # plt.xlabel('Date', fontsize='medium')
    plt.ylabel('Ret', fontsize='medium')
    color = 'tab:orange'
    plt.subplots_adjust(top=0.95, hspace=0.3)

    # 图：univ分组
    ax2 = fig.add_subplot(5, 1, 4)
    profit_pergroup_univ.plot(ax=ax2, legend=True)
    # ax2.plot(profit_pergroup_univ)
    plt.title('univ sample segment', fontsize='large')
    # plt.xlabel('Date', fontsize='medium')
    plt.ylabel('Cumulative Ret', fontsize='medium')
    plt.subplots_adjust(top=0.95, hspace=0.3)

    # 图：univ top
    ax2 = fig.add_subplot(5, 1, 5)
    select_y_univ['top_%d' % select_topnum].plot(ax=ax2, legend=False)
    # ax2.plot(select_y_univ['top_%d' % select_topnum])
    plt.title('univ sample top %d' % select_topnum, fontsize='large')
    # plt.xlabel('Date', fontsize='medium')
    plt.ylabel('Top Cumulative Ret', fontsize='medium')
    color = 'tab:orange'
    ax3 = ax2.twinx()
    select_y_univ['bottom_%d' % select_topnum].plot(ax=ax3, legend=False, color = color)
    # ax3.plot(select_y_univ.index.tolist(), select_y_univ['bottom_%d' % select_topnum].values, color = color)
    ax3.tick_params(axis = 'y', labelcolor = color)
    ax3.set_ylabel('Bottom Cumulative Ret', color = color)
    plt.subplots_adjust(top=0.95, hspace=0.3)

    if save_image:
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        plt.savefig(os.path.join(save_path, factor_name + '.png'), format='png')  # 存储图片
    if show_image:
        plt.show()
    plt.close()
    
    result = result.unstack().to_frame().T
    result.index = [factor_name]
    # result.index.name = 'factor_name'
    result.columns = [result.columns.map('{0[1]}_{0[0]}'.format)]
    result['IC'] = IC
    # 调整列的顺序
    univ_top_list = ['IC']
    res_list = []
    for x in result.columns.tolist():
        x = x[0]
        if x == 'IC':
            continue
        elif 'univ_top' in x:
            univ_top_list.append(x)
        else:
            res_list.append(x)
    # print(result.shape)
    # print(len(univ_top_list + res_list))
    # result = result[univ_top_list + res_list]

    r = result.T
    ind = [x[0] for x in r.index.tolist()]
    value = r[r.columns[0]].tolist()
    result = dict(zip(ind, value))
    result['factor_name'] = r.columns[0]

    return result, topy, topy_univ

def test_zsj_model(pkl_path,y,universe, show_image = True, save_image = True):
    save_path = os.path.join('/data/user/015626/data/share/factor/kzz_factor/report/model/' + pkl_path.split('/')[-2])
    csv_list = []
    model = pd.read_pickle(pkl_path)
    model_list= []
    for col in model.columns:
        model_list.append(model[col].unstack().rank(axis = 1,pct = True).stack())
        r,_,_ = test_kzz_overnight_super(model[col],y,universe,factor_name=col,select_topnum = 30, 
                         isrank=True,show_image=show_image,save_image=save_image,save_path=save_path)
        csv_list.append(r)
    new_model = pd.concat(model_list, axis = 1)
    f = new_model.mean(axis = 1)
    r,_,_ = test_kzz_overnight_super(f,y,universe,factor_name='model_mean',select_topnum = 30, 
                         isrank=True,show_image=show_image,save_image=save_image,save_path=save_path)
    csv_list.append(r)
    
    result = pd.DataFrame(csv_list)
    univ_top_list = ['factor_name','IC']
    res_list = []
    for x in result.columns.tolist():
        if x in ['factor_name','IC']:
            continue
        elif 'univ_top' in x:
            univ_top_list.append(x)
        else:
            res_list.append(x)
    r1 = result[univ_top_list + res_list].set_index('factor_name')    
    if save_image:
        r1.to_csv(os.path.join(save_path, pkl_path.split('/')[-2] + '_result.csv'))

def check_kzz_factor_into_lib(factor, y = None, universe = None, factor_name = None, seg_num = 5, select_topnum = 30, show_image = True,
                            save_image = False, save_path = None,
                             isrank = True, check_corr = True, target_corr_df = None, corr_t = 0.8, ic_t = 0.03, sharpe_univ_t = 5.5, annret_univ_t = 0.6, mdd_univ_t = -0.05, winratio_univ_t = 0.52,
                             sharpe_full_t = 2.5, annret_full_t = 0.3, mdd_full_t = -0.3, winratio_full_t = 0.4):
    r,topy,topy_univ = test_kzz_overnight_super(factor,y=y,universe = universe, factor_name=factor_name,select_topnum = 30, 
                         isrank=True,show_image=show_image,save_image=save_image,save_path=save_path)
    inflag = True
    if r['IC'] < ic_t:
        print('IC:', r['IC'], ic_t)
        inflag = False
    elif r['Sharpe Ratio_univ_top_30'] < sharpe_univ_t:
        print('Sharpe Ratio_univ_top_30', r['Sharpe Ratio_univ_top_30'], sharpe_univ_t)
        inflag = False        
    # elif float(r['Annual Return_univ_top_30'].replace('%',''))/100 < annret_univ_t:
    #     print('Annual Return_univ_top_30', r['Annual Return_univ_top_30'], annret_univ_t)
    #     inflag = False
    # elif float(r['Max Drawdown_univ_top_30'].replace('%',''))/100 < mdd_univ_t:
    #     print('Max Drawdown_univ_top_30', r['Max Drawdown_univ_top_30'], mdd_univ_t)
    #     inflag = False
    # elif r['Win Ratio_univ_top_30'] < winratio_univ_t:
    #     print('Win Ratio_univ_top_30', r['Win Ratio_univ_top_30'], winratio_univ_t)
    #     inflag = False
    # elif r['Sharpe Ratio_full_top_30'] < sharpe_full_t:
    #     print('Sharpe Ratio_full_top_30', r['Sharpe Ratio_full_top_30'] , sharpe_full_t)
    #     inflag = False
    # elif float(r['Annual Return_full_top_30'].replace('%',''))/100 < annret_full_t:
    #     print('Annual Return_full_top_30', r['Annual Return_full_top_30'], annret_full_t)
    #     inflag = False
    # elif float(r['Max Drawdown_full_top_30'].replace('%',''))/100 < mdd_full_t:
    #     print('Max Drawdown_full_top_30', r['Max Drawdown_full_top_30'], mdd_full_t)
    #     inflag = False
    # elif r['Win Ratio_full_top_30'] < winratio_full_t:
    #     print('Win Ratio_full_top_30', r['Win Ratio_full_top_30'], winratio_full_t)
    #     inflag = False
    if inflag == False:
        print(False)
        return False

    if check_corr:
        _target_corr = target_corr_df.reindex(factor.index)
        corrdf = _target_corr.corrwith(factor)
        corrdf = corrdf[corrdf > corr_t]
        if len(corrdf) > 0:
            print(corrdf)
            print(False)
            return False
    print(True)
    return True
