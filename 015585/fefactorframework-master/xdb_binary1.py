import struct
import pandas as pd
import numpy as np
import zstd
import os

def convert_tick(base_path, date, output_path):
    paths = base_path + "/" + date + ".pkl"
    df = pd.read_pickle(paths, compression='gzip')
    symbol_list = list(df.index.get_level_values(1).unique())
    total_header_size = len(symbol_list) * 26
    idx = pd.IndexSlice

    with open(output_path + "/" + date, 'wb') as file:
        file.write(b'12345600')
        file.write(struct.pack('<q', total_header_size))

        headerCurrentIndex = 8 + 8
        start = 8 + 8 + total_header_size
        end = 0
        for symbol in symbol_list:
            cur_df = df.loc[idx[:, [symbol]],]
            if cur_df.empty:
                continue
            md_date_nparr = np.array(cur_df["MDDate"].apply(lambda x: str.encode(x)))
            int_selected = cur_df[[
                "MDTime", "NumTrades", "TotalVolumeTrade", "VolumeTrade",
                'pattern', "TotalBidQty", "TotalOfferQty",
                "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty", "Buy5OrderQty",
                "Buy6OrderQty", "Buy7OrderQty", "Buy8OrderQty", "Buy9OrderQty", "Buy10OrderQty",
                "Buy1NumOrders", "Buy2NumOrders", "Buy3NumOrders", "Buy4NumOrders", "Buy5NumOrders",
                "Buy6NumOrders", "Buy7NumOrders", "Buy8NumOrders", "Buy9NumOrders", "Buy10NumOrders",
                "Sell1OrderQty", "Sell2OrderQty", "Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
                "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty", "Sell10OrderQty",
                "Sell1NumOrders", "Sell2NumOrders", "Sell3NumOrders", "Sell4NumOrders", "Sell5NumOrders",
                "Sell6NumOrders", "Sell7NumOrders", "Sell8NumOrders", "Sell9NumOrders", "Sell10NumOrders", ]]

            double_selected = cur_df[[
                "TotalValueTrade", "LastPx",
                'ff_shares', 'industry', 'after_not_ul_len', 'pre_close', "OpenPx",
                "WeightedAvgBidPx", "WeightedAvgOfferPx", "Buy1Price", "Buy2Price",
                "Buy3Price", "Buy4Price", "Buy5Price", "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price",
                "Buy10Price",
                "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price", "Sell6Price", "Sell7Price",
                "Sell8Price", "Sell9Price", "Sell10Price"]]
            int_selected_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                     arr=int_selected.values, axis=1)
            double_selected_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                        arr=double_selected.values, axis=1)

            df_nparr = md_date_nparr + int_selected_nparr + double_selected_nparr
            final_nparr = bytes.join(b"", df_nparr)

            compressed = zstd.ZSTD_compress(final_nparr)

            file.write(str.encode(symbol[:6] + '\0' + '\0'))
            file.write(str.encode(symbol[-2:]))
            file.write(struct.pack('<q', start))
            file.write(struct.pack('<q', start + len(compressed)))
            headerCurrentIndex += 26

            file.seek(start, 0)
            file.write(compressed)

            end = start + len(compressed)
            start = end

            file.seek(headerCurrentIndex, 0)

