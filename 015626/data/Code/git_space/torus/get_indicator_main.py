from xquant.compute.aimr import AIMR
import json, os
print("start")

with open('/dfs/user/015626/JupyterNotebooks/utils/imports.txt', 'r') as file:
    code = file.read()
    exec(code)

start_date, end_date = 20160101, 20250904

dailym = IO.read_data([start_date, end_date],columns = ['contract', 'volume'], alt = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/DAILY/MD_MAIN_CHINA_COMMODITY_DAILY_NO_DAYS.h5')
dailys = IO.read_data([start_date, end_date],columns = ['contract', 'volume'], alt = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/DAILY/MD_SECONDMAIN_CHINA_COMMODITY_DAILY_NO_DAYS.h5')
daily = pd.concat([dailym, dailys]).sort_index()
daily = daily[daily['volume'] > 0].reset_index()
daily['dt'] = daily['dt'].apply(lambda x:x.strftime('%Y%m%d'))

#prod_id_list=[x for x in daily['Ticker'].unique().tolist() if 'CZC' not in x]
prod_id_list=daily['Ticker'].unique().tolist()

prod_id_list = list(set(prod_id_list) - set(['AFS.CFE', 'EFS.CFE', 'IMS.SHF', 'WR.ZCE', 'SCTAS.INE']))
prod_id_list = [x for x in prod_id_list if not x.endswith('CFE')]
#prod_id_list = ['JM.DCE']
#rootpath = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/1MIN/PER_TICKER/CSV'
#now_exist_list = [x.replace('.h5', '') for x in os.listdir(rootpath)]
#prod_id_list = list(set(prod_id_list) - set(now_exist_list))
#prod_id_list = [x for x in prod_id_list if x.endswith('.CFE')]
print(prod_id_list)

params = {
    "parallel_list": prod_id_list, 
    "docker_version":'cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:dol_genesis_cpu',  
    "tag":"xquant",
    "cpu":24,
    "gpu":0,
    "memory":100000,
    "preferred_gpu":0,
    "subtask_limit_num":10
}
#job.py文件为用户自定义的并行任务文件    
result = AIMR.runTasks('data/get_indicator_job.py',json.dumps(params))