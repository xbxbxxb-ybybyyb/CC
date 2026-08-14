import pandas as pd
import numpy as np
from xquant.factordata import FactorData
fd = FactorData()

def sta_profit(profit):
    res = {}
    res['收益（万元）'] = profit.sum()
    res['区间最大回撤（万元）'] = (profit.cumsum().cummax() - profit.cumsum()).max()
    res['日均最大回撤（万元）'] = (profit.cumsum().cummax() - profit.cumsum()).mean()
    res['日最大回撤90%分位数（万元）'] = (profit.cumsum().cummax() - profit.cumsum()).quantile(0.9)
    res['收益风险比'] = res['收益（万元）'] / res['区间最大回撤（万元）']
    res['日扣费胜率'] = len(profit[profit > 0]) / len(profit[profit != 0]) if len(profit[profit != 0]) else np.nan
    roll_profit = profit.rolling(3, min_periods=1).sum()
    res['收益夏普比'] = roll_profit.mean() / roll_profit.std() * 250 ** 0.5 if roll_profit.std() else np.nan
    # res['日均持有量（手）'] = buy_vol.apply(lambda dct: sum(dct.values())).mean()
    # res['日均占资规模（万元）'] = amt.mean()
    return pd.Series(res)

def find_target_contract_delta_tolerance(data, df, delta_ratio, mkt_ratio, contract_month, fee=0.0025, tol_range=['虚值二档', '虚值一档', '平值', '实值一档', '实值二档']):
    df = df.copy()
    # for option_type in ['虚值二档', '虚值一档', '平值', '实值一档', '实值二档']:
    for option_type in ['平值', '虚值一档', '虚值二档', '实值一档', '实值二档']:
        data[f'{contract_month}{option_type}持有合约手数'] = [{} for _ in range(len(data))]
        data[f'buy_vol_{contract_month}{option_type}'] = [{} for _ in range(len(data))]
        data[f'sell_vol_{contract_month}{option_type}'] = [{} for _ in range(len(data))]
        data[f'buy_amt_{contract_month}{option_type}'] = [{} for _ in range(len(data))]
        data[f'sell_amt_{contract_month}{option_type}'] = [{} for _ in range(len(data))]
        contract = None
        hold_amt = 0.0
        hold_vol = 0.0
        for dt in data.index:
            option_type_dt = df.loc[(dt,contract),'option_type'] if contract in df.xs(dt, level=0).index else None# 更新档位
            if option_type_dt not in tol_range: # 超出容忍度范围，进行合约替换
                # 先卖
                data.at[dt, f'sell_vol_{contract_month}{option_type}'] = {**data.at[dt, f'sell_vol_{contract_month}{option_type}'], contract: data.at[dt, f'sell_vol_{contract_month}{option_type}'].get(contract,0) + hold_vol}
                data.at[dt, f'sell_amt_{contract_month}{option_type}'] = {**data.at[dt, f'sell_amt_{contract_month}{option_type}'], contract: data.at[dt, f'sell_amt_{contract_month}{option_type}'].get(contract,0) + hold_amt}

                # 再买
                contract = df.loc[dt].query(f"option_type == '{option_type}'").index[0]
                data.loc[dt, f'{contract_month}{option_type}新开合约'] = contract
                pct = df.loc[(dt,contract),'pct']
                target_amt = delta_ratio * data.loc[dt,'策略股票持仓'] / abs(df.loc[(dt,contract),'factor_delta'])
                mkt_amt = df.loc[(dt,contract),'amt']
                trade_price = df.loc[(dt,contract),'twap']
                target_buy_vol = min(np.floor(target_amt * 1e4 / data.loc[dt,'index_pre_close'] / 100), 100)
                buy_amt = min(target_buy_vol * 100 * trade_price / 10000, mkt_ratio * mkt_amt)
                buy_vol = np.floor(buy_amt * 1e4 / trade_price / 100)
                buy_amt = (buy_vol * 100 * trade_price / 10000)

                cost = 15*(hold_vol+buy_vol)/10000 + (hold_amt+buy_amt)*fee# 万元

                hold_vol = buy_vol # 买入合约即持有合约
                hold_amt = buy_amt
                data.at[dt, f'{contract_month}{option_type}持有合约手数'] = {**data.at[dt, f'{contract_month}{option_type}持有合约手数'], contract: data.at[dt, f'{contract_month}{option_type}持有合约手数'].get(contract, 0) + hold_vol}
                # data.loc[dt, f'{contract_month}{option_type}买入合约市场成交额'] = mkt_amt
                data.at[dt, f'buy_vol_{contract_month}{option_type}'] = {**data.at[dt, f'buy_vol_{contract_month}{option_type}'], contract: data.at[dt, f'buy_vol_{contract_month}{option_type}'].get(contract, 0) + buy_vol}
                data.at[dt, f'buy_amt_{contract_month}{option_type}'] = {**data.at[dt, f'buy_amt_{contract_month}{option_type}'], contract: data.at[dt, f'buy_amt_{contract_month}{option_type}'].get(contract, 0) + buy_amt}
                data.loc[dt, f'profit_{contract_month}{option_type}'] = buy_amt * pct - cost

            # 在容忍度内，不进行调仓，但考虑加减仓
            else:
                target_amt = delta_ratio * data.loc[dt, '策略股票持仓'] / abs(df.loc[(dt, contract), 'factor_delta'])
                mkt_amt = df.loc[(dt, contract), 'amt']
                trade_price = df.loc[(dt, contract), 'twap']
                target_hold_vol = np.floor(target_amt * 1e4 / data.loc[dt, 'index_pre_close'] / 100) # hold可以超100
                if target_hold_vol > hold_vol: # 继续买
                    target_buy_vol = min(target_hold_vol - hold_vol, 100) # 开仓不能超100手
                    trade_amt = min(target_buy_vol * 100 * trade_price / 10000, mkt_ratio * mkt_amt)
                    trade_vol = np.floor(trade_amt * 1e4 / trade_price / 100)
                    trade_amt = (trade_vol * 100 * trade_price / 10000)
                    data.at[dt, f'buy_vol_{contract_month}{option_type}'] = {**data.at[dt, f'buy_vol_{contract_month}{option_type}'], contract: data.loc[dt, f'buy_vol_{contract_month}{option_type}'].get(contract, 0) + trade_vol}
                    data.at[dt, f'buy_amt_{contract_month}{option_type}'] = {**data.at[dt, f'buy_amt_{contract_month}{option_type}'], contract: data.loc[dt, f'buy_amt_{contract_month}{option_type}'].get(contract, 0) + trade_amt}
                    hold_vol += trade_vol
                else:
                    target_sell_vol = hold_vol - target_hold_vol # 平仓超100手没事
                    trade_amt = min(target_sell_vol * 100 * trade_price / 10000, mkt_ratio * mkt_amt)
                    trade_vol = np.floor(trade_amt * 1e4 / trade_price / 100)
                    trade_amt = (trade_vol * 100 * trade_price / 10000)
                    data.at[dt, f'sell_vol_{contract_month}{option_type}'] = {**data.at[dt, f'sell_vol_{contract_month}{option_type}'], contract: data.loc[dt, f'sell_vol_{contract_month}{option_type}'].get(contract, 0) + trade_vol}
                    data.at[dt, f'sell_amt_{contract_month}{option_type}'] = {**data.at[dt, f'sell_amt_{contract_month}{option_type}'], contract: data.loc[dt, f'sell_amt_{contract_month}{option_type}'].get(contract, 0) + trade_amt}
                    hold_vol -= trade_vol

                hold_amt = hold_vol*100 * trade_price / 10000
                pct = df.loc[(dt,contract),'pct']
                cost = 15*trade_vol/10000 + trade_amt*fee
                data.at[dt, f'{contract_month}{option_type}持有合约手数'] = {**data.at[dt, f'{contract_month}{option_type}持有合约手数'], contract: data.at[dt, f'{contract_month}{option_type}持有合约手数'].get(contract, 0) + hold_vol}
                # data.loc[dt, f'{contract_month}{option_type}买入合约市场成交额'] = mkt_amt
                data.loc[dt, f'profit_{contract_month}{option_type}'] = hold_amt*pct - cost

        data[f'profit_{contract_month}{option_type}'] = data[f'profit_{contract_month}{option_type}'].shift(1)
        data[f'profit_{contract_month}{option_type}'] = data[f'profit_{contract_month}{option_type}'].fillna(0)

    return data

