# import pandas as pd
# import numpy as np
# from scipy.stats import skew, kurtosis
# from sklearn.linear_model import LinearRegression
# import settings
# import os
# import warnings
# import json
#
# warnings.filterwarnings("ignore")
# # TRADING_DAYS = pd.read_csv(os.path.join(settings.DAILY_DATA_PATH, "tools", "tradingdays.csv"))["tradingdays"].to_list()
#
#
# def standardize(df, ismdf=False, n=3):
#     # df is a dataframe with columns of stock names and rows are tradingDays
#     if ismdf:
#         col = df.columns[0]
#         df = df[col].unstack()
#     df = df.replace(np.inf, np.nan)
#     df = df.replace(-np.inf, np.nan)
#     m = df.mean(axis=1)
#     s = df.std(axis=1, ddof=0)
#     df1 = df.subtract(m, axis=0).divide(s, axis=0)
#     df1[df1 > n] = n
#     df1[df1 < -n] = -n
#     dfnew = df1.multiply(s, axis=0).add(m, axis=0)
#     dfs = dfnew.subtract(dfnew.mean(axis=1), axis=0).divide(dfnew.std(axis=1, ddof=0), axis=0)
#     if ismdf:
#         dfs = pd.DataFrame(dfs.stack(), columns=[col])
#     return dfs
#
#
# def get_trading_day_by_date(start_date, end_date):
#     if start_date is None:
#         return [str(x) for x in TRADING_DAYS if x <= end_date]
#     elif end_date is None:
#         return [str(x) for x in TRADING_DAYS if start_date <= x]
#     else:
#         assert start_date >= TRADING_DAYS[0], "传入开始日期过小，超出交易日列表范围！"
#         assert end_date <= TRADING_DAYS[-1], "传入结束日期过大，超出交易日列表范围！"
#         return [str(x) for x in TRADING_DAYS if start_date <= x <= end_date]
#
# def get_trading_day(start, end):
#     if isinstance(start, str):
#         start = int(start)
#     if isinstance(end, str):
#         end = int(end)
#     # end不是日期
#     if end < 100000:
#         if end < 0:
#             res = get_trading_day_by_date(None, start)
#             assert len(res) >= -end, "end绝对值过大，超出交易日列表范围！"
#             res = res[end:]
#         elif end > 0:
#             res = get_trading_day_by_date(start, None)
#             assert len(res) >= end, "end绝对值过大，超出交易日列表范围！"
#             res = res[:end]
#         else:
#             raise Exception("end可取值不为0的整数，请重新输入！")
#     else:
#         res = get_trading_day_by_date(start, end)
#     return res
