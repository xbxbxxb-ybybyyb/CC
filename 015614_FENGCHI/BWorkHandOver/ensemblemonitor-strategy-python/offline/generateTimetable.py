import sys
import os
import datetime as dt
import numpy as np
import pandas as pd


#
from xquant.factordata import FactorData
from xquant.marketdata import MarketData

fd = FactorData()
mdp = MarketData()


def getKeyMinutes(sxw):
    if sxw == "0930":
        minutes = [dt.datetime(1949, 10, 1, 9, 40, 0) + dt.timedelta(minutes=10 * i) for i in range(12)]
    elif sxw == '1000':
        minutes = [dt.datetime(1949, 10, 1, 10, 10, 0) + dt.timedelta(minutes=10 * i) for i in range(3)]
    elif sxw == '1030':
        minutes = [dt.datetime(1949, 10, 1, 10, 40, 0) + dt.timedelta(minutes=10 * i) for i in range(3)]
    elif sxw == '1100':
        minutes = [dt.datetime(1949, 10, 1, 11, 10, 0) + dt.timedelta(minutes=10 * i) for i in range(3)]
    elif sxw == "1300":
        minutes = [dt.datetime(1949, 10, 1, 13, 10, 0) + dt.timedelta(minutes=10 * i) for i in range(3)]
    elif sxw == "1330":
        minutes = [dt.datetime(1949, 10, 1, 13, 40, 0) + dt.timedelta(minutes=10 * i) for i in range(3)]
    elif sxw == "1400":
        minutes = [dt.datetime(1949, 10, 1, 14, 10, 0) + dt.timedelta(minutes=10 * i) for i in range(3)]
    elif sxw == "1430":
        minutes = [dt.datetime(1949, 10, 1, 14, 40, 0) + dt.timedelta(minutes=10 * i) for i in range(3)]
    #        minutes = [dt.datetime(1949, 10, 1, 13, 30, 0) + dt.timedelta(minutes=10 * i) for i in range(10)]
    else:
        print("Wrong sxw")
    minutes = list(map(lambda x: x.strftime("%H:%M:%S"), minutes))

    return minutes


def getNonSuspendStartDate(symbol, startDate, period):
    tradingDays = fd.tradingday(startDate - 10000, startDate)
    startDateIndex = np.searchsorted(tradingDays, startDate)
    startIndex = startDateIndex - period
    endIndex = startDateIndex - 1

    counter = 0
    while True:
        amt = fd.get_factor_value("Basic_factor", [symbol], list(map(str, tradingDays[startIndex:endIndex + 1])), ["amt"])
        validDayNumber = (amt["amt"] > 0).sum()

        if validDayNumber == period:
            break

        startIndex -= 1
        counter += 1
        if counter > 60:
            print(symbol, "real start date")
            break

    return tradingDays[startIndex]


def getDailyVolumeSeries(df, sxw):
    if sxw == "0930":
        preMinute = 0
    elif sxw == '1000':
        preMinute = 1000
    elif sxw == '1030':
        preMinute = 1030
    elif sxw == '1100':
        preMinute = 1100
    elif sxw == '1300':
        preMinute = 1300
    elif sxw == '1330':
        preMinute = 1330
    elif sxw == "1400":
        preMinute = 1400
    elif sxw == "1430":
        preMinute = 1430
    #        preMinute = 1320
    else:
        print("Wrong sxw")

    minutes = getKeyMinutes(sxw)
    minutes = list(map(lambda x: int(x[:2] + x[3:5]), minutes))

    df = df.droplevel(0)
    df.loc[930, "volume"] += df.loc[925, "volume"]
    df = df.drop(925)
    df.loc[1456, "volume"] += df.loc[1457, "volume"]
    df.loc[1457, "volume"] = df.loc[1500, "volume"]
    df = df.drop(1500)

    volumeSummation = df.groupby(pd.cut(df.index, [preMinute] + minutes, right=False), as_index=False)["volume"].sum()
    volumeSummation.index = minutes

    return volumeSummation


