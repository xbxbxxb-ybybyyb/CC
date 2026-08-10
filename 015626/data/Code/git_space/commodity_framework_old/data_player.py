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

            for i in range(len(self.today_index)):
                yield pd.concat([history_data, today_data.iloc[:i + 1]])

       