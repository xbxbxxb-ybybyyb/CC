import os
from multifactor.data.utils import check_update_date
from xquant.xqutils.helper import link


sdate,edate,cdate_list = check_update_date()

if len(os.listdir('/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/%s/'%edate)) >= 26:
    lm = link.LinkMessage()
    lm.sendMessage('SUCCESS !!!')
    del lm
else:   
    lm = link.LinkMessage()
    lm.sendMessage('SOMETHING WENT WRONG !!!')
    del lm