def find_target_contract_delta(data, df, delta_ratio, mkt_ratio, contract_month):
    df = df.copy()
    for option_type in ['平值', '虚值一档', '虚值二档', '实值一档', '实值二档']:
        df_filtered = df[df['option_type'] == option_type]
        data[f'{contract_month}{option_type}买入合约'] = df_filtered.reset_index().set_index('dt')['Ticker']
        pct = df_filtered['pct'].droplevel('Ticker') - 0.002
        target_amt = delta_ratio * data['策略股票持仓'] / df_filtered['factor_delta'].abs().droplevel('Ticker')
        mkt_amt = df_filtered.droplevel('Ticker')['amt']
        buy_price = df_filtered['twap'].droplevel('Ticker')
        target_buy_vol = np.floor(target_amt * 1e4 / data['index_pre_close'] / 10000)
        target_buy_amt = (target_buy_vol * 10000 * buy_price / 10000).combine(mkt_ratio * mkt_amt, min)
        buy_vol = np.floor(target_buy_amt * 1e4 / buy_price / 10000)
        buy_amt = (buy_vol * 10000 * buy_price / 10000)
        cost = 2 * 1.6 * buy_vol / 10000
        data[f'{contract_month}{option_type}持有合约手数'] = [{contract: vol} for contract, vol in zip(data[f'{contract_month}{option_type}买入合约'], buy_vol)]
        data[f'{contract_month}{option_type}买入合约市场成交额'] = mkt_amt
        data[f'buy_amt_{contract_month}{option_type}'] = buy_amt
        data[f'buy_vol_{contract_month}{option_type}'] = buy_vol
        data[f'profit_{contract_month}{option_type}'] = data[f'buy_amt_{contract_month}{option_type}'] * pct - cost
        data[f'profit_{contract_month}{option_type}'] = data[f'profit_{contract_month}{option_type}'].shift(1).fillna(0)
    return data


