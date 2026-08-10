from factor_generator import FactorGenerator
from operators_wsc import *



class wsc11_overnight_future(FactorGenerator):
    def __init__(self):
        super(wsc11_overnight_future, self).__init__(required_columns=['close', 'recent_month_mask', 'position', 'volume'],
                                                     lookback_bars=2000)

    def on_bar(self, data_dict):
        # 长江金工：经持仓量调整的价量相关性
        future_close = data_dict['close']
        future_position = data_dict['position']
        future_mask = data_dict['recent_month_mask']
        future_volume = data_dict['volume']

        position_1 = future_position[future_mask].sum(axis=1).to_frame()
        volume_1 = future_volume[future_mask].sum(axis=1).to_frame()
        close_1 = future_close[future_mask].sum(axis=1).to_frame()

        position_1['dt']  = [pd.to_datetime(i.date()) for i in position_1.index]
        volume_1['dt']  = [pd.to_datetime(i.date()) for i in volume_1.index]
        close_1['dt'] = [pd.to_datetime(i.date()) for i in close_1.index]

        a_daily = pd.Series(index=position_1['dt'].unique())

        for i, i_date in enumerate(position_1['dt'].unique()):
            position_temp = position_1[position_1['dt']==i_date].iloc[:230,0]
            volume_temp = volume_1[volume_1['dt']==i_date].iloc[:230,0]
            close_temp = close_1[close_1['dt']==i_date].iloc[:230,0]
            volume_weight = volume_temp / volume_temp.sum()
            position_daily = position_temp.iloc[-1] - position_temp.iloc[0]
            position_T_1 = volume_weight * position_daily
            position_T_0 = position_T_1 - ts_delta(position_temp, 1)
            position_modify = (position_T_0 + position_T_1).cumsum() + position_temp.iloc[0]
            pv = (ts_delta(close_temp, 1)).corr(ts_delta(position_modify, 1))
            # pv = (close_temp).corr(ts_delta(position_modify, 1))
            a_daily.iloc[i] = pv

        factor = ts_rank(a_daily, 20).to_frame()
        factor.index.name = 'dt'
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor