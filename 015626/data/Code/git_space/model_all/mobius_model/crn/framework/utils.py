import os
import torch
import pickle
import random
import numpy as np


def erase_daily_gaps(x, t):
    x = x.copy()
    i = x.groupby(x.index.date).head(t).index
    x.loc[i] = np.nan
    return x


def create_data_mask(x):
    m = x.notna().astype('float')
    return m


def normalize_return(x):
    lower_limit = x.quantile(q=0.005)
    upper_limit = x.quantile(q=0.995)
    x = x.clip(lower=lower_limit, upper=upper_limit)
    x = x / x.std()
    return x


def fill_inf_and_nan(x):
    x = x.replace([np.inf, -np.inf], np.nan)
    x = x.fillna(0.0)
    return x


def convert_to_prob(x, a):
    if a is None:
        p = (x > 0).astype(x.dtype)
    else:
        p = 1.0 / (1.0 + np.exp(-1.0 * a * x))
    return p


def set_random_seed(seed):
    os.environ['PYTHONHASHSEED'] = str(seed)  # python seed
    random.seed(seed)  # random seed
    np.random.seed(seed)  # numpy seed
    torch.manual_seed(seed)  # pytorch cpu seed
    torch.cuda.manual_seed(seed)  # pytorch gpu seed
    torch.cuda.manual_seed_all(seed)  # pytorch gpu seed
    return None


def save_pickle(data, path):
    with open(path, mode='wb') as file:
        pickle.dump(data, file)
    return None


def load_pickle(path):
    with open(path, mode='rb') as file:
        data = pickle.load(file)
    return data