def fix_hedging(data, df, contract_month, amt_tot, mkt_ratio, spread_cost):
    df = df.copy()
    for option_type in ['平值', '虚值一档', '虚值二档', '实值一档', '实值二档']:
        data[f'{contract_month}{option_type}持有合约手数'] = [{} for _ in range(len(data))]
        data[f'profit_{contract_month}{option_type}'] = 0.0
        for i in range(len(extention_dates)):
            dt_start = extention_dates[i]
            dt_end = pd.Timestamp(fd.tradingday(extention_dates[i + 1].strftime('%Y%m%d'), -2)[0]) if i < len(
                extention_dates) - 1 else data.index.get_level_values('dt')[-1]
            contract = df.xs(dt_start, level='dt').query(f"option_type == '{option_type}'").index[0]
            mkt_amt = df.loc[(dt_start, contract), 'amt']
            buy_price = df.loc[(dt_start, contract), 'SettlePrice']
            target_buy_vol = np.floor(amt_tot * 1e4 / data.loc[dt_start, 'index_pre_close'] / 100)  # 取消100手限制
            target_buy_amt = min((target_buy_vol * 100 * buy_price / 10000), mkt_ratio * mkt_amt)
            buy_vol = np.floor(target_buy_amt * 1e4 / buy_price / 100)
            buy_amt = (buy_vol * 100 * buy_price / 10000)
            cost = 2 * 15 * buy_vol / 10000
            pct = df.xs(contract, level='Ticker')['pct'].loc[dt_start:dt_end]
            data.loc[dt_start, f'{contract_month}{option_type}买入合约'] = contract
            data.loc[dt_start:dt_end, f'{contract_month}{option_type}持有合约手数'] = data.loc[dt_start:dt_end,
                                                                                      f'{contract_month}{option_type}持有合约手数'].apply(
                lambda dct: {**dct, contract: dct.get(contract, 0) + buy_vol})
            data.loc[dt_start, f'{contract_month}{option_type}买入合约市场成交额'] = mkt_amt
            pct_ = pct - spread_cost
            data.loc[dt_start, f'buy_amt_{contract_month}{option_type}'] = buy_amt
            data.loc[dt_start, f'buy_vol_{contract_month}{option_type}'] = buy_vol
            data.loc[dt_start:dt_end, f'profit_{contract_month}{option_type}'] = (
                        buy_amt * ((1 + pct_).cumprod() - (1 + pct_).cumprod().shift(1).fillna(1)) - cost).values

        data[f'profit_{contract_month}{option_type}'] = data[f'profit_{contract_month}{option_type}'].shift(1).fillna(0)
    return data


