from multiprocessing.pool import Pool
import datetime
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import os
import numpy as np
from arrow.naming_config import *
from arrow.utility import *
import re


class HotData:
    def __init__(self, ref_date=None):
        if ref_date is None:
            ref_date = pd.Timestamp.now().date()
        self.ref_date = IO.str_date_parser(ref_date).strftime('%Y%m%d')

    # 记得处理transaction中的bsflag
    def get_all(self):
        return pd.read_pickle(os.path.join(hot_root, self.ref_date, 'hot.pkl'))
