from utils import *
import pandas as pd

sdate,edate,cdate_list = check_update_date(20140101,20191111)
root_path = 'Z://warehouse//prod//LOCAL_DATA//CSV//WIND//HIGH_FREQ_MD_old//'
new_path = 'Z://warehouse//prod//LOCAL_DATA//CSV//WIND//HIGH_FREQ_MD//'

# csv_list = [os.path.join(root_path, i) for i in os.listdir(root_path)]
for i in os.listdir(root_path):
    print(i)
    df = pd.read_csv(os.path.join(root_path, i))
    dt = int(i[:8])
    new_dt = cdate_list[cdate_list.index(dt) + 1]
    print(new_dt)
    df['dt'] = new_dt
    df = df.set_index(['dt','Ticker'])
    df.to_csv(os.path.join(new_path, str(new_dt) + '.csv'))
