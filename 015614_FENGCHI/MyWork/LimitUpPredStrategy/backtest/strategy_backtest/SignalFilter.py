# author: kiki_777
# date: 2021/7/27

import pandas as pd
import numpy as np
from LimitUpPredStrategy.dataApi import getData, tradeDate, stockList
from LimitUpPredStrategy.dataApi.tradeDate import get_date_range
from LimitUpPredStrategy.dataApi.stockList import trans_windcode2int,trans_datetime2int,trans_int2windcode
from LimitUpPredStrategy.dataApi.getData import get_minute_1factor,get_daily_1factor

trade_minute = [
    925, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948,
    949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008,
    1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027,
    1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046,
    1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1100, 1101, 1102, 1103, 1104, 1105,
    1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124,
    1125, 1126, 1127, 1128, 1129, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310, 1311, 1312, 1313,
    1314, 1315, 1316, 1317, 1318, 1319, 1320, 1321, 1322, 1323, 1324, 1325, 1326, 1327, 1328, 1329, 1330, 1331, 1332,
    1333, 1334, 1335, 1336, 1337, 1338, 1339, 1340, 1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351,
    1352, 1353, 1354, 1355, 1356, 1357, 1358, 1359, 1400, 1401, 1402, 1403, 1404, 1405, 1406, 1407, 1408, 1409, 1410,
    1411, 1412, 1413, 1414, 1415, 1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424, 1425, 1426, 1427, 1428, 1429,
    1430, 1431, 1432, 1433, 1434, 1435, 1436, 1437, 1438, 1439, 1440, 1441, 1442, 1443, 1444, 1445, 1446, 1447, 1448,
    1449, 1450, 1451, 1452, 1453, 1454, 1455, 1456, 1457, 1458, 1459, 1500
]


class SignalFilter(object):

    def __init__(self, start_date, end_date, signal_address, method, time_lag):

        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        signal = pd.read_pickle(signal_address)
        self.start_date = start_date
        self.end_date = end_date
        self.date_list = date_list
        self.signal = signal
        self.method = method
        self.time_lag = time_lag

    def data_prepare(self):

        close_min = get_minute_1factor('close', start_datetime=self.start_date, end_datetime=self.end_date)
        high_min = get_minute_1factor('high', start_datetime=self.start_date, end_datetime=self.end_date)
        low_min = get_minute_1factor('low', start_datetime=self.start_date, end_datetime=self.end_date)

        limit_max = get_daily_1factor('limit_max', date_list=self.date_list)
        limitmax_min = pd.DataFrame(limit_max.loc[high_min.get_index_level_values('date'), high_min.columns].values,
                                    index=high_min.index, columns=high_min.columns)

        zf_3m = high_min.rolling(3).max()/low_min.rolling(3).min()-1

        return zf_3m

    def signal_filter(self):

        if self.method == '去除快速拉升':

            zf_3m = self.data_prepare()

            sz50_member = (get_daily_1factor('SZ50_exdiv_weight') > 0)
            sz50_member = pd.DataFrame(sz50_member.shift(1).loc[zf_3m.index.get_level_values('date')].values,
                                       index=zf_3m.index, columns=sz50_member.columns)

            self.signal['zf_3m'] = zf_3m.stack().reset_index().rename(columns={'level_2': 'stk_id'}).set_index(['date', 'stk_id', 'time']).loc[self.signal.index]
            self.signal['is_sz50_member'] = sz50_member.astype(int).stack().reset_index().rename(columns={'level_2': 'stk_id'}).set_index(['date', 'stk_id', 'time']).loc[self.signal.index]

            self.signal.loc[((self.signal['zf_3m'] > 0.04) & (self.signal['is_sz50_member'] == 0)) |
                            ((self.signal['zf_3m'] > 0.02) & (self.signal['is_sz50_member'] == 1)), 'signal'] = 0

            self.signal = self.signal.reset_index()
            self.signal['time'] = [trade_minute[trade_minute.index(x) + 1]*100 for x in self.signal['time']]

        elif self.method == '延迟下单':

            self.signal = self.signal.reset_index().rename(columns={'level_2': 'stk_id'})
            self.signal['time'] = [trade_minute[trade_minute.index(x) + self.time_lag]*100 for x in self.signal['time']]

        else:
            pass

        return self.signal.set_index(['date', 'stk_id', 'time'])








