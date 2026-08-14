import struct
import pandas as pd
import numpy as np
import zstd
import os
# 201905
base_dir = "/dfs/group/800463/data/xdb_data_lag3/europa_jupiter/xdb_tickfull/"
file_names_tmp = os.listdir(base_dir)
file_names = [i for i in file_names_tmp if i.startswith('201903')]
output_dir = "/dfs/user/015585/xdb_tickfull/"
for i in file_names:
    df = pd.read_pickle(base_dir + i, compression='gzip')
    symbol_list = list(df.index.get_level_values(1).unique())
    total_header_size = len(symbol_list) * 26
    idx = pd.IndexSlice

    with open(output_dir + i, 'wb') as file:
        file.write(b'12345600')
        file.write(struct.pack('<q', total_header_size))

        headerCurrentIndex = 8 + 8
        start = 8 + 8 + total_header_size
        end = 0
        for symbol in symbol_list:
            cur_df = df.loc[idx[:, [symbol]],]
            if cur_df.empty:
                continue
            symbol_nparr = np.array(cur_df["MDDate"].apply(lambda x: str.encode(x)))
            int_selected = cur_df[[
                "MDTime", "NumTrades", "TotalVolumeTrade", "VolumeTrade",
                'pattern', "TotalBidQty", "TotalOfferQty",
                "Buy1OrderQty", "Buy2OrderQty", "Buy3OrderQty", "Buy4OrderQty","Buy5OrderQty",
                "Buy6OrderQty", "Buy7OrderQty", "Buy8OrderQty", "Buy9OrderQty", "Buy10OrderQty",
                "Buy1NumOrders", "Buy2NumOrders", "Buy3NumOrders", "Buy4NumOrders", "Buy5NumOrders",
                "Buy6NumOrders", "Buy7NumOrders", "Buy8NumOrders", "Buy9NumOrders", "Buy10NumOrders",
                "Sell1OrderQty", "Sell2OrderQty", "Sell3OrderQty", "Sell4OrderQty", "Sell5OrderQty",
                "Sell6OrderQty", "Sell7OrderQty", "Sell8OrderQty", "Sell9OrderQty", "Sell10OrderQty",
                "Sell1NumOrders", "Sell2NumOrders", "Sell3NumOrders", "Sell4NumOrders", "Sell5NumOrders",
                "Sell6NumOrders", "Sell7NumOrders", "Sell8NumOrders", "Sell9NumOrders", "Sell10NumOrders", ]]

            double_selected = cur_df[[
                "TotalValueTrade", "LastPx",
                'ff_shares', 'industry', 'after_not_ul_len', "OpenPx",
                "WeightedAvgBidPx", "WeightedAvgOfferPx", "Buy1Price", "Buy2Price",
                "Buy3Price", "Buy4Price", "Buy5Price", "Buy6Price", "Buy7Price", "Buy8Price", "Buy9Price",
                "Buy10Price",
                "Sell1Price", "Sell2Price", "Sell3Price", "Sell4Price", "Sell5Price", "Sell6Price", "Sell7Price",
                "Sell8Price", "Sell9Price", "Sell10Price"]]
            int_selected_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void), arr=int_selected.values, axis=1)
            double_selected_nparr = np.apply_along_axis(lambda x: np.array(x.tobytes(), dtype=np.void), arr=double_selected.values, axis=1)

            df_nparr = symbol_nparr + int_selected_nparr + double_selected_nparr
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
print(1)

dic_path = {'015585':'/user/015585/xxxx/'}
'/europa/factor_20240229/'

/018107/
date =
for dic_path:
    if exists path:
        shutil.copy(code1,code2)
for