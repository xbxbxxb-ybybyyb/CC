
# coding: utf-8

# In[26]:


import IO
start_date,end_date=20201201,20201203 #输入起止日期
#分钟收盘价
min_close=IO.read_data([start_date,end_date],alt='/data/group/800463/data/minute_close.h5')
#指数成分股
zz1000=IO.read_data([start_date,end_date],columns=['index_1000'],alt='/data/group/800080/warehouseJG/prod/UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5')
min_close['index_1000']=zz1000['index_1000']
min_close=min_close[min_close['index_1000']]

