from xquant.factordata import FactorData
from IO_enums import *
from new_mapping import wind_dt_mapping
from new_mapping import overwrite_wind_dt
import datetime
from new_mapping.suntime_dt_mapping import get_suntime_dat_fig
import pandas as pd
# pd.set_option("display.max_columns",None)

today = datetime.date.today()
date_str = today.strftime("%Y-%m-%d")
s = FactorData()
wind_map = wind_dt_mapping.wind_dat_fig_dict
overwrite_tables = overwrite_wind_dt.overwrite_wind_table


def ticker_match(ticker_num):  # jit slow
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num >= 600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num))) * '0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker

#主要为了处理AShareMainandnoteitems
def get_longtable(table_name, canshu_map=None):
    if canshu_map == None:
        df1 = s.get_factor_value(table_name, OPDATE=["<20180401"])
        df2 = s.get_factor_value(table_name, OPDATE=[">=20180401", "<20180501"])
        df3 = s.get_factor_value(table_name, OPDATE=[">=20180501", "<20190101"])
        df4 = s.get_factor_value(table_name, OPDATE=[">=20190101", "<20190601"])
        df5 = s.get_factor_value(table_name, OPDATE=[">=20190601"])
        df = pd.concat([df1, df2, df3, df4, df5], axis=0)
    else:
        df1 = s.get_factor_value(table_name, OPDATE=["<20180401"], **canshu_map)
        df2 = s.get_factor_value(table_name, OPDATE=[">=20180401", "<20180501"], **canshu_map)
        df3 = s.get_factor_value(table_name, OPDATE=[">=20180501", "<20190101"], **canshu_map)
        df4 = s.get_factor_value(table_name, OPDATE=[">=20190101", "<20190601"], **canshu_map)
        df5 = s.get_factor_value(table_name, OPDATE=[">=20190601"], **canshu_map)
        df = pd.concat([df1, df2, df3, df4, df5], axis=0)
    return df

