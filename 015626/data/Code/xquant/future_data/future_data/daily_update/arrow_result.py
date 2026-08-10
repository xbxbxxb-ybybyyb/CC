import sys
sys.path.insert(1,'/data/user/015626/JupyterNotebooks/utils/')
from operators_all_wsc import *
from multifactor.data.utils import *
import multifactor.utility.dt as udt
from multifactor.IO import IO

_,date ,cdate_list = check_update_date()
path = f'/data/group/800466/warehouse/prod/tradingstats/Arrow/{date}/Arrow_Transaction_{date}.xlsx'
try:
    if os.path.exists(path):
        arrow = pd.read_excel(path, sheet_name='buy_details')
        msg1 = ' '.join(arrow['证券代码'].tolist())
        arrow = pd.read_excel(path, sheet_name='summary', index_col=0)
        arrow = arrow[['买入']]
        arrow.loc['平均买入金额'] = arrow.loc['成交金额']['买入'] / arrow.loc['股票数量']['买入']
        arrow.loc['股票数量'] = int(arrow.loc['股票数量']['买入'])
        send_link(str(arrow))
        send_link(msg1)
    else:
        send_link('arrow no deal today')
except:
    send_link('arrow no deal today')