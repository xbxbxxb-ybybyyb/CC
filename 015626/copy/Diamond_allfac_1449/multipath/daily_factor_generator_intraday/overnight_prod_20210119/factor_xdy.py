from factor_generator_xdy import FactorGeneratorXdy
from operators_wsc import *


def ts_rsi(data, d):
    data_diff = data - data.shift(1)
    data_diff[data_diff<0] = 0
    abs_data_diff = abs(data - data.shift(1))
    rsi = 100 * ts_mean(data_diff, d) / replace_zero(ts_mean(abs_data_diff, d))
    return rsi

def ts_ewma(data, d):
    y = data.ewm(halflife=d).mean()
    return y
    
def ts_macd(data, d):
    d_long = int(d * 3)
    d_short = int(d * 1.5)
    data_short = ts_mean(data, d_short)
    data_long = ts_mean(data, d_long)
    data_diff = data_short - data_long
    dea = ts_mean(data_diff, d)
    macd = 2 * (data_diff - dea)
    return macd

def ts_quantile(data, d, quantile):
    output = data.rolling(d).quantile(quantile/10)
    return output

def ts_position(data, d):
    output = rolling_norm(data, d)
    output = 0.5 * output + 0.5
    return output

def add_const(data, const):
    output = data + const
    return output

def ts_autocov(data, d, timelag):
    data_shift = ts_delay(data, timelag)
    output = ts_corr(data, data_shift, d)
    return output

def ts_level_change(data, d):
    output = (data - ts_delay(data, d)) + data
    return output

def turtle_helper(x):
    assert all(~np.isnan(x))
    counter = 0
    if x[-1] == x[-2]:
        return counter
    y = x[-1]
    # determine direction first round
    flag = 1 if y > x[-2] else -1
    # loop to find rank
    for i in reversed(x[0:-1]):
        if i == y:
            return counter
        else:
            _flag = 1 if y > i else -1
            if _flag * flag > 0:
                counter += flag
            else:
                return counter
    return counter

def ts_turtle(df, window=40):
    return df.rolling(window).apply(turtle_helper, raw=True)


class factor_xdy(FactorGeneratorXdy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, required_columns=['daily_close_spot', 'daily_high_spot', 'daily_low_spot', 'daily_amount_spot', 'daily_open_spot'],
                         lookback_bars=2000, **kwargs)

    def on_bar(self, data_dict):
        # 徐得元的合成因子
        index_close = data_dict['daily_close_spot']
        index_high = data_dict['daily_high_spot']
        index_low = data_dict['daily_low_spot']
        index_amount = data_dict['daily_amount_spot']
        index_open = data_dict['daily_open_spot']
                
        '''TSRESID(H_C,TSMA(TSDELTA(L_C,t=33),t=19)[0],t=82)'''
        H_C = index_high / index_close - 1
        L_C = index_low / index_close - 1
        factor_raw = ts_reg_beta(H_C, 82, ts_mean(ts_delta(L_C, 33), 19))
        x1 = rolling_norm(factor_raw, 240)
        x1.name = 'x1'

        '''TSMAX(TSBETA(TSMACD(TSBETA(TSSHIFT(TSEWMA(TSRSI(H_C,t=13),t=28)[0],t=15),t=14),t=17)[0],t=16),t=2)'''
        H_C = index_high / index_close - 1
        factor_raw = ts_max(ts_reg_beta(ts_macd(ts_reg_beta(ts_delay(ts_ewma(ts_rsi(H_C, 13), 28), 15), 14), 17), 16), 2)
        x2 = rolling_norm(factor_raw, 240)
        x2.name = 'x2'

        '''TSSKEW(TSPOSITION(TSQUANTILE(TSSHIFT(TSMACD(AMOUNT_5,t=20)[0],t=1),t=27,quantile=3),t=51),t=45)'''
        amount_5 = ts_sum(index_amount, 5)
        factor_raw = ts_skew(ts_position(ts_quantile(ts_delay(ts_macd(amount_5, 20), 1), 27, 3), 51), 45)
        x3 = rolling_norm(factor_raw, 240)
        x3.name = 'x3'

        '''TSPOSITION(ADDCONST(NORMALIZE(TSCOV(GAIN_20,O_C,t=81)),constant=-0.1760564961713173),t=107)'''
        GAIN_20 = ts_pct_change(index_close, 20)
        O_C = index_open / index_close - 1
        factor_raw = ts_position(add_const(ts_position(ts_cov(GAIN_20, O_C, 81), 240), -0.1760564961713173), 107)
        x4 = rolling_norm(factor_raw, 240)
        x4.name = 'x4'

        '''TSLEVELCHANGE(TSAUTOCOV(TSSHIFT(PCTCHG,t=20),t=59,timelag=16),t=16)'''
        pctchg = ts_pct_change(index_close, 1)
        factor_raw = ts_level_change(ts_autocov((ts_delay(pctchg, 20)), 59, 16), 16)
        x5 = rolling_norm(factor_raw, 240)
        x5.name = 'x5'

        '''TSAUTOCOV(TSTURTLE(HIGH,t=70),t=124,timelag=18)'''
        factor_raw = ts_autocov(ts_turtle(index_high, 70), 124, 18)
        x6 = rolling_norm(factor_raw, 240)
        x6.name = 'x6'

        '''TSMA(ADDCONST(NORMALIZE(TSAUTOCOV(TSEWMA(H_C,t=28)[1],t=41,timelag=14)),constant=-0.22542225793895465),t=2)'''
        H_C = index_high / index_close - 1
        factor_raw = ts_mean(add_const(rolling_norm(ts_autocov(H_C-ts_ewma(H_C, 28), 41, 14), 240), -0.22542225793895465), 2)
        x7 = rolling_norm(factor_raw, 240)
        x7.name = 'x7'

        '''TSAUTOCOV(TSRSI(OPEN,t=6),t=45,timelag=15)'''
        factor_raw = ts_autocov(ts_rsi(index_open, 6), 45, 15)
        x8 = rolling_norm(factor_raw, 240)
        x8.name = 'x8'

        '''TSTURTLE(TSSTD(O_C,t=74),t=62)'''
        O_C = index_open / index_close - 1
        factor_raw = ts_turtle(ts_std(O_C, 74), 62)
        x9 = rolling_norm(factor_raw, 240)
        x9.name = 'x9'

        factor_xdy = pd.concat([-x1, -x2, x3, -x4, x5, x6, x7, x8, x9], axis=1)
        factor = factor_xdy.mean(axis=1)
        factor = ts_rank(factor, 480)
        factor = factor.to_frame()
        # factor[factor<=0] = np.nan

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor