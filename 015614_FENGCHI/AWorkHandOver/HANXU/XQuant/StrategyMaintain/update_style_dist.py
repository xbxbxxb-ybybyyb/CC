import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')
#21:30
with open('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/TSmodel/BackPool/ConditionSample/ConditionSample2.py','r') as f:
    exec(f.read())

from dataApi.sendInfo import send_message
send_message(['015664'], '风格因子相似度更新成功')