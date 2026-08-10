from datetime import datetime
from xquant.factordata import FactorData

import os


def serialize_to_file(content: str, filepath: str):
    with open(filepath, 'wb') as f:
        f.write(content.encode("utf-8"))


def format_date(input_date):
    date = datetime.strptime(input_date, "%Y%m%d")
    fdate = date.strftime('%Y-%m-%d')
    return fdate

def get_trading_days(base_date, lag):
    fd_service = FactorData()
    all_dates = fd_service.tradingday(base_date, lag)
    return all_dates

def get_next_trading_day(base_date):
    all_dates = get_trading_days(base_date, 2)
    if all_dates[0] == base_date:
        return all_dates[1]
    else:
        return all_dates[0]