def find_target_contract_fix_tolerance(data, df, contract_month, k=5, amt_tot=20000, mkt_ratio=0.1, spread_cost=0.002,
                                       tol_range=['虚值二档', '虚值一档', '平值', '实值一档', '实值二档']):
    df = df.copy()
    target_amt_per_day = amt_tot / k
    for option_type in ['平值', '虚值一档', '虚值二档', '实值一档', '实值二档']:
        vol_limit_dict = {idx: 100 for idx in data.index}
        data[f'{contract_month}{option_type}买入合约市场成交额'] = [{} for _ in range(len(data))]
        data[f'buy_amt_{contract_month}{option_type}'] = [{} for _ in range(len(data))]
        data[f'buy_vol_{contract_month}{option_type}'] = [{} for _ in range(len(data))]
        data[f'sell_vol_{contract_month}{option_type}'] = [{} for _ in range(len(data))]
        data[f'{contract_month}{option_type}持有合约手数'] = [{} for _ in range(len(data))]
        data[f'profit_{contract_month}{option_type}'] = 0.0
        for i in range(len(extention_dates)):
            dt_start = extention_dates[i]
            dt_end = extention_dates[i + 1] if i < len(extention_dates) - 1 else data.index.get_level_values('dt')[-1]
            target_amt = target_amt_per_day
            for j in range(k):  # 分k天建仓、平仓
                _dt_start_ = pd.Timestamp(fd.tradingday(dt_start.strftime('%Y%m%d'), j + 1)[-1])
                dt_start_ = pd.Timestamp(fd.tradingday(_dt_start_.strftime('%Y%m%d'), 2)[-1])
                dt_end_ = pd.Timestamp(fd.tradingday(dt_end.strftime('%Y%m%d'), j + 1)[-1]) if i < len(
                    extention_dates) - 1 else dt_end
                _dt_end_ = pd.Timestamp(fd.tradingday(dt_end_.strftime('%Y%m%d'), -2)[0]) if i < len(
                    extention_dates) - 1 else pd.Timestamp(fd.tradingday(dt_end.strftime('%Y%m%d'), -2)[0])
                _dt_end_contract = _dt_end_ if i < len(extention_dates) - 1 else dt_end
                contract = df.xs(_dt_start_, level='dt').query(f"option_type == '{option_type}'").index[int(i != 0)]
                buy_price = df.loc[(_dt_start_, contract), 'twap']
                mkt_amt = df.loc[(_dt_start_, contract), 'amt']

                target_buy_vol = min(np.floor(target_amt * 1e4 / data.loc[_dt_start_, 'index_pre_close'] / 100),
                                     vol_limit_dict[_dt_start_])
                target_buy_amt = min((target_buy_vol * 100 * buy_price / 10000), mkt_ratio * mkt_amt)
                act_buy_vol = np.floor(target_buy_amt * 1e4 / buy_price / 100)
                if act_buy_vol == 0:
                    continue
                vol_limit_dict[_dt_start_] -= act_buy_vol
                act_buy_amt = (act_buy_vol * 100 * buy_price / 10000)

                cost = 2 * 15 * act_buy_vol / 10000
                for dt_tmp in fd.tradingday(_dt_start_.strftime('%Y%m%d'), _dt_end_.strftime('%Y%m%d')):
                    _dt_end_tmp_ = pd.Timestamp(dt_tmp)
                    dt_end_tmp_ = pd.Timestamp(fd.tradingday(dt_tmp, 2)[-1])
                    if len(tol_range) and df.loc[(dt_end_tmp_, contract), 'option_type'] not in tol_range:
                        # 结算
                        if vol_limit_dict[dt_end_tmp_] == 0 or dt_end_tmp_ > _dt_end_:
                            continue
                        pct = df.xs(contract, level='Ticker')['pct'].loc[_dt_start_:_dt_end_tmp_]
                        # data.loc[_dt_start_, f'{contract_month}{option_type}买入合约'] = contract
                        data.at[_dt_start_, f'{contract_month}{option_type}买入合约市场成交额'] = {
                            **data.at[_dt_start_, f'{contract_month}{option_type}买入合约市场成交额'],
                            contract: mkt_amt}
                        data.loc[_dt_start_:_dt_end_tmp_, f'{contract_month}{option_type}持有合约手数'] = data.loc[
                                                                                                          _dt_start_:_dt_end_tmp_,
                                                                                                          f'{contract_month}{option_type}持有合约手数'].apply(
                            lambda dct: {**dct, contract: dct.get(contract, 0) + act_buy_vol})
                        pct_ = pct - spread_cost
                        data.at[_dt_start_, f'buy_amt_{contract_month}{option_type}'] = {
                            **data.at[_dt_start_, f'buy_amt_{contract_month}{option_type}'],
                            contract: data.loc[_dt_start_, f'buy_amt_{contract_month}{option_type}'].get(contract,
                                                                                                         0) + act_buy_amt}
                        data.at[_dt_start_, f'buy_vol_{contract_month}{option_type}'] = {
                            **data.at[_dt_start_, f'buy_vol_{contract_month}{option_type}'],
                            contract: data.loc[_dt_start_, f'buy_vol_{contract_month}{option_type}'].get(contract,
                                                                                                         0) + act_buy_vol}
                        data.loc[dt_start_:dt_end_tmp_, f'profit_{contract_month}{option_type}'] += (act_buy_amt * (
                                    (1 + pct_).cumprod() - (1 + pct_).cumprod().shift(1).fillna(1)) - cost).values
                        # 换仓
                        _dt_start_ = dt_end_tmp_
                        data.at[_dt_start_, f'sell_vol_{contract_month}{option_type}'] = {
                            **data.at[_dt_start_, f'sell_vol_{contract_month}{option_type}'],
                            contract: data.loc[_dt_start_, f'sell_vol_{contract_month}{option_type}'].get(contract,
                                                                                                          0) + act_buy_vol}
                        dt_start_ = pd.Timestamp(fd.tradingday(_dt_start_.strftime('%Y%m%d'), 2)[-1])
                        df_tmp = df.xs(_dt_start_, level='dt').query(f"option_type == '{option_type}'")
                        contract = df_tmp.index[df_tmp.index.str[:6] == contract[:6]][0] if _dt_start_ < dt_end else \
                        df_tmp.index[1]
                        buy_price = df.loc[(_dt_start_, contract), 'twap']
                        mkt_amt = df.loc[(_dt_start_, contract), 'amt']
                        target_buy_vol = min(np.floor(target_amt * 1e4 / data.loc[_dt_start_, 'index_pre_close'] / 100),
                                             vol_limit_dict[_dt_start_])
                        target_buy_amt = min((target_buy_vol * 100 * buy_price / 10000), mkt_ratio * mkt_amt)
                        act_buy_vol = np.floor(1e-6 + target_buy_amt * 1e4 / buy_price / 100)
                        vol_limit_dict[_dt_start_] -= act_buy_vol
                        act_buy_amt = (act_buy_vol * 100 * buy_price / 10000)
                        cost = 2 * 15 * act_buy_vol / 10000

                pct = df.xs(contract, level='Ticker')['pct'].loc[_dt_start_:_dt_end_]
                if len(pct) == 0 or act_buy_vol == 0:
                    continue
                data.at[_dt_start_, f'{contract_month}{option_type}买入合约市场成交额'] = {
                    **data.at[_dt_start_, f'{contract_month}{option_type}买入合约市场成交额'], contract: mkt_amt}
                data.loc[_dt_start_:_dt_end_contract, f'{contract_month}{option_type}持有合约手数'] = data.loc[
                                                                                                      _dt_start_:_dt_end_contract,
                                                                                                      f'{contract_month}{option_type}持有合约手数'].apply(
                    lambda dct: {**dct, contract: dct.get(contract, 0) + act_buy_vol})
                pct_ = pct - spread_cost
                data.at[_dt_start_, f'buy_amt_{contract_month}{option_type}'] = {
                    **data.at[_dt_start_, f'buy_amt_{contract_month}{option_type}'],
                    contract: data.loc[_dt_start_, f'buy_amt_{contract_month}{option_type}'].get(contract,
                                                                                                 0) + act_buy_amt}
                data.at[_dt_start_, f'buy_vol_{contract_month}{option_type}'] = {
                    **data.at[_dt_start_, f'buy_vol_{contract_month}{option_type}'],
                    contract: data.loc[_dt_start_, f'buy_vol_{contract_month}{option_type}'].get(contract,
                                                                                                 0) + act_buy_vol}
                data.loc[dt_start_:dt_end_, f'profit_{contract_month}{option_type}'] += (act_buy_amt * (
                            (1 + pct_).cumprod() - (1 + pct_).cumprod().shift(1).fillna(1)) - cost).values
                data.at[dt_end_, f'sell_vol_{contract_month}{option_type}'] = {
                    **data.at[dt_end_, f'sell_vol_{contract_month}{option_type}'],
                    contract: data.loc[dt_end_, f'sell_vol_{contract_month}{option_type}'].get(contract,
                                                                                               0) + act_buy_vol}

    return data


