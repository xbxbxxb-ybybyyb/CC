# coding: utf-8
# Author：fengchi863
# Date ：2022/9/27 13:38

from dataApi import getData, stockList, tradeDate, indName
from dataApi.stockList import trans_int2windcode as to_wc
from dataApi.stockList import trans_windcode2int as Wc2Int
from xquant.factordata import FactorData
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.sans-serif'] = ['SimHei']
from LucienUtil.FileUtil import FileUtil
import numpy as np
import pandas as pd
import os
from LucienUtil import IO

fd = FactorData()

def forward_fill(arr, axis, zero_fill=True):
    arr = arr.swapaxes(axis, -1)
    if zero_fill:
        mask = arr == 0
    else:
        mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[-1]), 0)
    np.maximum.accumulate(idx, axis=-1, out=idx)

    out = arr[tuple(np.arange(idx.shape[x])[(None,) * x + (slice(None),) + (None,) * (idx.ndim - x - 1)] for x in range(idx.ndim - 1)) + (idx,)]
    out = out.swapaxes(axis, -1)
    return out

def get_lb(zt_flag):
    zt_values_copy = zt_flag.values.copy()
    zt_values2 = zt_values_copy.cumsum(axis=1)
    breaks = zt_values2 * (zt_values_copy == 0)
    zt_values3 = forward_fill(breaks, axis=1)
    zt_values4 = zt_values2 - zt_values3
    return zt_values4

class ZTGrad:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def continuos_zt_times(self):
        pass

