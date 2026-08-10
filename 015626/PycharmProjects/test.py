import sys

sys.path.insert(4, '/data/user/015626/JupyterNotebooks/utils/')
import json, datetime, os, glob
from multiprocessing import Pool
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import numpy as np

print(os.listdir('/data/user/015626'))