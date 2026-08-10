import numpy as np
import pandas as pd
import datetime
from xquant.factordata import FactorData
s = FactorData()

def get_arrow_dummies():
    univ = pd.read_pickle('./universe/stock_universe.pkl').reset_index()
    dt = univ.dt[0].strftime('%Y%m%d')
    trading_days = [pd.Timestamp(x) for x in s.tradingday(dt, (pd.Timestamp(dt) + datetime.timedelta(days = 60)).strftime('%Y%m%d'))]
    next_day_gap = np.array([(trading_days[x+1] - trading_days[x]).days for x in range(len(trading_days) - 1)])

    long_vacation_dates = np.array(trading_days[:-1])[(next_day_gap >= 4) & (next_day_gap <= 5)]
    long_vacation_deltas = np.array([[x.days for x in y - long_vacation_dates] for y in trading_days])
    long_vacation = np.array(trading_days)[((long_vacation_deltas <= 0) & (long_vacation_deltas >= -13)).any(axis = 1)]
    univ['long_vacation_3'] = [1 * (x in long_vacation) for x in univ.dt]

    long_vacation_dates = np.array(trading_days[:-1])[(next_day_gap >= 6) & (next_day_gap <= 7)]
    long_vacation_deltas = np.array([[x.days for x in y - long_vacation_dates] for y in trading_days])
    long_vacation = np.array(trading_days)[((long_vacation_deltas <= 0) & (long_vacation_deltas >= -13)).any(axis = 1)]
    univ['long_vacation_5'] = [1 * (x in long_vacation) for x in univ.dt]

    long_vacation_dates = np.array(trading_days[:-1])[(next_day_gap >= 8) & (next_day_gap <= 100)]
    long_vacation_deltas = np.array([[x.days for x in y - long_vacation_dates] for y in trading_days])
    long_vacation = np.array(trading_days)[((long_vacation_deltas <= 0) & (long_vacation_deltas >= -13)).any(axis = 1)]
    univ['long_vacation_7'] = [1 * (x in long_vacation) for x in univ.dt]

    result = pd.get_dummies(univ.set_index(['dt', 'Ticker']))
    
    return result

dummy = get_arrow_dummies()