# coding: utf-8
# Author：fengchi863
# Date ：2022/8/3 19:02
"""
下午发送上市次新股加股票池事项
"""
import sys
sys.path.append('/data/user/015614/Lucien')

import datetime as dt
import time
import pandas as pd
try:
    from exchangelib import Message, Mailbox, Credentials, Account, FileAttachment
except:
    import os
    print('开始安装库')
    os.system('pip3 install exchangelib')
    print('exchangelib安装成功')
    from exchangelib import Message, Mailbox, Credentials, Account, FileAttachment
from xquant.factordata import FactorData
from xquant.xqutils.helper import link
from MixedWork.SendStockEmail.password import password
from dataApi.sendInfo import send_message

send_no_list = ['015614']

s = FactorData()


class ExchangeMailer:
    def __init__(self, account, secret, email):
        self.credentials = Credentials(account, secret)
        self.account = Account(email, credentials=self.credentials, autodiscover=True)

    def send_mail(self, subject, body, to_recipients=[], cc_recipients=[], attachment_files=[]):
        if isinstance(to_recipients, str):
            to_recipients = [to_recipients]
        assert isinstance(to_recipients, list)

        if isinstance(cc_recipients, str):
            cc_recipients = [cc_recipients]
        assert isinstance(cc_recipients, list)

        to_recipients = [Mailbox(email_address=item) for item in to_recipients]
        cc_recipients = [Mailbox(email_address=item) for item in cc_recipients]
        messeage = Message(account=self.account, subject=subject, body=body, to_recipients=to_recipients,
                           cc_recipients=cc_recipients)
        for attachment_file in attachment_files:
            attachment_name = attachment_file[attachment_file.rindex('\\') + 1:]
            myfile = FileAttachment(name=attachment_name, content=open(attachment_file, 'rb').read())
            messeage.attach(myfile)
        messeage.send()
        print('邮件发送成功')

    def check_title_in_received(self, title_str, sender=None, check_num=100):
        for item in self.account.inbox.all().order_by('-datetime_received')[:check_num]:
            try:
                print(item.sender.name, item.subject)
                if (item.subject == title_str) and ((sender is None) | (item.sender.name == sender)):
                    return True
            except:
                print(item.subject)
        return False

#%% old版本，明天上市的创业板也发
# def get_new_stock(tommorow):
#     board_list = ['主板', '中小企业板', '创业板']  # if tommorow<'20200824' else ['主板', '中小企业板']
#     AShareDescription = s.get_factor_value('WIND_AShareDescription', S_INFO_LISTDATE=tommorow,
#                                            factors=['S_INFO_WINDCODE', 'S_INFO_NAME', 'S_INFO_LISTBOARDNAME'])
#     if len(AShareDescription) == 0:
#         return pd.DataFrame(), ''
#     AShareDescription = AShareDescription[AShareDescription['S_INFO_LISTBOARDNAME'].isin(board_list)]
#     if len(AShareDescription) == 0:
#         return pd.DataFrame(), ''
#
#     new_stock_str = ''
#     for i in AShareDescription.index:
#         code, name, board = AShareDescription.loc[i]
#         new_stock_str += '%s(%s)、' % (code, name)
#     new_stock_str = new_stock_str[:-1]
#     return AShareDescription, new_stock_str

def get_new_stock(tommorow):
    today_date = s.tradingday(tommorow, -2)[0]
    # board_list = ['主板', '中小企业板', '创业板']  # if tommorow<'20200824' else ['主板', '中小企业板']
    AShareDescription = s.get_factor_value('WIND_AShareDescription', S_INFO_LISTDATE=[f'>={today_date}'],
                                           factors=['S_INFO_WINDCODE', 'S_INFO_NAME', 'S_INFO_LISTBOARDNAME', 'S_INFO_LISTDATE'])
    if len(AShareDescription) == 0:
        return pd.DataFrame(), ''
    # AShareDescription = AShareDescription[AShareDescription['S_INFO_LISTBOARDNAME'].isin(board_list)]
    filter_regex = f'(S_INFO_LISTBOARDNAME == "主板" & S_INFO_LISTDATE == "{tommorow}") |' + \
                   f'(S_INFO_LISTBOARDNAME == "中小企业板" & S_INFO_LISTDATE == "{tommorow}") |' + \
                   f'(S_INFO_LISTBOARDNAME == "创业板" & S_INFO_LISTDATE == "{today_date}")'
    AShareDescription = AShareDescription.query(filter_regex)
    if len(AShareDescription) == 0:
        return pd.DataFrame(), ''

    new_stock_str = ''
    for i in AShareDescription.index:
        code, name, board, _ = AShareDescription.loc[i]
        new_stock_str += '%s(%s)、' % (code, name)
    new_stock_str = new_stock_str[:-1]
    return AShareDescription, new_stock_str

# while True:
#     current_time = time.localtime(time.time())
#     print(current_time)
#     if current_time.tm_hour == 17 and current_time.tm_min == 30:  # 定时运行的时间
#     # if current_time.tm_hour >= 17:  # DEBUG用
today = dt.datetime.now().strftime('%Y%m%d')
tommorow = s.tradingday(today, 2)[1]
last_tradingday = s.tradingday(today, -1)[0]
lm = link.LinkMessage()
if last_tradingday == today:
    mailer = None
    try:
        # ！！！注意，修改为自己的邮箱账号密码，每半年修改办公密码记得同步修改
        mailer = ExchangeMailer('fengchi@htsc.com', password, 'fengchi@htsc.com')
        flag = True
    except Exception as e:
        print(e)

    to_recipients = ['xieluyao@htsc.com', 'wangjing013550@htsc.com',
                     'sunshaosen@htsc.com', 'fengchi@htsc.com']
    cc_recipients = []

    # DEBUG用
    # to_recipients = ['sunshaosen@htsc.com']
    # cc_recipients = ['fengchi@htsc.com']

    today_has_send_email = mailer.check_title_in_received('上市股票入池申请-%s' % today, sender='冯炽', check_num=50)
    raw_data, new_stock_str = get_new_stock(tommorow)
    tommorow_has_new_stock = len(raw_data) > 0
    if today_has_send_email or tommorow_has_new_stock:
        # today_receive_mail_reply = mailer.check_title_in_received('答复: 上市股票入池申请-%s'%(today), sender='陈敏航', check_num=20)
        today_receive_mail_reply = mailer.check_title_in_received('答复: 上市股票入池申请-%s' % today, check_num=50)
        print('明天有无新股：%s, 邮件是否发送：%s' % (tommorow_has_new_stock, today_has_send_email))
        if not today_receive_mail_reply:
            mailer.send_mail(subject=today + '-风控没有回复入池邮件！！！', body='RT',
                             to_recipients=to_recipients, cc_recipients=cc_recipients)
            send_message('【入池提醒】麻烦陈老师检查下邮件，有新的股票需要进行入池操作~', users=send_no_list)
            print('邮件没有被回复')
            lm.sendMessage(today + '风控没有回复入池邮件！！！')
        else:
            print('邮件已被回复')
            send_message('邮件已被回复')
    else:
        print('明日没有次新股')
else:
    print('非交易日,不查询。')
    #     time.sleep(60 * 60 * 23)  # 休眠23个小时
    # time.sleep(30)
