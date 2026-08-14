# coding: utf-8
# Author：fengchi863
# Date ：2022/11/11 10:02
"""
下午发送上市次新股加股票池事项
"""
import sys
sys.path.append('/data/user/015614/Lucien')

from email.mime.text import MIMEText
from email.header import decode_header
from email.utils import parseaddr
import smtplib
import imaplib
import email
import time
from MixedWork.SendStockEmail.password import password
from email.mime.multipart import MIMEMultipart
import os
import pandas as pd
import datetime as dt
from xquant.xqutils.helper import link
from xquant.factordata import FactorData
import base64
from dataApi.sendInfo import send_message

send_no_list = ['015614', '003296']
s = FactorData()

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
        return value

class CoreMailer:
    def __init__(self):
        smtp_server = 'htemail.htsc.com.cn'
        from_addr = 'fengchi@htsc.com'
        server = smtplib.SMTP(smtp_server, 25)  # SMTP协议默认端口是25
        server.login(from_addr, password)
        self.server = server
        self.from_addr = from_addr

    def send_mail(self, subject, body, to_recipients=[], cc_recipients=[], attachment_file=''):
        msg = MIMEMultipart()
        if isinstance(to_recipients, str):
            to_recipients = [to_recipients]
            assert isinstance(to_recipients, list)

        if isinstance(cc_recipients, str):
            cc_recipients = [cc_recipients]
            assert isinstance(cc_recipients, list)

        if attachment_file:  # 处理附件
            file_name = os.path.split(attachment_file)[-1]  # 只取文件名，不取路径
            try:
                f = open(attachment_file, 'rb').read()
            except Exception as e:
                raise Exception('附件打不开！！！！%s' % e)
            else:
                att = MIMEText(f, "base64", "utf-8")
                att["Content-Type"] = 'application/octet-stream'
                new_file_name = '=?utf-8?b?' + base64.b64encode(file_name.encode()).decode() + '?='
                att["Content-Disposition"] = 'attachment; filename="%s"' % new_file_name
                msg.attach(att)

        msg.attach(MIMEText(body))
        msg['Subject'] = subject
        msg['From'] = self.from_addr
        msg['to'] = ','.join(to_recipients)
        msg['Cc'] = ','.join(cc_recipients)

        self.server.sendmail(self.from_addr, to_recipients + cc_recipients, msg.as_string())
        self.server.quit()

    def check_title_in_received(self, title_str, sender=None, check_num=100):
        from_addr = self.from_addr
        pop3_server = 'htemail.htsc.com.cn'
        server = imaplib.IMAP4_SSL(pop3_server)
        server.login(from_addr, password)
        server.select("INBOX")
        type, data = server.search(None, "ALL")
        msgList = data[0].split()[::-1]
        for i in range(0, check_num):
            type, datas = server.fetch(msgList[i], '(RFC822)')
            text = datas[0][1].decode('utf8')
            msg = email.message_from_string(text)

            From = parseaddr(msg.get('from'))[1]
            To = parseaddr(msg.get('To'))[1]
            Cc = parseaddr(msg.get_all('Cc'))[1]
            Subject = decode_str(parseaddr(msg.get('Subject'))[1])
            try:
                date1 = time.strptime(msg.get("Date")[0:24], '%a, %d %b %Y %H:%M:%S')
            except:
                print('时间错误！')
            date2 = time.strftime("%Y-%m-%d %H:%M:%S", date1)
            print(f'发件人：{From}；收件人：{To}；抄送人：{Cc}；主题：{Subject}；收件日期：{date2}')

            try:
                print(From, Subject)
                if (Subject == title_str) and ((sender is None) | (From == sender)):
                    return True
            except:
                print(Subject)

            # for part in msg.walk():
            #     if not part.is_multipart():
            #         print(part.get_payload()[0].get_payload(decode=True).decode('utf-8'))
        return False

