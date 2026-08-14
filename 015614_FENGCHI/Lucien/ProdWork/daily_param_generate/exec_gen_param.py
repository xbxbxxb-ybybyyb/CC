import os

path = os.getcwd()
print(path)
os.system("python3 %s/bak/param_20230911_O45.py"%path)
os.system("python3 %s/apart_param.py"%path)
os.system("python3 %s/combine_run.py"%path)
os.system("python3 %s/combine_run_copy.py"%path)
from xquant.xqutils.helper import link
lm = link.LinkMessage()
lm.sendMessage('prod param ready')