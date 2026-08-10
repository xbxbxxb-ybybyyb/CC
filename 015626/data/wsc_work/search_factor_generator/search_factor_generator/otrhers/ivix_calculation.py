import pandas as pd  # 42
import datetime as dt  # 67
import numpy as np  # 133

from xquant.thirdpartydata.marketdata import MarketData

ma = MarketData()


class IvixCalculate:
    """
    根据给定日期和标的证券计算当天标的对应期权的隐含波动率
    """

    def __init__(self, calc_date, underlying_security, risk_free_rate):
        """
        类初始化
        :param calc_date: int, e.g.20200202
            iv的计算日期
        :param underlying_security: {'510050', '510300', '159919', '000300'}
            iv的标的指数，目前国内共有4支证券成为期权标的
        :param risk_free_rate: float
            当日的无风险利率
        """
        self.calc_date = calc_date
        self.underlying_security = underlying_security
        self.risk_free_rate = risk_free_rate

    @staticmethod
    def tick_data_to_minute(df_tick):
        """
        把tick数据resample成分钟数据
        :param df_tick: dataframe
            tick数据
        :return: dataframe
            由tick数据resample得到的分钟数据
        """
        df_tick['minute'] = [str(i)[:4] for i in df_tick['MDTime']]
        df_minute = pd.DataFrame(index=df_tick['minute'].unique(),
                                 columns=['open', 'high', 'low', 'close', 'volume', 'amount'])
        df_minute['open'] = df_tick.groupby('minute')['LastPx'].first()
        df_minute['high'] = df_tick.groupby('minute')['LastPx'].max()
        df_minute['low'] = df_tick.groupby('minute')['LastPx'].min()
        df_minute['close'] = df_tick.groupby('minute')['LastPx'].last()
        df_minute['volume'] = df_tick.groupby('minute')['TotalVolumeTrade'].last().diff()
        df_minute['amount'] = df_tick.groupby('minute')['TotalValueTrade'].last().diff()
        df_minute = pd.concat([df_minute.iloc[30:150], df_minute.iloc[-121:-1]], axis=0)
        df_minute = df_minute.reset_index()

        return df_minute

    def get_option_info(self):
        """
        获取计算所需期权合约的所有执行价
        :return: list
            计算所需期权合约的所有执行价列表
        """
        if self.underlying_security == '000300':
            security_code = 'IO.CFE'
        else:
            security_code = self.underlying_security
        calc_date_dt = pd.to_datetime(str(self.calc_date))

        df_option_info = pd.read_hdf(
            '/data/group/800080/warehouse/prod/DATABASE/WIND/ChinaOptionDescription/ChinaOptionDescription.h5')
        df_option_info = df_option_info[df_option_info['S_INFO_SCCODE'].str.contains(security_code)].reset_index()
        df_option_info['enddate'] = pd.to_datetime([str(i)[:8] for i in df_option_info['S_INFO_MATURITYDATE']])
        contract_need = df_option_info[(df_option_info['dt'] <= calc_date_dt) & (
                df_option_info['enddate'] > calc_date_dt + dt.timedelta(
                  days=7))]  # 第一个条件表示这一天及以前已经开始交易的合约，第二个条件表示七天以后合约尚未下线（iv计算要求剩余到期天数超过7天）
        strike_price_list = sorted(contract_need['S_INFO_STRIKEPRICE'].unique())  # 所有计算所需合约的执行价列表

        return strike_price_list

    def get_minute_data(self, maturity_date):
        """
        从xquant读取原始的期权tick数据，并处理成后续计算iv要用到的分钟数据
        :param maturity_date: str, e.g.'2001'
            合约到期日，算iv的时候要分近月合约和次近月合约，该参数就是用来指定算哪类合约的iv
        :return: dataframe
            计算iv所需要的期权分钟数据
        """
        strike_price_list = self.get_option_info()
        intraday_starttime = str(int(self.calc_date * 1e6 + 90000))  # 开盘时间，xquant里期权数据从9:00就开始有值
        intraday_endtime = str(int(self.calc_date * 1e6 + 150000))  # 收盘时间

        df_minute_final = None

        for i_strike_price in strike_price_list:
            # print(i_strike_price)
            df_tick_call = ma.getOptTickData(underlyingSecurityID=self.underlying_security,
                                             startDateTime=intraday_starttime,
                                             endDateTime=intraday_endtime,
                                             callOrPut=True, expireMonth=maturity_date,
                                             exercisePrice=i_strike_price)
            df_tick_put = ma.getOptTickData(underlyingSecurityID=self.underlying_security,
                                            startDateTime=intraday_starttime,
                                            endDateTime=intraday_endtime,
                                            callOrPut=False, expireMonth=maturity_date,
                                            exercisePrice=i_strike_price)
            df_minute_call = IvixCalculate.tick_data_to_minute(df_tick_call)
            df_minute_call['C_P'] = 1
            df_minute_put = IvixCalculate.tick_data_to_minute(df_tick_put)
            df_minute_put['C_P'] = 0
            df_minute = pd.concat([df_minute_call, df_minute_put], axis=0)
            df_minute['strike_price'] = i_strike_price
            df_minute_final = df_minute_final if df_minute_final is None else pd.concat([df_minute_final, df_minute],
                                                                                        axis=0)

            return df_minute_final

    def volatility_calculate(self, maturity_date):
        """
        根据已经得到的期权分钟数据计算给定到期日合约的iv
        :param maturity_date: str, e.g.'2001'
            合约到期日，算iv的时候要分近月合约和次近月合约，该参数就是用来指定算哪类合约的iv
        :return: float
            给定到期日合约的iv
        """
        strike_price_list = self.get_option_info()
        option_minute_data = self.get_minute_data(maturity_date)
        days_delta = (dt.datetime.strptime(maturity_date, "%Y%m%d") - dt.datetime.strptime(str(self.calc_date),
                      "%Y%m%d")).days  # 合约剩余到期时间（日）
        remaining_expiry_time = [(days_delta * 240 - i) / (365 * 240) for i in
                                 range(1, 241)]  # 合约到期时间（分钟）占全年时间（分钟）的比例，记作T
        strike_price_interval = [strike_price_list[1] - strike_price_list[0]] + [
            (strike_price_list[i + 2] - strike_price_list[i]) / 2 for i in range(len(strike_price_list) - 2)] + [
                                    strike_price_list[-1] - strike_price_list[
                                        -2]]  # 第i个执行价所对应的执行价间隔，一般为(K_(i+1)-K_(i-1))/2，头和尾特殊处理

        call_put_diff = (option_minute_data.groupby(['index', 'strike_price'])['close'].first() -
                         option_minute_data.groupby(['index', 'strike_price'])['close'].last())  # 相同执行价的认购期权和认沽期权价格之差

        need_strike_price_idx = call_put_diff.groupby(call_put_diff.index.get_level_values(level=0)).apply(
            lambda _: abs(_).idxmin())  # 认购期权价格与认沽期权价格相差最小的执行价，记作S
        call_put_diff_use = call_put_diff.loc[need_strike_price_idx].reset_index()
        call_put_diff_use.columns = ['index', 'strike_price', 'price_diff']
        call_put_diff_use['T'] = remaining_expiry_time
        call_put_diff_use['F'] = (
                call_put_diff_use['strike_price'] + np.exp(self.risk_free_rate * call_put_diff_use['T']) *
                call_put_diff_use['price_diff'])  # S+exp^(RT)*[认购期权价格(S)-认沽期权价格(S)]

        K_0 = np.searchsorted(strike_price_list, call_put_diff_use['F'], side='left') - 1  # 小于F且最接近于F的执行价
        try:
            if K_0.min() < 0:  # 防止F比最小的执行价更小
                raise IndexError
            call_put_diff_use['K_0'] = [strike_price_list[i] for i in K_0]
        except IndexError:
            print('索引下界<0')

        price_df = pd.DataFrame(index=call_put_diff_use.index, columns=strike_price_list)
        for i, k_i in enumerate(strike_price_list):
            call_put_diff_use_temp = call_put_diff_use.copy()
            call_put_diff_use_temp['call'] = \
            option_minute_data[(option_minute_data['strike_price'] == k_i) & (option_minute_data['C_P'] == 1)][
                'close']
            call_put_diff_use_temp['put'] = \
            option_minute_data[(option_minute_data['strike_price'] == k_i) & (option_minute_data['C_P'] == 0)][
                'close']
            call_put_diff_use_temp['call_put_mean'] = (call_put_diff_use_temp['call'] + call_put_diff_use_temp[
                'put']) / 2
            call_put_diff_use_temp['P'] = call_put_diff_use_temp['call'] * (k_i > call_put_diff_use_temp['K_0']) + \
                                          call_put_diff_use_temp['put'] \
                                          * (k_i < call_put_diff_use_temp['K_0']) + call_put_diff_use_temp[
                                              'call_put_mean'] * (k_i == call_put_diff_use_temp['K_0'])
            price_df[k_i] = 2 / call_put_diff_use_temp['T'] * strike_price_interval[i] / (k_i ** 2) * np.exp(
                self.risk_free_rate * call_put_diff_use_temp['T']) * call_put_diff_use_temp['P']
            sigma = price_df.sum(axis=1) - 1 / call_put_diff_use['T'] * (
                        (call_put_diff_use['F'] / call_put_diff_use['K_0'] - 1) ** 2)

            return sigma

    def get_result(self):
        pass