def find_target_contract_fix(data, df, contract_month, k, amt_tot, mkt_ratio=0.1, spread_cost=0.002):
    df = df.copy()
    # df = df[df['option_type'] != '']
    # df = df.reset_index()
    # df['prev_ticker'] = df.sort_values(['option_type','dt']).groupby('option_type')['Ticker'].shift(1)
    # df['extension_flag'] = (df['Ticker'] != df['prev_ticker'])
    # df = df.drop(columns=['prev_ticker'])
    # df = df.set_index(['dt','Ticker'])
    # extention_dates = sorted(list(set(df[df['extension_flag'] == 1].index.get_level_values('dt'))))
    target_amt_per_day = amt_tot / k  # 每天的名义本金
    for option_type in ['平值', '虚值一档', '虚值二档', '实值一档', '实值二档']:
        data[f'{contract_month}{option_type}持有合约手数'] = [{} for _ in range(len(data))]
        data[f'profit_{contract_month}{option_type}'] = 0.0
        for i in range(len(extention_dates)):
            dt_start = extention_dates[i]
            dt_end = extention_dates[i + 1] if i < len(extention_dates) - 1 else data.index.get_level_values('dt')[-1]
            # dt_end = pd.Timestamp(fd.tradingday(extention_dates[i+1].strftime('%Y%m%d'), -2)[0]) if i < len(extention_dates) - 1 else data.index.get_level_values('dt')[-1]
            target_amt = target_amt_per_day
            for j in range(k):  # 分k天建仓、平仓
                _dt_start_ = pd.Timestamp(fd.tradingday(dt_start.strftime('%Y%m%d'), j + 1)[-1])
                dt_start_ = pd.Timestamp(fd.tradingday(dt_start.strftime('%Y%m%d'), j + 2)[-1])
                dt_end_ = pd.Timestamp(fd.tradingday(dt_end.strftime('%Y%m%d'), j + 1)[-1]) if i < len(
                    extention_dates) - 1 else dt_end
                _dt_end_ = pd.Timestamp(fd.tradingday(dt_end_.strftime('%Y%m%d'), -2)[0]) if i < len(
                    extention_dates) - 1 else pd.Timestamp(fd.tradingday(dt_end.strftime('%Y%m%d'), -2)[0])
                _dt_end_contract = _dt_end_ if i < len(extention_dates) - 1 else dt_end
                contract = df.xs(_dt_start_, level='dt').query(f"option_type == '{option_type}'").index[int(i != 0)]
                buy_price = df.loc[(_dt_start_, contract), 'SettlePrice']
                mkt_amt = df.loc[(_dt_start_, contract), 'amt']

                target_buy_vol = np.floor(target_amt * 1e4 / data.loc[dt_start, 'index_pre_close'] / 100)  # 取消100手限制
                target_buy_amt = min((target_buy_vol * 100 * buy_price / 10000), mkt_ratio * mkt_amt)
                act_buy_vol = np.floor(target_buy_amt * 1e4 / buy_price / 100)
                act_buy_amt = (act_buy_vol * 100 * buy_price / 10000)

                cost = 2 * 15 * act_buy_vol / 10000
                pct = df.xs(contract, level='Ticker')['pct'].loc[_dt_start_:_dt_end_]
                data.loc[_dt_start_, f'{contract_month}{option_type}买入合约'] = contract
                data.loc[_dt_start_:_dt_end_contract, f'{contract_month}{option_type}持有合约手数'] = data.loc[
                                                                                                      _dt_start_:_dt_end_contract,
                                                                                                      f'{contract_month}{option_type}持有合约手数'].apply(
                    lambda dct: {**dct, contract: dct.get(contract, 0) + act_buy_vol})
                data.loc[_dt_start_, f'{contract_month}{option_type}买入合约市场成交额'] = mkt_amt
                # data.loc[dt_start:dt_end, f'{contract_month}{option_type}流通市值'] = df.xs(contract, level='Ticker')['Circu_Mkt'].loc[dt_start:dt_end]
                pct_ = pct - spread_cost
                # data.loc[dt_start:dt_end, f'pct_{contract_month}{option_type}'] = df.xs(contract, level='Ticker')['pct'].loc[dt_start_:dt_end_]
                data.loc[_dt_start_, f'buy_amt_{contract_month}{option_type}'] = act_buy_amt
                data.loc[_dt_start_, f'buy_vol_{contract_month}{option_type}'] = act_buy_vol
                data.loc[dt_start_:dt_end_, f'profit_{contract_month}{option_type}'] += (act_buy_amt * (
                            (1 + pct_).cumprod() - (1 + pct_).cumprod().shift(1).fillna(1)) - cost).values
    return data


