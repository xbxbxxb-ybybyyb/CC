import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')



with open('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/TSmodel/RealTime/MRFixFactorTest.py','r') as f:
    exec(f.read())

from dataApi.sendInfo import send_message
send_message(['015664'], 'fix因子检测成功')