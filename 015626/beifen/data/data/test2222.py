import pandas as pd
from WindPy import *
import numpy as np
import datetime as dt
import math
import random

random.seed(123)
w.start()

data = w.wset("bonus", "orderby=报告期;year=%s;period=y1;sectorid=a001010100000000" % (str(2018 - 1)))

print(data)
print(pd.DataFrame(data.Data).T)