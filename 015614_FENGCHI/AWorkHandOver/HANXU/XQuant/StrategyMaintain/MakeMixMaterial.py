import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')
from HFfactor.MinFactorSuper.PrepareRealTime.MakeTmrMaterial import MakeTmrMaterial
from HFfactor.MinFactorSuper.PrepareOffline.WeeklyMaintain import WeeklyMaintain
from dataApi.sendInfo import send_message
import gc

mtm = MakeTmrMaterial()
del mtm
gc.collect()
mm = WeeklyMaintain()
del mm
gc.collect()
send_message(['015664'], '高频盘前数据更新成功')