def get_new_stock(tommorow):
    today_date = s.tradingday(tommorow, -2)[0]
    # board_list = ['主板', '中小企业板', '创业板']  # if tommorow<'20200824' else ['主板', '中小企业板']
    AShareDescription = s.get_factor_value('WIND_AShareDescription', S_INFO_LISTDATE=[f'>={today_date}'],
                                           factors=['S_INFO_WINDCODE', 'S_INFO_NAME', 'S_INFO_LISTBOARDNAME', 'S_INFO_LISTDATE'])
    if len(AShareDescription) == 0:
        return pd.DataFrame(), ''
    filter_regex = f'(S_INFO_LISTBOARDNAME == "主板" & S_INFO_LISTDATE == "{tommorow}") |' + \
                   f'(S_INFO_LISTBOARDNAME == "中小企业板" & S_INFO_LISTDATE == "{tommorow}") |' + \
                   f'(S_INFO_LISTBOARDNAME == "创业板" & S_INFO_LISTDATE == "{today_date}") |' + \
                   f'(S_INFO_LISTBOARDNAME == "科创板" & S_INFO_LISTDATE == "{today_date}")'
    AShareDescription = AShareDescription.query(filter_regex)
    if len(AShareDescription) == 0:
        return pd.DataFrame(), ''

    new_stock_str = ''
    for i in AShareDescription.index:
        code, name, board = AShareDescription.loc[i, ['S_INFO_WINDCODE', 'S_INFO_NAME', 'S_INFO_LISTBOARDNAME']]
        new_stock_str += '%s（%s）、' % (code, name)

        AShareAgency = s.get_factor_value('WIND_AShareAgency', S_INFO_WINDCODE=code)
        agency_num = len(AShareAgency)
        ht = 0
        if agency_num > 0:
            for S_AGENCY_NAME in AShareAgency['S_AGENCY_NAME']:
                if '华泰联合' in S_AGENCY_NAME:
                    ht = 1
        AShareDescription.loc[i, 'agency_num'] = agency_num
        AShareDescription.loc[i, 'ht'] = ht

    new_stock_str = new_stock_str[:-1]
    return AShareDescription, new_stock_str

today = dt.datetime.now().strftime('%Y%m%d')
tommorow = s.tradingday(today, 2)[1]
last_tradingday = s.tradingday(today, -1)[0]
lm = link.LinkMessage()
if last_tradingday == today:
    cm = None
    try:
        # ！！！注意，修改为自己的邮箱账号密码，每半年修改办公密码记得同步修改
        cm = CoreMailer()
        flag = True
    except Exception as e:
        print(e)

    to_recipients = ['xieluyao@htsc.com', 'wangjing013550@htsc.com',
                     'sunshaosen@htsc.com', 'fengchi@htsc.com']
    cc_recipients = []

    # DEBUG用
    # to_recipients = ['sunshaosen@htsc.com']
    # cc_recipients = ['fengchi@htsc.com']

    today_has_send_email = cm.check_title_in_received('上市股票入池申请-%s' % today, sender='冯炽', check_num=50)
    raw_data, new_stock_str = get_new_stock(tommorow)
    tommorow_has_new_stock = len(raw_data) > 0
    if today_has_send_email or tommorow_has_new_stock:
        # today_receive_mail_reply = mailer.check_title_in_received('答复: 上市股票入池申请-%s'%(today), sender='陈敏航', check_num=20)
        today_receive_mail_reply = cm.check_title_in_received('答复: 上市股票入池申请-%s' % today, check_num=50)
        print('明天有无新股：%s, 邮件是否发送：%s' % (tommorow_has_new_stock, today_has_send_email))
        if not today_receive_mail_reply:
            cm.send_mail(subject=today + '-风控没有回复入池邮件！！！', body='RT',
                        to_recipients=to_recipients, cc_recipients=cc_recipients)
            send_message('【入池提醒】麻烦李老师检查下邮件，有新的股票需要进行入池操作~', users=send_no_list)
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