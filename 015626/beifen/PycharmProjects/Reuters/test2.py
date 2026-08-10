import datetime as dt
import pandas as pd
import scipy.io as sio
import os
import numpy as np
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multiprocessing import Pool, Process, Manager
from multifactor.data.utils import *
import logging
from log import Log
import multifactor.utility.dt as tdt
import pickle
import pyodbc
from dateutil.parser import parse

data = IO.read_data([20190829,20191020], alt = r'Z:/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
print(data)