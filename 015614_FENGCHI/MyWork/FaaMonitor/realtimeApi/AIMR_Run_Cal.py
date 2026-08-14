from xquant.compute.aimr import AIMR
import configparser,os,json
import pandas as pd

#股票池
Conept_AllStock = pd.read_excel('/data/group/800319/Concept_monitor/概念板块分工及对应个股.xlsx',sheet_name=0 ,index_col=0).iloc[:, :3]
Conept_DelStock = set(pd.read_excel('/data/group/800319/Concept_monitor/概念板块分工及对应个股.xlsx',sheet_name=1 ,index_col=0)['子主题名称'].dropna())
concept_list=[]
for concept in sorted(list(set(Conept_AllStock['子主题']))):
    if len(set(Conept_AllStock[Conept_AllStock['子主题']==concept].index))>=50:
        pass
        #print(concept + '板块中个股数量超过50个，数量过多暂不计算')
    elif len(set(Conept_AllStock[Conept_AllStock['子主题']==concept].index))<=5:
        pass
        #print(concept + '板块中个股数量低于5个，数量过少暂不计算')
    elif concept in Conept_DelStock:
        pass
        #print(concept+'属于不监控板块，暂不计算')
    else:
        concept_list.append(concept)

concept_list = sorted(concept_list)
choice_num = int(len(concept_list)/4)+1

if choice_num<=20:
    cpu = 10
elif choice_num<=30:
    cpu = 15
else:
    cpu = 20


params = {
    "parallel_list": [1,2,3,4],
    "tag":"xquant",
    "cpu":cpu,
    "gpu":0,
    "memory":1024*50,
    "preferred_gpu":0
}

AIMR.runTasks('./RealTime_Data/RealTime_Cal.py',json.dumps(params))
print("end")