def getTargetQtyIntervalList(symbol, targetQty, date, period, sxw):
    nonSuspendStartDate = getNonSuspendStartDate(symbol, date, period)
    minuteData = mdp.get_data_by_time_frame("Kline1M4ZT", symbol, "{} 080000000".format(nonSuspendStartDate), "{} 160000000".format(date))
    minuteData["MDTime"] = (minuteData["MDTime"].astype("int") / 100000)
    minuteData = minuteData.astype({"MDDate": "int", "MDTime": "int"}).rename(columns={"TotalVolumeTrade": "volume"})
    minuteData = minuteData.set_index(["MDDate", "MDTime"]).loc[:, ["volume"]]

    dailyVolumeDF = minuteData.groupby(level=0).apply(getDailyVolumeSeries, sxw=sxw)
    dailyVolumeDF = dailyVolumeDF["volume"].unstack(level=1)
    dailyVolumeDF = dailyVolumeDF[dailyVolumeDF.sum(axis=1) > 0]
    dailyVolumeDF = dailyVolumeDF.rolling(period).sum()
    dailyVolumeDF = dailyVolumeDF.iloc[-1]

    targetQtyPctSeries = (dailyVolumeDF / dailyVolumeDF.sum()).cumsum()

    targetQtyIntervalSeries = targetQtyPctSeries * targetQty
    targetQtyIntervalSeries = targetQtyIntervalSeries.apply(lambda x: int(x / 100) * 100)
    targetQtyIntervalSeries.iloc[-1] = int(targetQty)

    return targetQtyIntervalSeries.tolist()


def generateTimetableAndTargetQtyInterval(symbol, quantity, date, period, sxw):
    try:
        targetQty = abs(quantity)
        timetable = getKeyMinutes(sxw)
        targetQtyIntervalList = getTargetQtyIntervalList(symbol, targetQty, date, period, sxw)

        timetableRes = []
        targetQtyIntervalRes = []
        lastQty = None
        for tt, tq in zip(timetable, targetQtyIntervalList):
            if tq == 0 or tq == lastQty:
                continue

            timetableRes.append(tt)
            targetQtyIntervalRes.append(tq)

            lastQty = tq

        if quantity > 0:
            result = [{"Time": str(v1), "TargetQty": str(v2)} for v1, v2 in zip(timetableRes, targetQtyIntervalRes)]
        else:
            result = [{"Time": str(v1), "TargetQty": str(-v2)} for v1, v2 in zip(timetableRes, targetQtyIntervalRes)]

        return result
    except Exception as e:
        print(repr(e))
        return None


def getTargetPercentIntervalList(symbol, date, period, sxw):
    nonSuspendStartDate = getNonSuspendStartDate(symbol, date, period)
    minuteData = mdp.get_data_by_time_frame("Kline1M4ZT", symbol, "{} 080000000".format(nonSuspendStartDate), "{} 160000000".format(date))
    minuteData["MDTime"] = (minuteData["MDTime"].astype("int") / 100000)
    minuteData = minuteData.astype({"MDDate": "int", "MDTime": "int"}).rename(columns={"TotalVolumeTrade": "volume"})
    minuteData = minuteData.set_index(["MDDate", "MDTime"]).loc[:, ["volume"]]

    dailyVolumeDF = minuteData.groupby(level=0).apply(getDailyVolumeSeries, sxw=sxw)
    dailyVolumeDF = dailyVolumeDF["volume"].unstack(level=1)
    dailyVolumeDF = dailyVolumeDF[dailyVolumeDF.sum(axis=1) > 0]
    dailyVolumeDF = dailyVolumeDF.rolling(period).sum()
    dailyVolumeDF = dailyVolumeDF.iloc[-1]

    targetQtyPctSeries = (dailyVolumeDF / dailyVolumeDF.sum()).cumsum()
    return targetQtyPctSeries.values


res = generateTimetableAndTargetQtyInterval('000001.SZ', -6000, 20201026, 20, '1000')
