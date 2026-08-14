# author: kiki_777
# date: 2021/5/27

import sys
sys.path.append('/data/group/800319/RealTime_Data')
from getdata_from_open import *
from datetime import datetime
import sys
sys.path.append('/data/group/800319')
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
import requests
import json
import time


def send_message(users, msg):

    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = " http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    for user in users:
        data = {"touser": user,
                "msgtype": "text",
                "agentid": 1000033,
                "text": {"content": msg}}
        json_data = json.dumps(data)
        requests.post(post_url, json_data)


send_message(['015628'], '开始测试')

today = datetime.today().strftime('%Y%m%d')
pre_date = get_pre_trade_date(int(today), 1)

daily_data = data_prepare(today)
preclose_day = daily_data['pre_close'].unstack()
limitmax_day = daily_data['max_price'].unstack()
limitmin_day = daily_data['min_price'].unstack()

trigger_concept = []
dict_daily = {'建党100周年':{'龙头':['603721.SH'],'活跃股': ['603000.SH', '600825.SH', '603888.SH', '601999.SH']},
              '碳中和':{'龙头':['002679.SZ', '000966.SZ'],'活跃股': ['000993.SZ', '600744.SH', '002639.SZ', '003039.SZ']}}
concept_list = ['建党100周年', '碳中和']


def get_daily_factor(factor_name):

    date_range = get_date_range(get_pre_trade_date(int(today), 120), get_pre_trade_date(int(today), 1))
    factor_df = get_daily_1factor(factor_name, date_range)
    factor_df.index = factor_df.index.map(str)
    factor_df.columns = factor_df.columns.map(trans_int2windcode)

    return factor_df


def interday_condition():

    close_badj = get_daily_factor('close_badj')
    ma5 = close_badj.rolling(5).mean()
    ma10 = close_badj.rolling(10).mean()
    ma20 = close_badj.rolling(20).mean()
    vol = get_daily_factor('volume')
    vol_ratio = vol/vol.rolling(5).mean().shift(1)
    pct = get_daily_factor('pct_chg')

    f = (ma5 > ma10) & (ma10 > ma20) & (vol_ratio > 0.8) & (~((pct < -5) & (vol_ratio > 1.2)))

    return f


def _forward_fill(arr, axis , zero_fill = True):
    arr = arr.swapaxes(axis , -1)
    if zero_fill:
        mask = arr == 0
    else:
        mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[-1]), 0)
    np.maximum.accumulate(idx, axis = -1, out = idx)
    out = arr[tuple(np.arange(idx.shape[x])[(None, )*x + (slice(None),) + (None,)*(idx.ndim-x-1)]
                   for x in range(idx.ndim-1))+(idx, )]
    out = out.swapaxes(axis, -1)
    return out

def calc_limit_high(limitup, error_limit):
    zt = np.array(limitup.astype(int)).T
    no_limit_idx = np.r_[0, (zt==0).sum(axis = 1)[:-1]].cumsum()
    if error_limit == 0:
        no_limit_idx = np.r_[tuple(no_limit_idx)]
        no_limit_arr = np.arange(zt.shape[1])[None, :].repeat(zt.shape[0], axis = 0)[zt == 0]
        no_limit_arr[no_limit_idx] = zt.shape[1]
    else:
        no_limit_idx = np.r_[tuple(no_limit_idx + x for x in range(error_limit))]
        no_limit_arr = np.arange(zt.shape[1])[None, :].repeat(zt.shape[0], axis = 0)[zt == 0]
        no_limit_arr = np.r_[[zt.shape[1]]*error_limit, no_limit_arr[: -error_limit]]
        no_limit_arr[no_limit_idx] = zt.shape[1]
    limit_idx = 1-zt
    limit_idx[limit_idx == 1] = no_limit_arr
    limit_idx = _forward_fill(limit_idx, axis = 1)
    limit_distance = np.arange(zt.shape[1])-limit_idx
    max_distance = np.fmax(limit_distance.max(axis = 0), error_limit)
    limit_high = pd.DataFrame(limit_distance.T, index =limitup.index, columns = limitup.columns)-error_limit
    limit_high[limit_high<0] = 0
    return limit_high


