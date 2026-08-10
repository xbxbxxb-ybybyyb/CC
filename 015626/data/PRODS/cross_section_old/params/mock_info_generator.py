import os
from datetime import datetime

import pandas as pd
from loguru import logger
from xquant.factordata import FactorData


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


def format_date(input_date):
    date = datetime.strptime(input_date, "%Y%m%d")
    fdate = date.strftime('%Y-%m-%d')
    return fdate


class MockInfoGenerator:
    def __init__(self):
        self.indicator_dir = r'/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_STOCK/MINUTE'

    def get_symbol_mock_info(self, symbol, cmp_date):
        h5_symbol_file = symbol + ".h5"
        cmp_fdate = format_date(cmp_date)
        next_trading_date = get_next_trading_day(cmp_date)
        nxt_fdate = format_date(next_trading_date)
        locate_err_symbols = []
        try:
            # df = df.loc['{} 09:30:00'.format(cmp_fdate): '{} 14:56:00'.format(cmp_fdate), py_stock_indicators]
            indicator_path = os.path.join(self.indicator_dir, h5_symbol_file)
            h5_store = pd.HDFStore(indicator_path)
            df = h5_store.select(symbol, where="dt>'{}'&dt<'{}'".format(cmp_fdate, nxt_fdate))
            h5_store.close()
        except:
            locate_err_symbols.append(symbol)
            logger.error("Symbol {} h5 file index locate error", symbol)
        df = df.droplevel('Ticker')
        s = datetime.strptime(cmp_date + '0930', '%Y%m%d%H%M')
        e = datetime.strptime(cmp_date + '1456', '%Y%m%d%H%M')
        df1 = df.loc[str(s):str(e)]
        df1 = df1.reset_index()
        if len(df1) > 0:
            return df1['weight'][0], df1['float_shares'][0]
        else:
            logger.error("Symbol {} data not exists, date={}", symbol, cmp_date)
            return None, None


if __name__ == "__main__":
    base_path = "/data/user/018728/cpp_projects/csi_calculator/testcase"
    symbol = '688041.SH'
    cmp_date = '20231226'
    generator = MockInfoGenerator()
    weight = generator.get_symbol_mock_info(symbol, cmp_date)
    print(weight)
