import datetime,os
from xquant.investment.strategyfile import upload_strategy_file

def upload_to_xtrader():
    cpp_path = r'/data/user/013551/forJYY-Strong/cpp/'
    strategy_date = datetime.date.today().strftime('%Y%m%d')
#    upload_strategy_file('BetaEventDrivenStrategy', strategy_date, 0, os.path.join(cpp_path,'%s-eventdriven-beta_zuhe.zip'%strategy_date), is_delete=False)
#    upload_strategy_file('BetaEventDrivenStrategy', strategy_date, 1, os.path.join(cpp_path,'%s-eventdriven-beta-front.zip'%strategy_date), is_delete=False)
#    upload_strategy_file('BetaEventdriven_udp', strategy_date, 1, os.path.join(cpp_path,'%s-eventdriven-beta_udp-front.zip'%strategy_date), is_delete=False)
#    upload_strategy_file('BetaEventdriven_fast', strategy_date, 1, os.path.join(cpp_path,'%s-eventdriven-beta_fast-front.zip'%strategy_date), is_delete=False)

    upload_strategy_file('EventDrivenStrategy', strategy_date, 0, os.path.join(cpp_path,'%s-eventdriven_zuhe.zip'%strategy_date), is_delete=False)
    upload_strategy_file('EventDrivenStrategy', strategy_date, 1, os.path.join(cpp_path,'%s-eventdriven-front.zip'%strategy_date), is_delete=False, is_ready=1)
    upload_strategy_file('Eventdriven_udp', strategy_date, 1, os.path.join(cpp_path,'%s-eventdriven_udp-front.zip'%strategy_date), is_delete=False, is_ready=1)
    upload_strategy_file('Eventdriven_fast', strategy_date, 1, os.path.join(cpp_path,'%s-eventdriven_fast-front.zip'%strategy_date), is_delete=False, is_ready=1)
    print("Upload cpp prod param ready!")
  
upload_to_xtrader()