import pandas as pd
import numpy as np
from data_center import DataCenter
import os

class DataPlayer(object):
    def __init__(self, date, days_past, data_type, data, today_index, handle_preadj):
        self.date = date
        self.days_past = days_past
        self.data_type = data_type
        self.prepared_data = data
        self.today_index = today_index
        self.handle_preadj = handle_preadj

    @property
    def today_data_generator(self):
        if self.data_type == 'Future':
            date_list = np.unique(self.prepared_data.index.date)
            if len(date_list) == 1:
                history_data = pd.DataFrame()
            else:
                history_data = self.prepared_data.loc[:date_list[-2].strftime('%Y%m%d')]
            today_data = self.prepared_data.loc[date_list[-1].strftime('%Y%m%d')]

            yield pd.concat([history_data, today_data])

        elif self.data_type == 'IndexStock':
            date_list = np.unique(self.prepared_data[list(self.prepared_data.keys())[0]].index.date)
            today_data = {k: v.loc[date_list[-1].strftime('%Y%m%d')] for k, v in self.prepared_data.items()}
            # print(today_data.keys())

            data_cols = set(today_data.keys())
            # 目前需要前复权的5个字段
            adj_price_cols = list(data_cols & {'open', 'high', 'low', 'close'})
            adj_volume_cols = list(data_cols & {'volume'})

            if len(date_list) > 1:
                history_data = {k:v.loc[date_list[0].strftime('%Y%m%d'):date_list[-2].strftime('%Y%m%d')] for k,v in self.prepared_data.items()}

                # 复权
                if self.handle_preadj:

                    today_adj = today_data['adjfactor']
                    history_adj = history_data['adjfactor']

                    history_daynum = len(date_list) - 1
                    adj = pd.DataFrame(history_adj.values / np.tile(today_adj.values,(history_daynum,1)), index=history_adj.index, columns=history_adj.columns)
                    adj[adj >= (1/1.08)] = 1

                    if len(adj_price_cols) > 0:
                        for k in adj_price_cols:
                            history_data['%s_preadj' % k] = history_data[k] * adj
                            today_data['%s_preadj' % k] = today_data[k]
                    if len(adj_volume_cols) > 0:
                        for k in adj_volume_cols:
                            history_data['%s_preadj' % k] = history_data[k] / adj
                            today_data['%s_preadj' % k] = today_data[k]

                    for k in adj_price_cols + adj_volume_cols:
                        del history_data[k]
                        del today_data[k]

            else:
                if self.handle_preadj:
                    print('preadj processing')
                    for k in adj_price_cols + adj_volume_cols:
                        today_data['%s_preadj' % k] = today_data[k]
                        del today_data[k]

            played_data = {}
            for k in today_data.keys():
                if len(date_list) == 1:
                    played_data[k] = today_data[k]
                else:
                    played_data[k] = history_data[k].append(today_data[k])
            yield played_data

        elif self.data_type == 'IndexStock_tick':
            stock_list = list(self.prepared_data.keys())

            played_data = {}
            for stock in stock_list:
                sdf = self.prepared_data[stock]
                if len(sdf) <= 0:
                    continue
                date_list = np.unique(sdf.index.date)

                today_data = sdf.loc[date_list[-1].strftime('%Y%m%d')]

                data_cols = set(today_data.columns.tolist())
                # 目前需要前复权的5个字段
                adj_price_cols = list(data_cols & {'LastPx_tick'})
                adj_volume_cols = list(data_cols & {'volume_tick'})

                if len(date_list) > 1:
                    history_data = sdf.loc[date_list[0].strftime('%Y%m%d'):date_list[-2].strftime('%Y%m%d')]
                    # 复权
                    if self.handle_preadj:

                        today_adj = today_data['adjfactor_tick'].iloc[0]
                        history_adj = history_data['adjfactor_tick']

                        adj = pd.DataFrame(history_adj.values / today_adj, index=history_adj.index)
                        adj[adj >= (1/1.08)] = 1

                        if len(adj_price_cols) > 0:
                            for k in adj_price_cols:
                                adj.columns = [k]
                                history_data['%s_preadj' % k] = history_data[[k]] * adj
                                today_data['%s_preadj' % k] = today_data[k]
                        if len(adj_volume_cols) > 0:
                            for k in adj_volume_cols:
                                adj.columns = [k]
                                history_data['%s_preadj' % k] = history_data[[k]] / adj
                                today_data['%s_preadj' % k] = today_data[k]

                        for k in adj_price_cols + adj_volume_cols:
                            del history_data[k]
                            del today_data[k]

                else:
                    if self.handle_preadj:
                        for k in adj_price_cols + adj_volume_cols:
                            today_data['%s_preadj' % k] = today_data[k]
                            del today_data[k]

                if len(date_list) == 1:
                    played_data[stock] = today_data
                else:
                    played_data[stock] = history_data.append(today_data)

            yield played_data