def classify_moneyness_top7(df, index_col='index_pre_close', strike_col='Strike'):
    """
    对于每个日期 dt，标记最多7个合约：平值、实值一/二/三档、虚值一/二、三档，其余为空字符串''
    """

    def process_group(group):
        index_price = group[index_col].iloc[0]
        group['abs_diff'] = np.abs(group[strike_col] - index_price)
        group['diff'] = group[strike_col] - index_price
        # 初始化 option_type 为空字符串
        group['option_type'] = ''
        # 标记平值（最靠近指数的一个）
        atm_idx = group['abs_diff'].idxmin()
        group.at[atm_idx, 'option_type'] = '平值'
        # 剔除平值后，分别对正 diff（虚值方向）和负 diff（实值方向）排序
        non_atm = group.drop(index=atm_idx)
        # 虚值方向（diff < 0）：从大到小选前三个
        virtual_side = non_atm[non_atm['diff'] < 0].sort_values('diff', ascending=False)
        if len(virtual_side) >= 1:
            group.at[virtual_side.index[0], 'option_type'] = '虚值一档'
        if len(virtual_side) >= 2:
            group.at[virtual_side.index[1], 'option_type'] = '虚值二档'
        if len(virtual_side) >= 3:
            group.at[virtual_side.index[2], 'option_type'] = '虚值三档'
        if len(virtual_side) >= 4:
            group.at[virtual_side.index[3], 'option_type'] = '虚值四档'
        # 实值方向（diff > 0）：从小到大选前三个
        in_side = non_atm[non_atm['diff'] > 0].sort_values('diff')
        if len(in_side) >= 1:
            group.at[in_side.index[0], 'option_type'] = '实值一档'
        if len(in_side) >= 2:
            group.at[in_side.index[1], 'option_type'] = '实值二档'
        if len(in_side) >= 3:
            group.at[in_side.index[2], 'option_type'] = '实值三档'
        if len(in_side) >= 4:
            group.at[in_side.index[3], 'option_type'] = '实值四档'
        return group.drop(columns=['abs_diff', 'diff'])

    return df.groupby(level='dt', group_keys=False).apply(process_group)


ratio = 0.1
mkt_ratio = 0.1
start_date, end_date = 20230101, 20250630
trading_days = fd.tradingday(start_date, end_date)

data_2024_2025 = pd.read_excel('2024年~2025年上半年.xlsx',index_col=0)
data_2023 = pd.read_excel('事件型策略2023年净值.xlsx',index_col=0)
data_2023['策略日度盈利'] = data_2023['策略累计盈利'] - data_2023['策略累计盈利'].shift(1).fillna(0)
data_2022 = pd.DataFrame(index=[pd.Timestamp(date) for date in fd.tradingday(20220722, 20221231)],columns=['策略股票持仓','策略日度盈利'])
data = pd.concat([data_2022, data_2023[['策略股票持仓','策略日度盈利']], data_2024_2025], axis=0)
data = data.rename_axis('dt')
data.index = pd.to_datetime(data.index.astype(str))
data = data.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]

for date in trading_days:
    data_index = pd.read_csv(f'/data/group/800080/warehouseJG/prod/LOCAL_DATA/CSV/WIND/WIND_AIndexEODPrices/{date}.csv')
    data.loc[pd.Timestamp(date),'index_pre_close'] = data_index.loc[data_index['S_INFO_WINDCODE'] == '000852.SH','S_DQ_PRECLOSE'].values[0]
    data.loc[pd.Timestamp(date),'index_close'] = data_index.loc[data_index['S_INFO_WINDCODE'] == '000852.SH', 'S_DQ_CLOSE'].values[0]

df = pd.read_pickle('/dfs/user/023859/options/df_MO_20220722_20250630.pkl')
df['pct_settle'] = df['Next_SettlePrice']/df['SettlePrice'] - 1

unique_last_trading_dates = set(df['LastTradingDate'])

