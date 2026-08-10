
# coding: utf-8

# In[2]:


import pandas as pd
main = pd.read_hdf("/data/group/800445/future_data/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5")
ic_00 = main.groupby(level=0).head(1).reset_index()
if_00 = main.groupby(level=0).head(2).reset_index()
ih_00 = main.groupby(level=0).head(3).reset_index()


# In[3]:


t_00 = main.groupby(level=0).head(4).reset_index()


# In[4]:


filter = ['dt', 'contract_00','contract_main']
ic_value = ic_00[ic_00['Ticker']=='IC.CFE'][filter]
if_value = if_00[if_00['Ticker']=='IF.CFE'][filter]
ih_value = ih_00[ih_00['Ticker']=='IH.CFE'][filter]
t_value = t_00[t_00['Ticker']=='T.CFE'][filter]


# In[5]:


ic_value = ic_value[ic_value['dt']>'2020-11-01']
if_value = if_value[if_value['dt']>'2020-11-01']
ih_value = ih_value[ih_value['dt']>'2020-11-01']
t_value  = t_value[t_value['dt']>'2020-11-01']


# In[6]:


msg = 'date,variety,recent,main\n'
for i in range(0, len(ic_value)):
    strtime =  str(ic_value.iloc[i]['dt'])[0:10]
    #ta = str.split(strtime, '-')
    #for s in ta:
    #    msg = msg + s
    msg = msg + strtime
    msg = msg + ',IC,'
    msg = msg + str(ic_value.iloc[i]['contract_00'])[:-1] + ',' + str(ic_value.iloc[i]['contract_main'])[:-1] + '\n'
    
    strtime = str(if_value.iloc[i]['dt'])[0:10]
    #ta = str.split(strtime, '-')
    #for s in ta:
    #    msg = msg + s
    msg = msg + strtime
    msg = msg + ',IF,'
    msg = msg + str(if_value.iloc[i]['contract_00'])[:-1] + ',' + str(if_value.iloc[i]['contract_main'])[:-1] + '\n'
    
    strtime = str(ih_value.iloc[i]['dt'])[0:10]
    #ta = str.split(strtime, '-')
    #for s in ta:
    #    msg = msg + s
    msg = msg + strtime
    msg = msg + ',IH,'
    msg = msg + str(ih_value.iloc[i]['contract_00'])[:-1] + ',' + str(ih_value.iloc[i]['contract_main'])[:-1] + '\n'
    
    strtime = str(t_value.iloc[i]['dt'])[0:10]
    #ta = str.split(strtime, '-')
    #for s in ta:
    #    msg = msg + s
    msg = msg + strtime
    msg = msg + ',T,'
    msg = msg + str(t_value.iloc[i]['contract_00'])[:-1] + ',' + str(t_value.iloc[i]['contract_main'])[:-1] + '\n'
    
print(msg)
f = open('futuresContract.csv', 'w')
f.write(msg)
f.close()