def read_data(trading_days, columns=None, universe=None, mkttype=MktType.CHINA, dtype=DType.STOCK,
              ftype=FType.MD, dfreq=DFreq.DAILY, dsource=DSource.HTSC, alt=None, h5root=None, max_workers=1):
    mkttype = mkttype.name
    dtype = dtype.name
    ftype = ftype.name
    dfreq = dfreq.name
    dsource = dsource.name
    table_name = ""
    ziduan_map = {}

    # get tablename
    if alt is not None:
        alt_list = alt.split("/")
        if alt_list[-3] == "WIND":
            table_name = "WIND_" + alt_list[-1][:-3]

        elif alt_list[-3] == "SUNTIME":
            table_name = "GOGOAL_" + alt_list[-1][:-3].upper()
    else:
        table_name = dsource + "_" + '_'.join([ftype, mkttype, dtype, dfreq, dsource])

    # 处理columns参数
    if type(columns) is not list and columns is not None:
        columns = [columns]

    # 处理trading_days参数
    if type(trading_days) is not list:
        trading_days = [trading_days]
    elif len(trading_days) == 2:
        trading_days = [">=" + str(trading_days[0]), "<=" + str(trading_days[1])]

    # WIND
    if "WIND" in table_name:
        ziduan_map = wind_map[table_name] if table_name in wind_map else {'dt': 'TRADE_DT', 'Ticker': 'S_INFO_WINDCODE'}

        if table_name not in overwrite_tables:
            if universe is None:
                if columns is None:
                    canshu_map = {ziduan_map["dt"]: trading_days}
                    df = s.get_factor_value(table_name, **canshu_map)
                else:
                    canshu_map = {ziduan_map["dt"]: trading_days, "factors": columns + list(ziduan_map.values())}
                    df = s.get_factor_value(table_name, **canshu_map)
            elif len(ziduan_map) == 1:
                raise KeyError(table_name + " 表没有universe参数")
            else:
                if columns is None:
                    canshu_map = {ziduan_map["dt"]: trading_days, ziduan_map["Ticker"]: universe}
                    df = s.get_factor_value(table_name, **canshu_map)
                else:
                    canshu_map = {ziduan_map["dt"]: trading_days, ziduan_map["Ticker"]: universe,
                                  "factors": columns + list(
                                      ziduan_map.values())}
                    df = s.get_factor_value(table_name, **canshu_map)
            # 空表直接返回
            if len(df) == 0:
                return df
            else:
                if table_name in wind_map:
                    rename_map = dict((v, k) for k, v in ziduan_map.items())
                else:
                    rename_map = {'TRADE_DT': 'dt', 'S_INFO_WINDCODE': 'Ticker'}
                sort_list = ["dt", "Ticker"] if len(rename_map) == 2 else ["dt", "OBJECT_ID"]
                df = df.rename(rename_map, axis=1).sort_values(by=sort_list)
                df["dt"] = df["dt"].apply(lambda x: str(x[:4]) + "-" + str(x[4:6]) + "-" + x[6:] if len(x) == 8 else x)
                res = df.set_index(sort_list)

        # overwrite的，dt和ticker为index
        elif len(ziduan_map) == 2:
            ziduan_map.__delitem__("dt")
            if universe is None:
                if columns is None:
                    try:
                        df = s.get_factor_value(table_name)
                    except:
                        df = get_longtable(table_name)
                else:
                    canshu_map = {"factors": columns + list(ziduan_map.values())}
                    try:
                        df = s.get_factor_value(table_name, **canshu_map)
                    except:
                        df = get_longtable(table_name, canshu_map)
            else:
                if columns is None:
                    canshu_map = {ziduan_map["Ticker"]: universe}
                    df = s.get_factor_value(table_name, **canshu_map)
                else:
                    canshu_map = {ziduan_map["Ticker"]: universe, "factors": columns + list(ziduan_map.values())}
                    df = s.get_factor_value(table_name, **canshu_map)
            # 空表直接返回
            if len(df) == 0:
                return df
            else:
                df["dt"] = date_str
                rename_map = dict((v, k) for k, v in ziduan_map.items())
                df = df.rename(rename_map, axis=1).sort_values(by=["dt", "Ticker"])
                df["dt"] = df["dt"].apply(lambda x: str(x[:4]) + "-" + str(x[4:6]) + "-" + x[6:] if len(x) == 8 else x)
                res = df.set_index(["dt", "Ticker"])

        # overwrte的，只有一个dt index，需要设置object为另一个index
        else:
            if universe is not None:
                raise KeyError(table_name + " 表没有universe参数")
            else:
                if columns is None:
                    df = s.get_factor_value(table_name)
                else:
                    canshu_map = {"factors": columns + ["OBJECT_ID"]}
                    df = s.get_factor_value(table_name, **canshu_map)
                # 空表直接返回
                if len(df) == 0:
                    return df
                else:
                    df["dt"] = date_str
                    df = df.sort_values(by=["dt", "OBJECT_ID"])
                    res = df.set_index(["dt", "OBJECT_ID"])

        return res

    # 朝阳永续，没有overwrite的
    if "GOGOAL" in table_name:
        ziduan_map = get_suntime_dat_fig(table_name[7:].lower())
        # index为日期和股票
        if universe is None:
            if columns is None:
                canshu_map = {ziduan_map["dt"]: trading_days}
                df = s.get_factor_value(table_name, **canshu_map)
            else:
                canshu_map = {ziduan_map["dt"]: trading_days, "factors": columns + list(ziduan_map.values())}
                df = s.get_factor_value(table_name, **canshu_map)

        elif len(ziduan_map) == 1:
            raise KeyError(table_name + " 表没有universe参数")

        else:
            if columns is None:
                canshu_map = {ziduan_map["dt"]: trading_days, ziduan_map["Ticker"]: universe}
                df = s.get_factor_value(table_name, **canshu_map)
            else:
                canshu_map = {ziduan_map["dt"]: trading_days, ziduan_map["Ticker"]: universe, "factors": columns + list(
                    ziduan_map.values())}
                df = s.get_factor_value(table_name, **canshu_map)

        # 处理df，空表直接返回
        if len(df) == 0:
            return df
        else:
            rename_map = dict((v, k) for k, v in ziduan_map.items())
            sort_list = ["dt", "Ticker"] if len(rename_map) == 2 else ["dt", "ID"]
            df = df.rename(rename_map, axis=1).sort_values(by=sort_list)
            df["dt"] = df["dt"].map(
                lambda x: x[:10] if ziduan_map["dt"] == "ENTRYDATE" else str(x)[:4] + "-" + str(x)[
                                                                                            4:6] + "-" + str(x)[
                                                                                                         6:])
            if "Ticker" in sort_list:
                df["Ticker"] = df["Ticker"].map(lambda x: ticker_match(x))
            res = df.set_index(sort_list)
            return res


if __name__ == "__main__":
    path = '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareIllegality/AShareIllegality.h5'
    df = read_data(alt=path, trading_days=[20190601, 20190909])
    print(df)
