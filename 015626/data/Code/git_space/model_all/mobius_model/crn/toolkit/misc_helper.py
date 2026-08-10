import torch
import pynvml
import pandas as pd


def get_gpu_version():
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    device = pynvml.nvmlDeviceGetName(handle)
    device = device.decode('utf-8')
    return device


def get_cuda_version():
    cuda = torch.version.cuda
    return cuda


def quarter_last_friday(str_date, end_date):
    dates = pd.date_range(start=str_date, end=end_date, freq='D')
    dates = pd.Series(dates.strftime('%Y%m%d'), index=dates)
    dates = dates.resample('Q').apply(lambda x: x[x.index.weekday == 4][-1]).to_list()
    return dates


def month_last_friday(str_date, end_date):
    dates = pd.date_range(start=str_date, end=end_date, freq='D')
    dates = pd.Series(dates.strftime('%Y%m%d'), index=dates)
    dates = dates.resample('M').apply(lambda x: x[x.index.weekday == 4][-1]).to_list()
    return dates


def print_error(error):
    print('Error: {}'.format(error), flush=True)
    return None