def convert_trade(base_path, date, output_path):
    paths = base_path + "/" + date + ".pkl"
    # paths = "/data/user/015585/01-因子挖掘/999-share/for system/trade/20190924.pkl"
    # paths = "/data/user/015585/01-因子挖掘/999-share/for system/trade/20160226.pkl"

    df = pd.read_pickle(paths, compression='gzip')
    df["TradeBuyNo"] = df["TradeBuyNo"].astype('int64')
    df["TradeSellNo"] = df["TradeSellNo"].astype('int64')
    symbol_list = list(df.index.get_level_values(1).unique())
    total_header_size = len(symbol_list) * 26
    idx = pd.IndexSlice

    with open(output_path + "/" + date, 'wb') as file:
        file.write(b'12345600')
        file.write(struct.pack('<q', total_header_size))

        headerCurrentIndex = 8 + 8
        start = 8 + 8 + total_header_size
        end = 0
        for symbol in symbol_list:
            cur_df = df.loc[idx[:, [symbol]],]
            if cur_df.empty:
                continue
            md_date_nparr = np.array(cur_df["MDDate"].apply(lambda x: str.encode(x)))

            int_selected = cur_df[[
                "MDTime", "TradeIndex", "TradeBuyNo", "TradeSellNo", "TradeType", "TradeBSFlag",
                'TradeQty', "pattern",]]

            double_selected = cur_df[[
                "TradePrice", "TradeMoney",
                'ff_shares', 'industry', 'after_not_ul_len', "pre_close",]]

            int_selected_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                     arr=int_selected.values, axis=1)
            double_selected_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                        arr=double_selected.values, axis=1)

            df_nparr = md_date_nparr + int_selected_nparr + double_selected_nparr
            final_nparr = bytes.join(b"", df_nparr)

            compressed = zstd.ZSTD_compress(final_nparr)

            file.write(str.encode(symbol[:6] + '\0' + '\0'))
            file.write(str.encode(symbol[-2:]))
            file.write(struct.pack('<q', start))
            file.write(struct.pack('<q', start + len(compressed)))
            headerCurrentIndex += 26

            file.seek(start, 0)
            file.write(compressed)

            end = start + len(compressed)
            start = end

            file.seek(headerCurrentIndex, 0)

def convert_order(base_path, date, output_path):
    paths = base_path + "/" + date + ".pkl"
    # paths = "/data/user/015585/01-因子挖掘/999-share/for system/order/20190724.pkl"
    # paths = "/data/user/015585/01-因子挖掘/999-share/for system/order/20160204.pkl"

    df = pd.read_pickle(paths, compression='gzip')
    df["OrderIndex"] = df["OrderIndex"].astype('int64')
    symbol_list = list(df.index.get_level_values(1).unique())
    total_header_size = len(symbol_list) * 26
    idx = pd.IndexSlice

    with open(output_path + "/" + date, 'wb') as file:
        file.write(b'12345600')
        file.write(struct.pack('<q', total_header_size))

        headerCurrentIndex = 8 + 8
        start = 8 + 8 + total_header_size
        end = 0
        for symbol in symbol_list:
            cur_df = df.loc[idx[:, [symbol]],]
            if cur_df.empty:
                continue
            md_date_nparr = np.array(cur_df["MDDate"].apply(lambda x: str.encode(x)))
            if cur_df["OrderType"].dtype == np.object:
                ordertype_nparr = np.array(cur_df["OrderType"].apply(lambda x: str.encode(x)))
            elif cur_df["OrderType"].dtype == np.int64:
                ordertype_nparr = np.array(cur_df["OrderType"].apply(lambda x: str.encode(str(x))))

            int_selected = cur_df[[
                "MDTime", "OrderIndex", "OrderQty", "OrderBSFlag", "pattern"
                ]]

            double_selected = cur_df[[
                "OrderPrice",
                'ff_shares', 'industry', 'after_not_ul_len', "pre_close"]]
            int_selected_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                     arr=int_selected.values, axis=1)
            double_selected_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void),
                                                        arr=double_selected.values, axis=1)

            df_nparr = md_date_nparr + ordertype_nparr + int_selected_nparr + double_selected_nparr
            final_nparr = bytes.join(b"", df_nparr)

            compressed = zstd.ZSTD_compress(final_nparr)

            file.write(str.encode(symbol[:6] + '\0' + '\0'))
            file.write(str.encode(symbol[-2:]))
            file.write(struct.pack('<q', start))
            file.write(struct.pack('<q', start + len(compressed)))
            headerCurrentIndex += 26

            file.seek(start, 0)
            file.write(compressed)

            end = start + len(compressed)
            start = end

            file.seek(headerCurrentIndex, 0)

base_path = '/dfs/group/800463/data/xdb_data_lag3/europa_jupiter/xdb_trade/'
date_list = list(os.listdir(base_path))
date_list = [i.replace('.pkl','') for i in date_list if i.startswith('201903')]
for i in date_list:
    print(i)
    convert_trade(base_path, i, "/dfs/user/015585/20240226_xdb_binary_test/xdb_trade/")
# convert_order("", "20190506", "/data/user/019073/")
# convert_trade("", "20190506", "/data/user/019073/")
print(1)