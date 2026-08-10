from multifactor.IO import IO
import pandas as pd
import numpy as np
from utils_wsc.help_functions import rolling_window, rolling_norm
from factor_test.SIF_Factor_Test5_IF import check_factor_into_lib_no_corr, SIF_Factor_Test
import datetime as dt
import bottleneck as bn


start_date = 20160916
end_date = 20200801

index_data = IO.read_data([start_date, end_date],
                          alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_STOCK_INDEX_SPOT_MINUTE.h5')
futures_data = IO.read_data([start_date, end_date],
                            alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/'
                                'MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5')

data_dict = pd.concat([index_data, futures_data], axis=1).xs('IF.CFE', level=1).sort_index()
data_dict.columns = [col + '_if' for col in data_dict.columns]
icdata = futures_data.xs('IC.CFE', level=1)
ihdata = futures_data.xs('IH.CFE', level=1)
ihdata.columns = [col + '_ih' for col in ihdata.columns]

icdata_spot = index_data.xs('IC.CFE', level=1)
ihdata_spot = index_data.xs('IH.CFE', level=1)
ihdata_spot.columns = [col + '_ih' for col in ihdata_spot.columns]
data_dict = data_dict.join(icdata).join(ihdata).join(icdata_spot).join(ihdata_spot)


def delta(df, d):
    output = df.diff(periods=d)
    return output


def reg_beta(df1, d):
    # 过去d期A对1:d回归的回归系数
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(np.arange(d) + 1, (temp_y.shape[0], 1))
        y = np.nansum((temp_y.T - np.nanmean(temp_y, axis=1).T) * (temp_x.T - np.nanmean(temp_x, axis=1).T), axis=0)
        x = np.nansum((temp_x.T - np.nanmean(temp_x, axis=1).T) ** 2, axis=0)
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = (y / x) * flag
    return output


def ts_decay_linear(df1, d):
    # weighted moving average over the past d periods
    # linearly decaying weights d, d – 1, …, 1 (rescaled to sum up to 1)
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    weight = np.arange(d) + 1
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(weight, (temp_y.shape[0], 1))
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d / 2), 1, np.nan)
        output[i].iloc[d - 1:] = ((temp_y * temp_x).sum(axis=1) / temp_x.sum(axis=1)) * flag
    return output


def ts_wma1(df1, alpha):
    # 移动平均 using weights (1-alpha)**(n-1), (1-alpha)**(n-2), …, 1-alpha, 1.
    output = df1.ewm(alpha=alpha, adjust=True).mean()
    return output


def ts_sma(df1, alpha):
    # 移动平均 using weights (1-alpha)**(n-1), (1-alpha)**(n-2), …, 1-alpha, 1.
    output = df1.ewm(alpha=alpha, adjust=False).mean()
    return output


def ts_wma(df1, d, alpha):
    # weighted moving average over the past d periods
    # with linearly decaying weights 1, 0.9, …, 0.9^(d-1) (rescaled to sum up to 1)
    output = pd.DataFrame(np.nan, index=df1.index, columns=df1.columns)
    weight = [(1 - alpha) ** i for i in range(d - 1, -1, -1)]
    for i in df1.columns:
        temp_y = df1[i].values
        temp_y = rolling_window(temp_y, d)
        temp_x = np.tile(weight, (temp_y.shape[0], 1))
        flag = np.sum(np.isnan(temp_y), axis=1)  # 缺失值个数
        flag = np.where(flag <= d - int(d/2), 1, np.nan)
        output[i].iloc[d - 1:] = ((temp_y * temp_x).sum(axis=1) / temp_x.sum(axis=1)) * flag
    return output


def ts_std(df1, d):
    # moving time-series standard deviation over the past d periods
    output = pd.DataFrame(bn.move_std(df1, window=d, min_count=int(d/2), axis=0, ddof=1),
                          index=df1.index, columns=df1.columns)
    return output


t1 = dt.datetime.now()
final_df = None
count = 0
for i in [45, 60, 75]:
    factor1 = ts_std(data_dict['open_if'].to_frame(), i)
    for j in [0.05, 0.1, 0.2]:
        factor2 = ts_sma(factor1, j)
        for k in [900, 1200, 1500]:
            factor3 = rolling_norm(factor2, k)
            if_true = check_factor_into_lib_no_corr(factor3)
            sif = SIF_Factor_Test(factor3, str(i) + '+' + str(j) + '+' + str(k), save_image=False, layers=4)
            result = sif.draw_result()
            temp_df = pd.DataFrame(result.values(), index=result.keys(), columns=[str(i) + '+' + str(j) + '+' + str(k)])
            temp_df.loc['if_true'] = str(if_true)
            final_df = temp_df if final_df is None else pd.concat([final_df, temp_df], axis=1)
            count = count + 1
            print(count)
final_df.T.to_excel('/data/user/017024/ts_sma(ts_std(open_if)).xlsx')
t2 = dt.datetime.now()
print('The process costs: ', t2 - t1)
