import os
import numpy as np
import pandas as pd
from loguru import logger
import zstd
import struct
import toolkit.xdb_reader.xdb.factordata as xdbFactorData


def parse_header(file_stream):
    location_map = {}
    magic_data = file_stream.read(8)

    _header_size = file_stream.read(8)
    _header_size = struct.unpack('q', _header_size)[0]
    _header_count = _header_size // 34
    if _header_count != _header_size / 34:
        logger.error("解析头文件出错：头文件大小不合规。请检查数据文件是否完整。")
        return

    for i in range(_header_count):
        cur_symbol = file_stream.read(34)
        name, mkt, start, end = struct.unpack('<16s2sqq', cur_symbol)

        name = name.decode()
        name = name.rstrip('\x00')
        location_map[name] = {"name": name, "start": start, "end": end}

    return location_map


writer_format = {"IndexDF": [('dt', 'S64'), ('Ticker', 'S64'), ('contract_00', 'S64'), ('contract_main', 'S64'), ('contract_list', 'S64')]}


def get_contract_from_xdb(file_path, read_format):
    if not os.path.exists(file_path):
        logger.warning("xdb file not exists! return empty data frame, file={}", file_path)
        return pd.DataFrame()
    data_format = np.dtype(writer_format.get(read_format))
    file_stream = open(file_path, 'rb')
    location_map = parse_header(file_stream)
    res = pd.DataFrame()
    for k, v in location_map.items():
        loc = location_map[k]
        start = loc["start"]
        end = loc["end"]
        if len(loc["name"]) == 0:
            return pd.DataFrame()
        if end <= start or end < 0 or start < 0:
            return pd.DataFrame()

        file_stream.seek(start, 0)
        _data = file_stream.read(end - start)

        uncompress = zstd.ZSTD_uncompress(_data)

        df = pd.DataFrame(np.frombuffer(uncompress, data_format))

        for fmt in writer_format.get(read_format):
            if fmt[1].startswith("S"):
                df[fmt[0]] = df[fmt[0]].apply(lambda x: x.decode())

        res = pd.concat([res, df])

    return res


def read_indicator_from_xdb(col, date, ticker, recent, offset):
    indicator_root_path = f'/dfs/user/666466/03_mobius/02_FactorData/{date}/offset_{offset}/01_Indicator/'
    file_path = os.path.join(indicator_root_path, f'FS_{ticker.upper()}_1MIN')

    if not os.path.exists(file_path):
        return pd.Series()
    s = xdbFactorData.FactorData()
    data = s.get_factor_from_path(date, recent, file_path)
    res_data = pd.Series(data=data[col].values, index=[pd.Timestamp(str(x)) for x in data['timestamp']])
    res_data.index.name = 'dt'

    return res_data


def read_signal_from_xdb(cols, date, offset, model_group):
    indicator_root_path = f'/dfs/user/666466/03_mobius/02_FactorData/{date}/offset_{offset}/03_signal/{model_group}/norm2'
    file_path = os.path.join(indicator_root_path, date)

    if not os.path.exists(file_path):
        return pd.Series()
    s = xdbFactorData.FactorData()
    data = s.get_factor_from_path(date, "Mobius", file_path)
    res_data = pd.DataFrame(data=data[cols].values, columns=cols, index=[pd.Timestamp(str(x)) for x in data['timestamp']])
    res_data.index.name = 'dt'

    return res_data


def read_signal_from_pickle(date, model_grp, model_name):
    root_path = f'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/{model_grp}/model_value/model_norm2/20250519/'
    file = os.path.join(root_path, f'{model_name}.pkl')
    df = pd.read_pickle(file)
    return df.iloc[-237:]


def read_factor_from_xdb(date, offset):
    indicator_root_path = f'/dfs/user/666466/03_mobius/02_FactorData/{date}/offset_{offset}/02_Factor/norm'
    file_path = os.path.join(indicator_root_path, date)

    if not os.path.exists(file_path):
        return pd.Series()
    s = xdbFactorData.FactorData()
    data = s.get_factor_from_path(date, "Mobius", file_path)
    res_data = pd.DataFrame(data=data.values, columns=data.columns, index=[pd.Timestamp(str(x)) for x in data['timestamp']])
    res_data.index.name = 'dt'

    return res_data


def get_factor_from_pkl(date, factor_name):
    path2 = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm'
    path3 = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm'
    path4 = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm'

    if os.path.exists(os.path.join(path2, f'{factor_name}.h5')):
        df = pd.read_hdf(os.path.join(path2, f'{factor_name}.h5'))
        return df.iloc[-237:]
    elif os.path.exists(os.path.join(path3, f'{factor_name}.h5')):
        df = pd.read_hdf(os.path.join(path3, f'{factor_name}.h5'))
        return df.iloc[-237:]
    elif os.path.exists(os.path.join(path4, f'{factor_name}.h5')):
        df = pd.read_hdf(os.path.join(path4, f'{factor_name}.h5'))
        return df.iloc[-237:]
    else:
        logger.info("{} not found", factor_name)
        return None


if __name__ == '__main__':
    my_data = read_factor_from_xdb('20250516', '0')

    # 以下代码比较xdb信号与业务H5信号的相关性
    # cols = ['20250328_ic_ic_v7unifac']
    # model_name = 'pred_comb2'
    # model_grp = '20250328_ic_ic_v7unifac'
    # date = '20250519'
    # df_my = read_signal_from_xdb(cols, date, '0', model_grp)
    # df_busi = read_signal_from_pickle(date, model_grp, model_name)
    #
    # for col in cols:
    #     print(col + '=' + str(df_busi[col].corr(df_my[col])))