if __name__ == '__main__':
    start_date, end_date = 20220101, 20221014
    week_start_date, week_end_date = 20221010, 20221014
    Friday = 20221014
    Friday_str = pd.to_datetime(str(Friday)).strftime('%Y-%m-%d')
    ths_dict = pd.read_json(f'/data/user/015614/daily/同花顺数据/同花顺概念排名/everyday/同花顺概念排名{Friday}.json', typ='dict')

    zt_data_path = f'/data/user/015614/daily/复盘/复盘{week_start_date}_{week_end_date}/涨停数据/'
    zt_plot_data_path = f'/data/user/015614/daily/复盘/复盘{week_start_date}_{week_end_date}/涨停数据分析图表/'

    shift_start_date = tradeDate.get_pre_trade_date(start_date, 40)
    date_list = tradeDate.get_date_range(start_date, end_date)
    shift_date_list = tradeDate.get_date_range(shift_start_date, end_date)
    week_date_list = tradeDate.get_date_range(week_start_date, week_end_date)

    # 获取Wind名字
    # fd = FactorData()
    # wind_concept = fd.get_factor_value('WIND_AIndexDescription', S_INFO_WINDCODE="like'884%'")
    # wind_concept['S_INFO_NAME'] = wind_concept['S_INFO_NAME'].str.replace('指数', '')
    # wind_concept = wind_concept[wind_concept['CHANGE_HISTORY'].astype(str).str.contains('概念')]  # 筛选概念、题材
    # wind_concept = wind_concept[~wind_concept['S_INFO_NAME'].str.contains('退市|板|全A|新股|振幅|低价|高价|点位贡献|重组|定增|回购|预增|龙虎榜|领涨龙头|金股|精选|中非合作|国资|台资|陆股通')]
    # wind_name_dict = wind_concept[['S_INFO_WINDCODE', 'S_INFO_NAME']].set_index('S_INFO_WINDCODE').to_dict()['S_INFO_NAME']
    #
    # sw2_name = pd.read_excel('/data/user/015614/junkData/133.xlsx', index_col=0)
    # sw2_name_dict = sw2_name['简称'].map(lambda x: x[:-4]).to_dict()
    #
    # name_dict = dict(list(wind_name_dict.items()) + list(sw2_name_dict.items()))

    jupiter_data = pd.DataFrame()
    for week_date in week_date_list:
        tmp_jupiter_data = pd.read_pickle(f'/data/user/015614/daily/basic/basic_wind_sw_history/BlockData/daily_max_pctchg_concept/jupiter/{week_date}.pkl')
        jupiter_data = pd.concat([jupiter_data, tmp_jupiter_data], axis=0)
    jupiter_dict = jupiter_data['概念名称'].reset_index().set_index('Ticker')['概念名称'].to_dict()

    stk_pool = stockList.clean_stock_list(no_ST=True, least_live_days=30, least_normal_days=1, no_pause=True, least_recover_days=0, start_date=shift_start_date, end_date=end_date)
    stk_list = stk_pool.iloc[-1].index.tolist()

    sw2 = getData.get_daily_1factor('SW20212', code_list=stk_list, date_list=[Friday]).T.reset_index().set_index('code')[Friday]
    sw2 = sw2.apply(lambda x: indName.sw2021_level2[x])
    sw2_dict = sw2.to_dict()

    def format_stock(stk_id, stk_name, jupiter_dict=jupiter_dict, sw2_dict=sw2_dict):
        stk_code = stockList.trans_int2windcode(stk_id)
        # return f'{stk_name}({stockList.trans_int2windcode(stk_id)[:-3]})' # 华泰证券(601688)
        # return f'{stk_name}({sw2_dict[stk_id] if stk_id in sw2_dict.keys() else ""},' \
        #     f'{jupiter_dict[stk_code].split(",")[0] if stk_code in jupiter_dict.keys() else ""})'
        return f'{stk_name}({jupiter_dict[stk_code].split(",")[0] if (stk_code in jupiter_dict.keys()) and (type(jupiter_dict[stk_code]) == str) else ""})'

    limit_max = getData.get_daily_1factor('limit_max', date_list=shift_date_list, code_list=stk_list) # 属于不复权的价格
    limit_min = getData.get_daily_1factor('limit_min', date_list=shift_date_list, code_list=stk_list)
    daily_pctchg = getData.get_daily_1factor('pct_chg', date_list=shift_date_list, code_list=stk_list)
    opn = getData.get_daily_1factor('open', date_list=shift_date_list, code_list=stk_list)
    low = getData.get_daily_1factor('low', date_list=shift_date_list, code_list=stk_list)
    high = getData.get_daily_1factor('high', date_list=shift_date_list, code_list=stk_list)
    close = getData.get_daily_1factor('close', date_list=shift_date_list, code_list=stk_list)
    high_badj = getData.get_daily_1factor('high_badj', date_list=shift_date_list, code_list=stk_list)
    open_badj = getData.get_daily_1factor('open_badj', date_list=shift_date_list, code_list=stk_list)
    pre_close_badj = getData.get_daily_1factor('pre_close_badj', date_list=shift_date_list, code_list=stk_list)
    daily_high_pctchg = (high_badj / pre_close_badj - 1) * 100
    daily_open_pctchg = (open_badj / pre_close_badj - 1) * 100
    zt = pd.DataFrame((close == limit_max)) & stk_pool
    filter_zt = pd.DataFrame((close == limit_max) & (opn != limit_max)) & stk_pool # 去掉一字板和T字板
    dt = pd.DataFrame(close == limit_min) & stk_pool
    zb = pd.DataFrame(((close != limit_max) & (high == limit_max))) & stk_pool
    filter_zb = pd.DataFrame((close != limit_max) & (high == limit_max) & (opn != limit_max)) & stk_pool

    zt = zt & (daily_pctchg > 6)
    filter_zt = filter_zt & (daily_pctchg > 6)
    dt = dt & (daily_pctchg < -6)
    zb = zb & (daily_high_pctchg > 6)   # 只要触过板就算，但同花顺上比如20220812宇通重工、宏和科技就不算在内，应该是必须上板一段时间
    filter_zb = filter_zb & (daily_high_pctchg > 6)

    short_name = fd.get_factor_value('Basic_factor', mddate=[str(end_date)], factor_names=['short_name'])
    short_name.index = short_name.index.map(stockList.trans_windcode2int)
    short_name = short_name.to_dict()['short_name']

    lb = pd.DataFrame(get_lb(zt.T).T, index=zt.index, columns=zt.columns)
    lb_height = lb.max(axis=1)  # 连板高度

    lb = lb.loc[date_list]
    lb_height = lb_height[date_list]

    # 计算连板梯度
    lb_grad = pd.DataFrame(index=range(2, 15)[::-1], columns=week_date_list)
    for _date in week_date_list:
        for _grad in lb_grad.index:
            if _grad in lb.T[_date].tolist():
                lb_list = lb.loc[_date][lb.loc[_date] == _grad].index.tolist()
                # 这里根据排序指标构造Series，然后排序后取index
                ind_series = pd.Series(dict(zip(lb_list, list(map(lambda x: sw2[x] if x in sw2.keys() else np.nan, lb_list))))).sort_values()
                lb_list = ind_series.index.tolist()
                format_lb_list = '\n'.join(list(map(lambda x: format_stock(x, short_name[x]), lb_list)))
                lb_grad.loc[_grad, _date] = format_lb_list
    _lb_grad = lb_grad.loc[:, week_start_date:week_end_date]
    _lb_grad = _lb_grad.dropna(how='all', axis=0)
    _lb_grad.columns = _lb_grad.columns.astype(str)
    _lb_grad.index = _lb_grad.index.astype(str)
    FileUtil.save_df2xls(_lb_grad, zt_data_path, f'市场梯度{week_start_date}_{week_end_date}.xlsx')

    #%% 计算涨停家数，炸板家数，炸板率，封板率等
    daily_zt_num = zt.sum(axis=1)   # 每日涨停数量
    daily_filter_zt_num = filter_zt.sum(axis=1)     # 每日筛选涨停数量
    daily_zb_num = zb.sum(axis=1)   # 每日炸板数量
    daily_filter_zb_num = filter_zb.sum(axis=1)     # 每日筛选炸板数量
    daily_zb_pctchg = daily_zb_num / (daily_zt_num + daily_zb_num)  # 每日炸板率
    daily_zt_pctchg = daily_zt_num / (daily_zt_num + daily_zb_num)  # 每日封板率
    daily_filter_zt_pctchg = daily_filter_zt_num / (daily_filter_zt_num + daily_filter_zb_num)  # 每日筛选封板率
    daily_filter_zb_pctchg = daily_filter_zb_num / (daily_filter_zt_num + daily_filter_zb_num)  # 每日筛选炸板率
    daily_rolling5d_filter_zt_num = daily_filter_zt_num.rolling(5).mean()
    daily_rolling5d_filter_zb_num = daily_filter_zb_num.rolling(5).mean()
    daily_rolling5d_filter_zt_pctchg = daily_filter_zt_pctchg.rolling(5).mean()
    daily_rolling5d_filter_zb_pctchg = daily_filter_zb_pctchg.rolling(5).mean()

    # 这里把index控制在本年度
    zt = zt.loc[date_list]
    filter_zt = filter_zt.loc[date_list]
    dt = dt.loc[date_list]
    zb = zb.loc[date_list]
    filter_zb = filter_zb.loc[date_list]
    daily_zt_num = daily_zt_num.loc[date_list]
    daily_filter_zt_num = daily_filter_zt_num.loc[date_list]
    daily_zb_num = daily_zb_num.loc[date_list]
    daily_filter_zb_num = daily_filter_zb_num.loc[date_list]
    daily_filter_zb_num = daily_filter_zb_num.loc[date_list]
    daily_zb_pctchg = daily_zb_pctchg.loc[date_list]
    daily_zt_pctchg = daily_zt_pctchg.loc[date_list]
    daily_filter_zt_pctchg = daily_filter_zt_pctchg.loc[date_list]
    daily_filter_zb_pctchg = daily_filter_zb_pctchg.loc[date_list]
    daily_rolling5d_filter_zt_num = daily_rolling5d_filter_zt_num.loc[date_list]
    daily_rolling5d_filter_zb_num = daily_rolling5d_filter_zb_num.loc[date_list]
    daily_rolling5d_filter_zt_pctchg = daily_rolling5d_filter_zt_pctchg.loc[date_list]
    daily_rolling5d_filter_zb_pctchg = daily_rolling5d_filter_zb_pctchg.loc[date_list]

    # 在每日的涨停股上加入所属概念，计算每日的概念集中度
    jupiter_concept_data = IO.read_data([start_date, end_date], alt='/data/group/800463/fengc/daily/concept/jupiter_concept.h5')
    filter_zt_stack = filter_zt.stack()[filter_zt.stack()].reset_index()
    filter_zt_stack['概念名称'] = filter_zt_stack.apply(lambda x: jupiter_concept_data.loc[(pd.to_datetime(str(x['mddate'])), to_wc(x['level_1'])), '概念名称']
        if (pd.to_datetime(str(x['mddate'])), to_wc(x['level_1'])) in jupiter_concept_data.index else '', axis=1)
    filter_zt_stack['概念内涨停数量'] = filter_zt_stack.apply(lambda x: jupiter_concept_data.loc[(pd.to_datetime(str(x['mddate'])), to_wc(x['level_1'])), '概念涨停数量']
        if (pd.to_datetime(str(x['mddate'])), to_wc(x['level_1'])) in jupiter_concept_data.index else np.nan, axis=1)
    filter_zt_stack['概念内涨停数量'] = filter_zt_stack['概念内涨停数量'].fillna(0)
    filter_zt_stack2 = filter_zt_stack.copy()
    filter_zt_stack = filter_zt_stack.query('概念内涨停数量 >= 5')
    daily_center_concept_num = filter_zt_stack.groupby(['mddate', '概念名称'])['概念内涨停数量'].count().reset_index()
    daily_center_concept_num = daily_center_concept_num.groupby('mddate').count()['概念名称'].reindex(index=date_list).fillna(0)

    # 20221018新增一个本周涨停数量大于等于5的概念
    weekly_zt_stack = filter_zt_stack2.query(f'mddate >= {week_start_date} & mddate <= {week_end_date}')
    weekly_zt_stack_num = weekly_zt_stack.groupby(['概念名称', 'level_1'])['概念内涨停数量'].count().reset_index().groupby('概念名称').count()['概念内涨停数量']
    weekly_zt_stack_num = weekly_zt_stack_num[weekly_zt_stack_num >= 5].sort_values(ascending=False)
    weekly_zt_stack_num_indexes = weekly_zt_stack_num.index.tolist()
    weekly_zt_stack_num_indexes.remove('')
    weekly_zt_stack_num = weekly_zt_stack_num.loc[weekly_zt_stack_num_indexes]
    weekly_zt_stack_num = pd.DataFrame(weekly_zt_stack_num)
    weekly_zt_stack_num.columns = ['本周概念内涨停数量']

    # %% 统计本周的数据在相对区间的位置
    stats_dict = {}
    stats_df = pd.DataFrame(index=[f'{start_date}-{end_date}', f'{week_start_date}-{week_end_date}'])
    stats_df['日涨停数均值'] = [round(daily_zt_num.mean(), 2), round(daily_zt_num.loc[week_start_date:week_end_date].mean(), 2)]
    stats_df['日筛选涨停数均值'] = [round(daily_filter_zt_num.mean(), 2), round(daily_filter_zt_num.loc[week_start_date:week_end_date].mean(), 2)]
    stats_df['日炸板数均值'] = [round(daily_zb_num.mean(), 2), round(daily_zb_num.loc[week_start_date:week_end_date].mean(), 2)]
    stats_df['日筛选炸板数均值'] = [round(daily_filter_zb_num.mean(), 2), round(daily_filter_zb_num.loc[week_start_date:week_end_date].mean(), 2)]
    stats_df = stats_df.T
    stats_dict['日均'] = stats_df

    stats_df2 = pd.DataFrame(index=['均值', '所处分位数'])
    weekly_zt_num_mean = round(daily_zt_num.loc[week_start_date:week_end_date].mean(), 2)
    weekly_zb_num_mean = round(daily_zb_num.loc[week_start_date:week_end_date].mean(), 2)
    weekly_zt_pctchg_mean = round(daily_zt_pctchg.loc[week_start_date:week_end_date].mean(), 2)
    weekly_zb_pctchg_mean = round(daily_zb_pctchg.loc[week_start_date:week_end_date].mean(), 2)
    weekly_filter_zt_num_mean = round(daily_filter_zt_num.loc[week_start_date:week_end_date].mean(), 2)
    weekly_filter_zt_pctchg_mean = round(daily_filter_zt_pctchg.loc[week_start_date:week_end_date].mean(), 2)
    weekly_filter_zb_num_mean = round(daily_filter_zb_num.loc[week_start_date:week_end_date].mean(), 2)
    weekly_filter_zb_pctchg_mean = round(daily_filter_zb_pctchg.loc[week_start_date:week_end_date].mean(), 2)
    weekly_lb_height = lb_height[week_date_list]
    stats_df2['涨停数'] = weekly_zt_num_mean, 1 - (daily_zt_num >= weekly_zt_num_mean).sum() / len(daily_zt_num)
    stats_df2['筛选涨停数'] = weekly_filter_zt_num_mean, 1 - (daily_filter_zt_num >= weekly_filter_zt_num_mean).sum() / len(daily_filter_zt_num)
    stats_df2['炸板数'] = weekly_zb_num_mean, 1 - (daily_zb_num >= weekly_zb_num_mean).sum() / len(daily_zb_num)
    stats_df2['封板率'] = weekly_zt_pctchg_mean, 1 - (daily_zt_pctchg >= weekly_zt_pctchg_mean).sum() / len(daily_zt_pctchg)
    stats_df2['筛选封板率'] = weekly_filter_zt_pctchg_mean, 1 - (daily_filter_zt_pctchg >= weekly_filter_zt_pctchg_mean).sum() / len(daily_filter_zt_pctchg)
    stats_df2['炸板率'] = weekly_zb_pctchg_mean, 1 - (daily_zb_pctchg >= weekly_zb_pctchg_mean).sum() / len(daily_zb_pctchg)
    stats_df2['市场高度'] = weekly_lb_height.max(), 1 - (lb_height >= weekly_lb_height.max()).sum() / len(lb_height)
    stats_df2['筛选炸板数'] = weekly_filter_zb_num_mean, 1 - (daily_filter_zb_num >= weekly_filter_zb_num_mean).sum() / len(daily_filter_zb_num)
    stats_df2['筛选炸板率'] = weekly_filter_zb_pctchg_mean, 1 - (daily_filter_zb_pctchg >= weekly_filter_zb_pctchg_mean).sum() / len(daily_filter_zb_pctchg)
    stats_df2['筛选滚动涨停数'] = daily_rolling5d_filter_zt_num.iloc[-1], 1 - (daily_rolling5d_filter_zt_num >= daily_rolling5d_filter_zt_num.iloc[-1]).sum() / len(daily_rolling5d_filter_zt_num)
    stats_df2['筛选滚动炸板数'] = daily_rolling5d_filter_zb_num.iloc[-1], 1 - (daily_rolling5d_filter_zb_num >= daily_rolling5d_filter_zb_num.iloc[-1]).sum() / len(daily_rolling5d_filter_zb_num)
    stats_df2['筛选滚动封板率'] = daily_rolling5d_filter_zt_pctchg.iloc[-1], 1 - (daily_rolling5d_filter_zt_pctchg >= daily_rolling5d_filter_zt_pctchg.iloc[-1]).sum() / len(daily_rolling5d_filter_zt_pctchg)
    stats_df2['筛选滚动炸板率'] = daily_rolling5d_filter_zb_pctchg.iloc[-1], 1 - (daily_rolling5d_filter_zb_pctchg >= daily_rolling5d_filter_zb_pctchg.iloc[-1]).sum() / len(daily_rolling5d_filter_zb_pctchg)
    stats_dict['分位数'] = stats_df2.T
    stats_dict['本周概念涨停数量'] = weekly_zt_stack_num
    FileUtil.save_dict2xls(stats_dict, zt_data_path, '上周和全年对比统计结果.xlsx')

    #%% 计算涨停次日溢价等
    # _zt = zt.loc[week_start_date:week_end_date]
    _zt = zt.copy()
    zt_stack = _zt.stack()[_zt.stack()].reset_index()
    zt_stack['次日溢价'] = zt_stack.apply(lambda x: daily_open_pctchg.shift(-1).loc[x['mddate'], x['level_1']], axis=1)
    daily_zt_tmr_open_profit = zt_stack.groupby(['mddate'])['次日溢价'].mean()  # 涨停次日溢价

    #%% 连板晋级率
    daily_lb_num = (lb >= 2).sum(axis=1)    # 连板数
    daily_lb_pctchg = daily_lb_num / daily_zt_num.shift(1)  # 连板晋级率

    output_df = pd.concat([lb_height,
                           daily_zt_num,
                           daily_zt_pctchg,
                           daily_zb_num,
                           daily_zb_pctchg,
                           daily_lb_num,
                           daily_lb_pctchg,
                           daily_filter_zt_num,
                           daily_filter_zt_pctchg,
                           daily_filter_zb_num,
                           daily_filter_zb_pctchg,
                           daily_rolling5d_filter_zt_num,
                           daily_rolling5d_filter_zb_num,
                           daily_rolling5d_filter_zt_pctchg,
                           daily_rolling5d_filter_zb_pctchg,
                           daily_center_concept_num], axis=1)
    output_df.columns = ['市场高度', '涨停数', '封板率', '炸板数', '炸板率', '连板数', '晋级率', '筛选涨停数', '筛选封板率', '筛选炸板数', '筛选炸板率',
                         '筛选滚动涨停数', '筛选滚动炸板数', '筛选滚动封板率', '筛选滚动炸板率', '概念集中度']
    output_df.index = output_df.index.astype(str)
    FileUtil.save_df2xls(output_df, zt_data_path, f'涨停统计数据{week_start_date}_{week_end_date}.xlsx')

    output_df = FileUtil.read_df4xls(zt_data_path, f'涨停统计数据{week_start_date}_{week_end_date}.xlsx').set_index('mddate')

    #%% 绘图
    def plot_twinx(data, col1, col2, output_path, file_name):
        fig, ax1 = plt.subplots(figsize=(36, 20), dpi=80)
        ax2 = ax1.twinx()
        label1 = col1[-3:] if '筛选' in col1 else col1
        label2 = col2[-3:] if '筛选' in col2 else col2
        ax1.bar(range(0, len(data)), data[col1].values, label=label1)
        ax2.plot(range(0, len(data)), data[col2].values, c='orange', label=label2, linewidth=5)
        ax1.scatter(range(len(data)-len(week_date_list), len(data)), data[col1].values[-len(week_date_list):], color='r', linewidth=5)
        ax2.scatter(range(len(data)-len(week_date_list), len(data)), data[col2].values[-len(week_date_list):], color='y', linewidth=5)
        ax1.set_ylabel(label1, fontsize=20)
        ax2.set_ylabel(label2, fontsize=20)
        ax1.legend(loc=2, borderaxespad=1.).set_zorder(2)
        ax2.legend(loc=1, borderaxespad=1.).set_zorder(2)
        plt.title(f'{label1}相关走势图', fontsize='large')
        for xtick in ax1.get_xticklabels():
            xtick.set_rotation(75)
            xtick.set_fontsize(20)
        for ytick in ax1.get_yticklabels():
            ytick.set_fontsize(20)
        for ytick in ax2.get_yticklabels():
            ytick.set_fontsize(20)
        # 设置横坐标等间隔，不然太密集
        plt.xticks(range(0, len(data), 3), data.index.astype(str)[range(0, len(data), 3)].tolist())
        os.makedirs(output_path, exist_ok=True)
        fig.savefig(f'{output_path}{file_name}', bbox_inches='tight', pad_inches=0.1)

    def plot_line(data, col, output_path, file_name):
        fig, ax = plt.subplots(figsize=(36, 12), dpi=80)
        ax.plot(range(0, len(data)), data[col].values, c='orange', label=col, linewidth=5)
        ax.scatter(range(len(data) - len(week_date_list), len(data)), data[col].values[-len(week_date_list):], color='r', linewidth=5)
        ax.set_ylabel(col, fontsize=20)
        ax.legend(loc=2, borderaxespad=1.).set_zorder(2)
        plt.title(f'{col}', fontsize='large')
        for xtick in ax.get_xticklabels():
            xtick.set_rotation(75)
            xtick.set_fontsize(20)
        for ytick in ax.get_yticklabels():
            ytick.set_fontsize(20)
        # 设置横坐标等间隔，不然太密集
        plt.xticks(range(0, len(data), 3), data.index.astype(str)[range(0, len(data), 3)].tolist())
        os.makedirs(output_path, exist_ok=True)
        fig.savefig(f'{output_path}{file_name}', bbox_inches='tight', pad_inches=0.1)

    plot_twinx(output_df, '筛选滚动涨停数', '筛选滚动封板率', zt_plot_data_path, f'涨停数_封板率_{Friday}.jpg')
    plot_twinx(output_df, '筛选滚动炸板数', '筛选滚动炸板率', zt_plot_data_path, f'炸板数_炸板率_{Friday}.jpg')
    plot_twinx(output_df, '连板数', '晋级率', zt_plot_data_path, f'连板数_晋级率_{Friday}.jpg')
    plot_line(output_df, '市场高度', zt_plot_data_path, f'市场高度_{Friday}.jpg')
    plot_line(output_df, '概念集中度', zt_plot_data_path, f'概念集中度_{Friday}.jpg')

    #%% 输出每一天的涨停股、炸板股、连板股
    daily_zt_dict = dict()
    for _date in week_date_list:
        zt_list = zt.loc[_date][zt.loc[_date]].index.tolist()
        zt_info = pd.DataFrame(index=zt_list)
        zt_info['股票名称'] = zt_info.index.map(lambda x: short_name[x] if x in short_name.keys() else "")
        zt_info['连板数'] = zt_info.index.map(lambda x: lb.loc[_date, x])
        zt_info['所属二级行业'] = zt_info.index.map(lambda x: sw2.loc[x] if x in sw2.index else "")
        zt_info['所属同花顺概念'] = zt_info.index.map(lambda x: ths_dict[to_wc(x)].split(",")[0] if to_wc(x) in ths_dict.keys() else "")
        zt_info['所属概念'] = zt_info.index.map(lambda x: jupiter_dict[to_wc(x)].split(",")[0] if to_wc(x) in jupiter_dict.keys() and type(jupiter_dict[to_wc(x)]) == str else "")
        zt_info = zt_info.sort_values(['连板数', '所属二级行业'], ascending=False)
        zt_info.index = zt_info.index.map(lambda x: str(x).zfill(6))
        daily_zt_dict[str(_date)] = zt_info
    FileUtil.save_dict2xls(daily_zt_dict, zt_data_path, '每日涨停股.xlsx')

    daily_zb_dict = dict()
    for _date in week_date_list:
        zb_list = filter_zb.loc[_date][filter_zb.loc[_date]].index.tolist()
        zb_info = pd.DataFrame(index=zb_list)
        zb_info['股票名称'] = zb_info.index.map(lambda x: short_name[x] if x in short_name.keys() else "")
        zb_info['前一日连板数'] = zb_info.index.map(lambda x: lb.shift(1).loc[_date, x])
        zb_info['所属二级行业'] = zb_info.index.map(lambda x: sw2.loc[x] if x in sw2.index else "")
        zb_info['所属同花顺概念'] = zb_info.index.map(lambda x: ths_dict[to_wc(x)].split(",")[0] if to_wc(x) in ths_dict.keys() else "")
        zb_info['所属概念'] = zb_info.index.map(lambda x: jupiter_dict[to_wc(x)].split(",")[0] if to_wc(x) in jupiter_dict.keys() else "")
        zb_info = zb_info.sort_values(['前一日连板数', '所属概念'], ascending=False)
        zb_info.index = zb_info.index.map(lambda x: str(x).zfill(6))
        daily_zb_dict[str(_date)] = zb_info
    FileUtil.save_dict2xls(daily_zb_dict, zt_data_path, '每日炸板股.xlsx')

    #%% ------------------------------------以下为手动运行--------------------------------
    #%% 根据成交记录来进行标粗，周五晚上19:00以后就可以开始跑这个
    jupiter_buy_record = pd.read_excel(f'/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/jupiter成交记录-{Friday}.xlsx', sheet_name='累计买入明细')
    jupiter_sell_record = pd.read_excel(f'/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/jupiter成交记录-{Friday}.xlsx', sheet_name='累计卖出明细')
    europa_buy_record = pd.read_excel(f'/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/Europa成交记录-{Friday}.xlsx', sheet_name='累计买入明细')
    europa_sell_record = pd.read_excel(f'/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/Europa成交记录-{Friday}.xlsx', sheet_name='累计卖出明细')
    jupiter_sell_record = jupiter_sell_record.dropna(subset=['卖出日期'])
    europa_sell_record = europa_sell_record.dropna(subset=['卖出日期'])
    jupiter_sell_record['卖出日期列表'] = jupiter_sell_record['卖出日期'].apply(lambda x: x.split(','))
    europa_sell_record['卖出日期列表'] = europa_sell_record['卖出日期'].apply(lambda x: x.split(','))

    # 为了在连板金字塔标注不同的颜色
    strategy = 'europa'    # europa jupiter
    deal_list = list()
    for _date in week_date_list:
        _date_str = pd.to_datetime(str(_date)).strftime('%Y-%m-%d')
        tmp_jupiter_buy_record = jupiter_buy_record.query(f'发生日期 == "{_date_str}" & 成交金额 > 0')
        tmp_europa_buy_record = europa_buy_record.query(f'发生日期 == "{_date_str}" & 成交金额 > 0')
        tmp_jupiter_sell_record = jupiter_sell_record[jupiter_sell_record['卖出日期列表'].apply(lambda x: _date_str in x)]
        tmp_europa_sell_record = europa_sell_record[europa_sell_record['卖出日期列表'].apply(lambda x: _date_str in x)]
        if strategy is 'jupiter':
            tmp_append_list = tmp_jupiter_buy_record['证券代码'].tolist() + tmp_jupiter_sell_record['证券代码'].tolist()
        else:
            tmp_append_list = tmp_europa_buy_record['证券代码'].tolist() + tmp_europa_sell_record['证券代码'].tolist()
        deal_list.extend(tmp_append_list)

    deal_stk_list = deal_list
    for _date in week_date_list:
        for _grad in lb_grad.index:
            if _grad in lb.T[_date].tolist():
                lb_list = lb.loc[_date][lb.loc[_date] == _grad].index.tolist()
                common_stk = list(set(list(map(to_wc, lb_list))) & set(deal_stk_list))
                if len(common_stk) > 0:
                    print(_date, _grad, list(map(lambda x: short_name[Wc2Int(x)], common_stk)))

    # 市场热点个股的委托与成交结果，标粗与下划线
    deal_list = list()
    for _date in week_date_list:
        _date_str = pd.to_datetime(str(_date)).strftime('%Y-%m-%d')
        # tmp_jupiter_buy_record = jupiter_buy_record.query(f'发生日期 == "{_date_str}" & 成交金额 > 0')
        # tmp_europa_buy_record = europa_buy_record.query(f'发生日期 == "{_date_str}" & 成交金额 > 0')
        tmp_jupiter_buy_record = jupiter_buy_record.query(f'发生日期 == "{_date_str}"')
        tmp_europa_buy_record = europa_buy_record.query(f'发生日期 == "{_date_str}"')
        tmp_jupiter_sell_record = jupiter_sell_record[jupiter_sell_record['卖出日期列表'].apply(lambda x: _date_str in x)]
        tmp_europa_sell_record = europa_sell_record[europa_sell_record['卖出日期列表'].apply(lambda x: _date_str in x)]
        tmp_append_list = tmp_jupiter_buy_record['证券代码'].tolist() + tmp_jupiter_sell_record['证券代码'].tolist() + \
                          tmp_europa_buy_record['证券代码'].tolist() + tmp_europa_sell_record['证券代码'].tolist()
        deal_list.extend(tmp_append_list)

    hot_stk_str = ''    # 以顿号、分隔，放入外部分析资料中的市场活跃个股名称
    hot_stk_list = hot_stk_str.split('、')
    common_stk = list(set(list(map(lambda x: short_name[Wc2Int(x)], deal_list))) & set(hot_stk_list))
    print(common_stk)

    #%% 统计涉及到的概念和二级行业
    weekly_zt_stk = pd.concat([daily_zt_dict[x] for x in daily_zt_dict.keys()], axis=0)
    weekly_zt_stk['所属二级行业'].unique()
    len(weekly_zt_stk['所属二级行业'].unique())
    weekly_zt_stk['所属同花顺概念'].unique()
    len(weekly_zt_stk['所属同花顺概念'].unique())
    weekly_zt_stk['所属概念'].unique()
    len(weekly_zt_stk['所属概念'].unique())

    #%% 统计炸板率最高的一天
    _date = 20221010
    zb_info = daily_zb_dict[str(_date)]
    # 手动调整，因为同一周内不同个股可能所属概念就变了
    zb_info.loc['002746', '所属概念'] = '鸡产业'
    zb_info.loc['002197', '所属概念'] = '互联网金融'
    zb_info.loc['003029', '所属概念'] = '网络安全'
    # 分析某一天炸板的个股所处行业、概念以及o2ul均值
    label = pd.read_hdf('/data/group/800463/project/project1_prod/generalStrong_v3/Label_zt/Label_zt.h5')
    label = label.loc[pd.to_datetime(str(_date)), slice(None)]
    tmp = zb_info.groupby('所属概念')['股票名称'].count().sort_values(ascending=False)
    len(tmp)
    FileUtil.save_df2xls(tmp, zt_data_path, f'{_date}炸板的概念.xlsx')
    zb_info['o2ul'] = zb_info.index.map(lambda x: label.loc[to_wc(int(x)), 'label_T_o2ul'] if to_wc(int(x)) in label.index else np.nan)
    tmp3 = zb_info.groupby('所属概念')['o2ul'].mean().sort_values(ascending=False).reindex(index=tmp.index)
    tmp1 = pd.concat([tmp, tmp3], axis=1)

    tmp_filter_zt = pd.DataFrame(filter_zt.loc[_date][filter_zt.loc[_date]])
    tmp_filter_zb = pd.DataFrame(filter_zb.loc[_date][filter_zb.loc[_date]])
    tmp_filter_zt['概念名称'] = tmp_filter_zt.index.map(lambda x: jupiter_concept_data.loc[(pd.to_datetime(str(_date)), to_wc(x)), '概念名称']
        if (pd.to_datetime(str(_date)), to_wc(x)) in jupiter_concept_data.index else '')
    tmp_filter_zb['概念名称'] = tmp_filter_zb.index.map(lambda x: jupiter_concept_data.loc[(pd.to_datetime(str(_date)), to_wc(x)), '概念名称']
        if (pd.to_datetime(str(_date)), to_wc(x)) in jupiter_concept_data.index else '')
    index = list(set(tmp_filter_zt['概念名称'].tolist() + tmp_filter_zb['概念名称'].tolist()))
    tmp_filter_zt_concept_num = tmp_filter_zt.groupby('概念名称').count().reindex(index=index).fillna(0)[_date]
    tmp_filter_zb_concept_num = tmp_filter_zb.groupby('概念名称').count().reindex(index=index).fillna(0)[_date]
    tmp_filter_zb_concept_pctchg = tmp_filter_zb_concept_num / (tmp_filter_zt_concept_num + tmp_filter_zb_concept_num)
    tmp1['概念炸板率'] = tmp1.index.map(lambda x: tmp_filter_zb_concept_pctchg.loc[x])

    from dataApi.sendInfo import send_file
    send_file(tmp1)
