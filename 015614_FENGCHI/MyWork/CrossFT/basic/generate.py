import warnings
warnings.filterwarnings("ignore")
import sys
sys.path.append('/data/group/800442/800319')
sys.path.append('/data/user/016385')
sys.path.append('/data/user/016385/test/digger_factor')
sys.path.append('/data/user/016385/test/crossft')
from basic.utils import *
from basic.crossUtils import *
from a02_monitor.link import send_file
from dataApi.getData import *
from dataApi.tradeDate import *
from datetime import date
import os
loc = '/data/user/016385/test/crossft/'

types = ['class','cross_group', 'cross_func', 'extend_days',  'author', 'logic', 'article', 'freq']
end_date =get_pre_trade_date(int(date.today().strftime('%Y%m%d')),offset=0)
yes = 20211026#get_pre_trade_date(int(end_date),offset=3)

final =[]
for f in ['factors','monitor_factor','daily2min']:
    for name in os.listdir(loc+f):
        if '.' not in name and '__' not in name:
            for file in os.listdir(loc+f+'/'+name):
                if '__' not in file and '.ipynb_checkpoints' not in file:
                    tfile = file.replace('.py','')
                    val = [('class',tfile)]
                    m = get_factor_class(tfile, '.'.join([f,name]))
                    for t in types[1:]:
                        val.append((t, eval('m.{}'.format( t))))
                    final.append(val)
                    #finstance = create_factor_instance(m)
                    #print(finstance.author)

f = pd.DataFrame(index = types)
for i,x in enumerate(final):
    val =pd.Series(dict(x))
    f.loc[val.index,i]=val.values
todayval = (f.T).set_index('class')
yesval = pd.read_excel('/arch1/group/800442/800319/AAcross/factor_summary/横截面因子{}.xlsx'.format(yes),sheet_name='累积全部因子',index_col=0)

writer = pd.ExcelWriter('/arch1/group/800442/800319/AAcross/factor_summary/横截面因子{}.xlsx'.format(end_date))
todayval.dropna(thresh=1).loc[todayval.index.map(lambda x: x not in yesval.index),:].to_excel(excel_writer=writer, sheet_name='新增因子')
todayval.dropna(thresh=1).to_excel(excel_writer=writer, sheet_name='累积全部因子')
writer.save()
send_file(['016385'],'/arch1/group/800442/800319/AAcross/factor_summary/横截面因子{}.xlsx'.format(end_date))