limitup = get_daily_1factor('limit_up', get_date_range(get_pre_trade_date(int(pre_date), 60), int(pre_date)))
limithigh = calc_limit_high(limitup, 2)
limithigh.index = limithigh.index.map(str)
limithigh.columns = limithigh.columns.map(trans_int2windcode)
limithigh_day = pd.DataFrame(limithigh.loc[str(pre_date)]).T
f = interday_condition()


def dragon_arbitrary(dragon_stk, stock_list, concept_name):

    stock_data = get_stock_factor(['ClosePx', 'HighPx', 'TotalVolumeTrade', 'TotalValueTrade', 'MeanPrice'], list(set(stock_list)|set(dragon_stk)))
    close = stock_data['ClosePx']
    high = stock_data['HighPx']
    cumhigh = high.expanding().max()
    volume = stock_data['TotalVolumeTrade']
    amt = stock_data['TotalValueTrade']
    avgprice = stock_data['MeanPrice']
    pct_1m = close.pct_change(1)
    pct_2m = close.pct_change(2)
    vol_ratio = (volume/volume.rolling(5).mean().shift(1)).shift(1)
    zt = (close.loc[close.index[-1]] == limitmax_day.loc[today, close.columns])
    limithigh_inday = limithigh_day.loc[str(pre_date), zt.index] * zt + zt

    buy_list = []
    # 1、判断是否满足板块条件:涨停股数量>=1, 实时涨跌幅>0, 实时涨跌幅排序前50%
    if concept_pct[concept_name].tolist()[-1] >= 0 and concept_pct_rank[concept_name].tolist()[-1] <= 0.5:
        if (close.loc[close.index[-1], stock_list].values == limitmax_day.loc[today, stock_list].values).sum() > 0 \
                and (close.loc[close.index[-1], stock_list].values == limitmin_day.loc[today, stock_list].values).sum() == 0 \
                and (close.loc[close.index[-1], dragon_stk].values == limitmax_day.loc[today, dragon_stk].values).sum() == 0:
            for stk in dragon_stk:
                # 2、判断是否满足龙头股日间条件
                if f.loc[str(pre_date), stk] == 0:
                    pass
                # 3、判断开盘涨跌幅及是否被卡位
                elif 0.03 >= close[stk].tolist()[0]/preclose_day.loc[today, stk]-1 >= -0.05 \
                        and limithigh_day.loc[str(pre_date), stk]> limithigh_inday.loc[stock_list].max():
                    if (close[stk][1:] > preclose_day.loc[today, stk]).sum() >= 2 and \
                            close[stk].tolist()[-1] > preclose_day.loc[today, stk] > close[stk].tolist()[-2]:
                        buy_list.append(stk)
                        trigger_concept.append(concept_name)
                        trigger_concept.append(concept_name)
                    else:
                        pass
                else:
                    pass

    if len(buy_list) > 0:
        send_message(['015628'], '%s板块内%s股票触发买入信号'%(concept_name, buy_list))


while time.localtime()[3] < 15:
    concept_pct = get_concept_value('Pct_Change')
    concept_pct_1m = concept_pct - concept_pct.shift(1)
    concept_pct_2m = concept_pct - concept_pct.shift(2)
    concept_pct_rank = concept_pct.rank(axis=1, ascending=False, pct=True)
    concept_max_num = get_concept_value('Max_Num', concept_list)
    concept_min_num = get_concept_value('Min_Num', concept_list)
    concept_vol = get_concept_value('TotalVolumeTrade', concept_list)

    for con in concept_list:

        concept_name = con
        dragon_stk = dict_daily[con]['龙头']
        stock_list = dict_daily[con]['活跃股']
        dragon_arbitrary(dragon_stk, stock_list, concept_name)

    concept_list = list(set(concept_list)-set(trigger_concept))
    time.sleep(1)