date_to_extend = {date: pd.Timestamp(fd.tradingday(date.strftime('%Y%m%d'), -3)[0]) for date in unique_last_trading_dates}
df['ExtentionDate'] = df['LastTradingDate'].map(date_to_extend)
df = df[df.index.get_level_values('dt') < df['ExtentionDate']]  # 去掉临到期合约

df['tag'] = df.groupby('dt')['LastTradingDate'].rank(method='dense', ascending=True)
df_filtered_this_month = df[df['tag'] == 1]
df_filtered_this_month = classify_moneyness_top7(df_filtered_this_month)
df_filtered_next_month = df[df['tag'] == 2]
df_filtered_next_month = classify_moneyness_top7(df_filtered_next_month)
df_filtered_next_2_month = df[df['tag'] == 3]
df_filtered_next_2_month = classify_moneyness_top7(df_filtered_next_2_month)
df_this_month = pd.concat([df_filtered_this_month, df_filtered_next_month]).sort_index()
df_next_month = pd.concat([df_filtered_next_month, df_filtered_next_2_month]).sort_index()

# df_filtered_this_month = df_filtered_this_month[df_filtered_this_month['option_type'].isin(['虚值四档','虚值三档', '虚值二档', '虚值一档', '平值', '实值一档', '实值二档','实值三档','实值四档'])]
df_filtered_this_month['factor_delta'] = df_filtered_this_month.groupby('option_type')['factor_delta'].ffill()
data = find_target_contract_delta_tolerance(data, df_filtered_this_month, ratio, mkt_ratio, '当月',fee=0.0025, tol_range=['虚值四档','虚值三档','虚值二档','虚值一档','平值','实值一档'])
data = find_target_contract_delta_tolerance(data, df_filtered_next_month, ratio, mkt_ratio, '次月',fee=0.0025, tol_range=['虚值四档','虚值三档','虚值二档','虚值一档','平值','实值一档'])

# data = find_target_contract_delta(data, df_filtered_this_month, ratio, mkt_ratio, '当月')
# data = find_target_contract_delta(data, df_filtered_next_month, ratio, mkt_ratio, '次月')

# data = fix_hedging(data, df_filtered_this_month, '当月', amt_tot=5000, mkt_ratio=0.1, spread_cost=0.002)
# data = fix_hedging(data, df_filtered_next_month, '次月', amt_tot=5000, mkt_ratio=0.1, spread_cost=0.002)

# data = find_target_contract_fix(data, df_this_month, '当月', amt_tot=20000, mkt_ratio=0.1, spread_cost=0.002)
# data = find_target_contract_fix(data, df_next_month, '次月', amt_tot=20000, mkt_ratio=0.1, spread_cost=0.002)

# data = find_target_contract_fix(data, df_this_month, contract_month='当月', k=5, buy_amt_tot=500, mkt_ratio=0.1, spread_cost=0.002)
# data = find_target_contract_fix(data, df_next_month, contract_month='次月', k=5, buy_amt_tot=500, mkt_ratio=0.1, spread_cost=0.002)

# data = find_target_contract_fix_tolerance(data, df_this_month, contract_month='当月', k=k, amt_tot=20000, mkt_ratio=0.1,
#                                           spread_cost=0.002, tol_range=['虚值二档', '虚值一档', '平值', '实值一档'])
# data = find_target_contract_fix_tolerance(data, df_next_month, contract_month='次月', k=k, amt_tot=20000, mkt_ratio=0.1,
#                                           spread_cost=0.002, tol_range=['虚值二档', '虚值一档', '平值', '实值一档'])

data['策略累计盈利'] = data['策略日度盈利'].cumsum()
res = {}
res['事件型策略'] = sta_profit(data['策略日度盈利'])
for contract_month in ['当月', '次月']:
# for contract_month in ['当月']:
    # for option_type in ['平值']:
    for option_type in ['平值', '虚值一档', '虚值二档', '实值一档', '实值二档']:
        # for contract_month in ['当月']:
        #     for option_type in ['虚值一档']:
        data[f'{contract_month}{option_type}累计盈利'] = (data['策略日度盈利'] + data[f'profit_{contract_month}{option_type}']).cumsum()
        data[f'{contract_month}{option_type}期权端累计盈利'] = data[f'profit_{contract_month}{option_type}'].cumsum()
        res[f'{contract_month}{option_type}'] = sta_profit(data['策略日度盈利'] + data[f'profit_{contract_month}{option_type}'])

res_df = pd.DataFrame(res)

with pd.ExcelWriter(f'/dfs/user/023859/options/期权低比例delta对冲回测结果_{ratio}_000852_twap_20230101_20250630.xlsx', engine='xlsxwriter') as writer:
    data.to_excel(writer, sheet_name='20230101~20250630上半年数据')
    res_df.to_excel(writer, sheet_name='收益统计')
    writer.save()


# with pd.ExcelWriter(f'/dfs/user/023859/options/期权低比例delta对冲回测结果_0.1_20220722_20250630.xlsx', engine='xlsxwriter') as writer:
#     data.to_excel(writer, sheet_name='20220722~20250630上半年数据')
#     res_df.to_excel(writer, sheet_name='收益统计')
#     writer.save()

