import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

with open('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/TSmodel/MorningModel/BackPoolRealTime/market_timing.py',
          'r') as f:
    exec(f.read())

with open('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/TSmodel/MorningModel/BackPoolRealTime2022/run_back_pool.py',
          'r') as f:
    exec(f.read())

from dataApi.sendInfo import send_message

send_message(['015664'], '日间股票池更新成功')