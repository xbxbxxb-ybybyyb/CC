import numpy as np
import pandas as pd
from help_functions_wsc import *
from future_factor import FutureFactor


def type_convertor(func):
    """
    与operators文件中的算子相配套，用于调整输出的数据格式，使之与输入的数据格式相一致
    """
    def wrapper(*args, **kwargs):
        data = args[0]
        if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
            raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
        output = func(*args, **kwargs)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(output, index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(output, index=data.index, name=data.name)
        return output
    return wrapper


@type_convertor
def ts_position(data, d):
    if not isinstance(data, np.ndarray):
        data = data.values
    data_expanding = rolling_window_upgrade(data, d)
    output_need = (data_expanding[...,-1] - np.nanmin(data_expanding, axis=-1)) / (np.nanmax(data_expanding, axis=-1) - np.nanmin(data_expanding, axis=-1))
    output = np.full(data.shape, np.nan)
    output[d - 1:] = output_need
    return output


class wyc_fast1_spot(FutureFactor):

    data_type = 'Future' 
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 237 * 3
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-50:]

        factor = ts_position(spot_close, 50)
        return factor[-1]