import datetime,os
from xquant.investment.strategyfile import upload_strategy_file

def upload_to_xtrader():
    strategy_id = 'EventDriven'
    strategy_date = datetime.date.today().strftime('%Y%m%d')
    upload_file_path = r'/data/user/013551/forJYY-Strong/%s-O45-SZ-new/daily-zuhe-prod-O45-SZ-new'%strategy_date
    for filename in os.listdir(upload_file_path):
        print(filename)
        upload_strategy_file(strategy_id, strategy_date, 0, os.path.join(upload_file_path,filename), is_delete=False)
    upload_file_path = r'/data/user/013551/forJYY-Strong/%s-O45-SH-new/daily-zuhe-prod-O45-SH-new'%strategy_date
    for filename in os.listdir(upload_file_path):
        print(filename)
        upload_strategy_file(strategy_id, strategy_date, 0, os.path.join(upload_file_path,filename), is_delete=False)
    upload_file_path = r'/data/user/013551/forJYY-Strong/%s-O45-mock/daily-zuhe-prod-O45-mock'%strategy_date
    for filename in os.listdir(upload_file_path):
        print(filename)
        upload_strategy_file(strategy_id, strategy_date, 0, os.path.join(upload_file_path,filename), is_delete=False)
    upload_strategy_file(strategy_id, strategy_date, 1, r'/data/user/013551/forJYY-Strong/%s-O45-SZ-new/%s-prod-O45-SZ-new.zip'%(strategy_date,strategy_date), is_delete=False)
    upload_strategy_file(strategy_id, strategy_date, 1, r'/data/user/013551/forJYY-Strong/%s-O45-SH-new/%s-prod-O45-SH-new.zip'%(strategy_date,strategy_date), is_delete=False)
    upload_strategy_file(strategy_id, strategy_date, 1, r'/data/user/013551/forJYY-Strong/%s-O45-mock/%s-prod-O45-mock.zip'%(strategy_date,strategy_date), is_delete=False, is_ready=1)
upload_to_xtrader()