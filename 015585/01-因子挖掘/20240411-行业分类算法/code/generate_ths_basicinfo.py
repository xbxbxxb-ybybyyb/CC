import pandas as pd
import numpy as np
import os
import IO
from datetime import datetime
from xquant.thirdpartydata.fic_api_data import FicApiData

fad = FicApiData()
# totalCount = 74042
resource = "ZX_CONCEPTION"
paramMaps = {}
orderBy = ""
rownum = 100
startrow = 0
#
result_dict = fad.get_fic_api_data(resource, paramMaps, startrow=startrow, rownum=rownum,
                               orderBy=orderBy)
res = pd.DataFrame(result_dict['data'])