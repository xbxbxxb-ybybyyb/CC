
import os
os.system("pip uninstall xdbJG -y")
os.system("pip install /data/user/019073/marketdata/installer_and_demo/xdbJG-2.0.0-cp36-cp36m-linux_x86_64.whl")
# os.system("pip install /data/user/019073/marketdata/installer_and_demo/xdbJG-2.0.0-cp36-cp36m-linux_x86_64.whl")

from xdbJG.stockdata import StockData
xdb_datasource = StockData()

tmp = xdb_datasource.get_tick_1min('20170110','000001.SZ')
