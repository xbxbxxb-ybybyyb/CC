import pandas as pd
import numpy as np
import os

class FactorGenerator:
    __data__ = None
    def __init__(self, lookback_bars = 5000, required_columns = None):
        self.lookback_bars = lookback_bars
        self.required_columns = required_columns

    @classmethod
    def prepare_hot_data(inst, data):
        data_dict = {}
        for col in data.columns:
            data_dict[col] = data[col].copy()
        inst.__data__ = data_dict

    def slicer(self):
        return {col:self.__data__[col].copy() for col in self.required_columns}

    def __callback__(self):
        data = self.slicer()
        factor = self.on_bar(data)
        return factor