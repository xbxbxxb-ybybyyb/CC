from ts_factor.factor_generator import FactorGenerator
from ts_factor.wyc_ts1_future import wyc_ts1_future
import pandas as pd

FactorGenerator(required_columns=['close','volume'],lookback_bars=5000).prepare_hot_data()

for subclass in FactorGenerator.__subclasses__():
    inst = subclass()
    df = inst.__callback__()
    print(df)