def merge_vol_pct_amt_delta(row, df):
    dt = row.name
    vol_dict = row['次月虚值二档持有合约手数']
    index_close = row['index_close']
    merged = {}
    for contract, vol in vol_dict.items():
        pct = df.loc[(dt, contract), 'pct_chg']
        amt = df.loc[(dt, contract), 'SettlePrice'] * vol * 100 / 10000
        delta_exposure = df.loc[(dt, contract), 'delta'] * index_close * 100 / 10000
        exposure = index_close * 100 / 10000
        merged[contract] = {'vol': vol, 'pct': pct, 'amt': amt, 'delta_exposure': delta_exposure, 'exposure': exposure}
    return merged

data['次月虚值二档持有合约信息'] = data[['次月虚值二档持有合约手数', 'index_close']].apply(lambda row: merge_vol_pct_amt_delta(row, df), axis=1)
data['次月虚值二档持有合约总规模'] = data['次月虚值二档持有合约信息'].apply(lambda dct: sum(sub['amt'] for sub in dct.values()))
data['次月虚值二档delta敞口'] = data['次月虚值二档持有合约信息'].apply(lambda dct: sum(sub['vol'] * sub['delta_exposure'] for sub in dct.values()))
data['次月虚值二档敞口'] = data['次月虚值二档持有合约信息'].apply(lambda dct: sum(sub['vol'] * sub['exposure'] for sub in dct.values()))

data['事件型策略日度最大回撤'] = (data['策略日度盈利'].cumsum().cummax() - data['策略日度盈利'].cumsum())
data['期权+事件型策略日度最大回撤'] = ((data['策略日度盈利'] + data['profit_次月虚值二档']).cumsum().cummax() - (data['策略日度盈利'] + data['profit_次月虚值二档']).cumsum())

res_half_year = {}
half_year_dict = {'2023年': ['20230101', '20231231'],
                  '2023年上半年': ['20230101', '20230630'],
                  '2023年下半年': ['20230701', '20231231'],
                  '2024年': ['20240101', '20241231'],
                  '2024年上半年': ['20240101', '20240630'],
                  '2024年下半年': ['20240701', '20241231'],
                  '2025年上半年': ['20250101', '20250630'],
                  '2023~2025年上半年': ['20230101', '20250630']}

for period in half_year_dict:
    start_date, end_date = pd.Timestamp(half_year_dict[period][0]), pd.Timestamp(half_year_dict[period][1])
    res_half_year[(period, '事件型策略')] = sta_profit(data.loc[start_date:end_date]['策略日度盈利'])
    res_half_year[(period, '期权+事件型策略')] = sta_profit(data.loc[start_date:end_date, '策略日度盈利'] + data.loc[start_date:end_date, 'profit_次月虚值二档'])

res_df_half_year = pd.DataFrame(res_half_year)
res_df_half_year = res_df_half_year.sort_index(axis=1, level=0)

data_best = data[
    ['策略股票持仓', '策略日度盈利', '事件型策略日度最大回撤', 'index_close', 'index_pre_close', '次月虚值二档持有合约信息',
     '次月虚值二档持有合约总规模', '次月虚值二档敞口', '次月虚值二档delta敞口', \
     'profit_次月虚值二档', '期权+事件型策略日度最大回撤', 'buy_amt_次月虚值二档',
     'buy_vol_次月虚值二档', 'sell_vol_次月虚值二档', 'sell_amt_次月虚值二档', \
     '策略累计盈利', '次月虚值二档累计盈利', '次月虚值二档期权端累计盈利']].rename(
    columns={'次月虚值二档持有合约信息': '持有合约信息', '次月虚值二档持有合约总规模': '持有合约总规模', \
             '次月虚值二档敞口': '持有合约名义市值', '次月虚值二档delta敞口': 'delta敞口', \
             'profit_次月虚值二档': 'profit', \
             'buy_amt_次月虚值二档': 'buy_amt', 'buy_vol_次月虚值二档': 'buy_vol', 'sell_vol_次月虚值二档': 'sell_vol', 'sell_amt_次月虚值二档': 'sell_amt', \
             '次月虚值二档累计盈利': '对冲后策略累计盈利', '次月虚值二档期权端累计盈利': '策略期权端累计盈利'})

with pd.ExcelWriter(f'/dfs/user/023859/options/期权低比例delta对冲回测结果_{ratio}_000852_twap_次月虚值二档_20230101_20250630.xlsx',
                    engine='xlsxwriter') as writer:
    data_best.to_excel(writer, sheet_name='20230101~20250630次月虚值二档数据')
    res_df_half_year.to_excel(writer, sheet_name='期权次月虚值二档+事件型策略收益统计')
    writer.save()

# with pd.ExcelWriter(f'/dfs/user/023859/options/期权低比例delta对冲回测结果_0.1_当月虚值二档_20220722_20250630.xlsx', engine='xlsxwriter') as writer:
#     data_best.to_excel(writer, sheet_name='20220722~20250630当月虚值二档数据')
#     res_df_half_year.to_excel(writer, sheet_name='期权当月虚值二档+事件型策略收益统计')
#     writer.save()