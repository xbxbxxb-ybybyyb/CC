import json
import os
import numpy as np
import pandas as pd
from loguru import logger
import zstd
import struct
import copy
import xdb.factordata as xdbFactorData
from xquant.factordata import FactorData


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


def get_history_price(ticker, end_date, offset):
    contract_root = '/dfs/group/900001/XDB/00_MarketData/02_FutureData/02_UHFData/03_CCFX/10_ContractInfo/'
    s = FactorData()
    dates = s.tradingday(end_date, -255)

    data_list = []
    counter = 1
    while counter < len(dates):    
        data = get_contract_from_xdb(contract_root + dates[counter - 1] + "/contract_univ", "IndexDF")
        if data is None or data.empty:
            counter = counter + 1
            continue
        contracts = data[data['Ticker'] == ticker + '.CF']['contract_00'].values

        if len(contracts) != 1:
            logger.error("date={} has no contract 00", dates[counter])
        else:
            col = 'twap' if ticker == "IM" else "close"

            data = read_indicator_from_xdb(col, dates[counter], ticker, contracts[0], offset)
            if data is None or data.empty:
                counter = counter + 1
                continue
            data_list.append(data)
        counter = counter + 1
    return pd.concat(data_list, axis=0)


def get_signal(signal_group_name, end_date, offset):
    s = FactorData()
    date_list = s.tradingday(end_date, -254)
    data_list = []
    for date in date_list:
        file_path = f'/dfs/user/666466/03_mobius/02_FactorData/{date}/offset_{offset}/03_signal/{signal_group_name}/raw/{date}'
        if not os.path.exists(file_path):
            logger.warning("file={} not exist", file_path)
            continue
        s = xdbFactorData.FactorData()
        data = s.get_factor_from_path(date, "Mobius", file_path)
        res_data = copy.deepcopy(data)
        res_data.drop(axis=1, columns=['timestamp'], inplace=True)
        res_data.index = [pd.Timestamp(str(x)) for x in data['timestamp']]
        res_data.index.name = 'dt'
        data_list.append(res_data)

    return pd.concat(data_list, axis=0)


def get_index_list(minute_ret, minute_std, data_end_date, num_samples, min_quantile, max_quantile):
    assert len(minute_ret[:data_end_date]) >= num_samples
    assert len(minute_std[:data_end_date]) >= num_samples
    minute_ret = minute_ret[:data_end_date].tail(num_samples)
    minute_std = minute_std[:data_end_date].tail(num_samples)

    min_std = minute_std.quantile(min_quantile)
    max_std = minute_std.quantile(max_quantile)

    select_pos = (minute_ret > 0) & (minute_std > min_std) & (minute_std < max_std)
    select_neg = (minute_ret < 0) & (minute_std > min_std) & (minute_std < max_std)
    select_num = min(select_pos.sum(), select_neg.sum())
    select_pos = select_pos[select_pos].tail(select_num)
    select_neg = select_neg[select_neg].tail(select_num)

    index_list = select_pos.index.to_list() + select_neg.index.to_list()
    index_list.sort()
    return index_list


def rank_index(date_list, variety, offset):
    # sample parameters
    num_samples = 60000
    min_quantile = 0.25
    max_quantile = 0.75

    ticker_signal_dict = {}
    if offset == '0':
        #ticker_signal_dict = {'IM': ['20250328_im_im_v1unifac', '20250328_im_im_v1unifac_crn', '20240628_im_im_v1unifac'],
        #                      "IC": ['20250328_ic_ic_v7unifac', '20250328_ic_ic_v7unifac_crn'],
        #                      "IF": ['20250328_if_if_v7c', '20250328_if_if_v7_crn']}
        ticker_signal_dict = {'IM': ['20250328_im_im_v1_crn_ew', '20250328_im_im_v1unifac_crn_trend', '20250328_im_im_v1unifac', '20250328_im_im_v1unifac_crn', '20240628_im_im_v1unifac'],
                              "IC": ['20250328_ic_ic_v7_crn_ew', '20250328_ic_ic_v7unifac_crn_trend','20250328_ic_ic_v7unifac', '20250328_ic_ic_v7unifac_crn'], 
                              "IF": ['20250328_if_if_v7_crn_ew',  '20250328_if_if_v7_crn_trend','20250328_if_if_v7c', '20250328_if_if_v7_crn']}
    else:
        ticker_signal_dict = {'IC': ['20241213_ic_ic_v7unifac', '20241213_ic_ic_v7unifac_crn'], 'IF': ['20241213_if_if_v7c', '20241213_if_if_v7_crn'], 'IM':['20241213_im_im_v1unifac_crn', '20241213_im_im_v1unifac']}

    for ticker, signal_group_list in ticker_signal_dict.items():
        if ticker != variety:
            continue
        for sample_date in date_list:
            s = FactorData()
            next_day = s.tradingday(sample_date, 2)[1]
            # set output path
            # for offset in offset_list:
            price = get_history_price(ticker, sample_date, offset=offset)

            for signal_group in signal_group_list:
                minute_ret = price.groupby(price.index.date).apply(lambda x: x.pct_change(5, fill_method=None).shift(-6))
                minute_std = price.groupby(price.index.date).apply(
                    lambda x: x.pct_change(1, fill_method=None).rolling(30, min_periods=30, center=True).std())

                sample_date = str(sample_date)
                # data_end_date = (pd.Timestamp(sample_date) - pd.Timedelta(days=1)).strftime('%Y%m%d')
                output_root = f'/dfs/user/666466/03_mobius/02_FactorData/{next_day}/offset_{offset}/03_signal/{signal_group}/history_files/signalNorm2Value'
                os.makedirs(output_root, exist_ok=True)

                index_list = get_index_list(minute_ret, minute_std, next_day, num_samples, min_quantile, max_quantile)

                signal_data = get_signal(signal_group, sample_date, offset)
                dest_data = signal_data.loc[index_list]
                fw = open(os.path.join(output_root, sample_date), 'w')
                for col in list(dest_data.columns):
                    dest_data[col] = dest_data[col].astype('float64')
                    signal_value_list = list(dest_data[col].sort_values(ascending=True).values)
                    logger.info('signal_raw={}, value_size={}', col, len(signal_value_list))
                    factor_dict = {'SignalName': col, 'Values': signal_value_list}
                    s = json.dumps(factor_dict)
                    fw.write(s + '\n')
                logger.info("write to {}", os.path.join(output_root, sample_date))
                fw.close()
    return None


if __name__ == '__main__':
    s = FactorData()
    trading_list = s.tradingday('20250331', -11)
    trading_list = ['20250328']
    rank_index(trading_list, "IC", '0')
    rank_index(trading_list, "IF", '0')
    rank_index(trading_list, "IM", '0')


