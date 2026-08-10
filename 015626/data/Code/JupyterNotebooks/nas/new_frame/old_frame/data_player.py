import pandas as pd
import numpy as np
# from get_data import *
from data_center import DataCenter

class DataPlayer(object):
    def __init__(self, date, days_past, data_type, data, today_index):
        self.date = date
        self.days_past = days_past
        self.data_type = data_type
        self.prepared_data = data
        self.today_index = today_index

    @property
    def today_data_generator(self):
        if self.data_type == 'Future':
            date_list = np.unique(self.prepared_data.index.date)
            if len(date_list) == 1:
                history_data = pd.DataFrame()
            else:
                history_data = self.prepared_data.loc[:date_list[-2].strftime('%Y%m%d')]
            today_data = self.prepared_data.loc[date_list[-1].strftime('%Y%m%d')]

            for i in range(len(self.today_index)):
                yield pd.concat([history_data, today_data.iloc[:i + 1]])

        elif self.data_type == 'IndexStock':
            date_list = np.unique(self.prepared_data[list(self.prepared_data.keys())[0]].index.date)

            for i in range(len(self.today_index)):
                played_data = {}
                for k,v in self.prepared_data.items():
                    if len(date_list) == 1:
                        played_data[k] = v.iloc[:i+1]
                    else:
                        played_data[k] = v.loc[date_list[0].strftime('%Y%m%d'):date_list[-2].strftime('%Y%m%d')].append(v.loc[date_list[-1].strftime('%Y%m%d')].iloc[:i+1])
                yield played_data