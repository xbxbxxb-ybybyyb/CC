import os
import datetime
from xquant.factordata import FactorData
s = FactorData()
date = datetime.date.today().strftime('%Y%m%d')

path = os.getcwd()
print(path)
print('deleteFile================================================')
os.system("python3 %s/deleteFile.py"%path)
print('generate_json_forT0_O45_SZ_new================================================')
os.system("python3 %s/generate_json_forT0_O45_SZ_new.py"%path)
print('generate_json_forT0_O45_SH_new================================================')
os.system("python3 %s/generate_json_forT0_O45_SH_new.py"%path)

print('generate_params_prod_O45_SZ_new================================================')
os.system("python3 %s/bak/generate_params_prod_O45_SZ_20230721.py"%path)
print('generate_params_prod_O45_SH_new================================================')
os.system("python3 %s/bak/generate_params_prod_O45_SH_20230721.py"%path)
os.system("python3 %s/zipFile.py"%path)
os.system("python3 %s/zone_allocate_20230516.py"%path)
