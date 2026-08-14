# coding: utf-8
# Author：fengchi863
# Date ：2022/8/31 20:38

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
import numpy as np
import datetime as dt
from xquant.xqutils.helper import link
from xquant.factordata import FactorData
from LucienUtil import IO
import base64
from dataApi.sendInfo import send_message

send_no_list = ['015614']
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
        res_dic = {}

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
            try:
                date1 = time.strptime(msg.get("Date")[0:24], '%a, %d %b %Y %H:%M:%S')
            except:
                date1 = time.strptime(msg.get("Date")[0:26], '%d %b %Y %H:%M:%S +0800')
            tradingday = date1.tm_year * 10000 + date1.tm_mon * 100 + date1.tm_mday
            try:
                Subject = decode_str(parseaddr(msg.get('Subject'))[1])
            except:
                print(f'{tradingday}有一个找不到')
                continue

            if (tradingday < start_date) or (tradingday > end_date) or \
                    (Subject is None) or ('入池申请' not in Subject):
                continue
            try:
                for part in msg.walk():
                    if part.is_multipart():
                        parts = part.get_payload()
                        content = parts[0].get_payload(decode=True).decode('utf-8')
                    else:
                        content = part.get_payload(decode=True).decode('utf-8')
            except:
                parts = msg.get_payload()
                content = parts[0].get_payload(decode=True)

            if ((Subject is not None) and (title_str in Subject)) and ((sender is None) | (From == sender)):
                key = Subject + '-%s' % tradingday
                if key in res_dic:
                    res_dic[key + str(tradingday)] = content
                else:
                    res_dic[key] = content
        return res_dic

def transf_code(code_list):
    code_list = list(code_list)
    res = ''
    for code in code_list:
        res += code + ','
    return res[:-1]


def windData2DataFrame(windData, columnNames):
    import numpy as np
    return pd.DataFrame(np.transpose(windData.Data), index=windData.Codes, columns=columnNames)


if __name__ == '__main__':
    mailer = None
    try:
        mailer = CoreMailer()
        flag = True
    except Exception as e:
        print(e)
    start_date, end_date = 20250301, 20250323
    # email_dic1 = mailer.check_title_in_received('入池申请', sender='王伟地', check_num=1000)
    # email_dic2 = mailer.check_title_in_received('入池申请', sender='孙少森', check_num=1000)
    email_dic2 = mailer.check_title_in_received('入池申请', sender='fengchi@htsc.com', check_num=1000)
    email_dic = email_dic2
    zt_list = []
    event_list = []
    for key, value in email_dic.items():
        # print(key, value)
        try:
            use_value = value[value.index('麻烦把') + 3:value.index('加一下')].replace(' ', '')
        except:
            continue

        if len(use_value) > 16:
            has_split = False
            for s in [',', '，', '、']:
                if s in use_value:
                    value_list = use_value.split(s)
                    has_split = True
                    break
            if not has_split:
                print('error!!!', use_value)
        else:
            value_list = [use_value]
        print(value_list)

        if '事件型交易证券池' in value:
            event_list += value_list

        if ('证投部交易证券池' in value) or ('证投部交易池' in value):
            zt_list += value_list

    event_list = [stock for stock in event_list if '华泰联合' not in stock]
    event_list = np.unique([stock[:stock.index("(")] if '(' in stock else stock[:stock.index("（")] for stock in event_list])
    event_df = pd.DataFrame()
    event_df['证券代码'] = event_list
    event_df['证券代码'] = event_df['证券代码'].apply(lambda x: x[:6] + '.SH' if x[0] == '6' else x[:6] + '.SZ')

    # name_data = IO.read_data([end_date, end_date], alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
    end_date = 20250321 # 如果赶上end_date是周末，那么这一天没有name_data数据
    name_data = IO.read_data([end_date, end_date], alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
    for index, row in event_df.iterrows():
        if (pd.to_datetime(str(end_date)), row['证券代码']) in name_data.index:
            event_df.loc[index, '证券名称'] = name_data.loc[pd.to_datetime(str(end_date)), row['证券代码']]['STOCK_NAME'].values[0]
        else:
            event_df.loc[index, '证券名称'] = str(np.nan)

    zt_list = [stock for stock in zt_list if '华泰联合' not in stock]
    zt_list = np.unique([stock[:stock.index("(")] if '(' in stock else stock[:stock.index("（")] for stock in zt_list])
    zt_df = pd.DataFrame()
    zt_df['证券代码'] = zt_list
    from dataApi.stockList import trans_int2windcode
    zt_df['证券代码'] = zt_df['证券代码'].apply(lambda x: trans_int2windcode(x))
    for index, row in zt_df.iterrows():
        if (pd.to_datetime(str(end_date)), row['证券代码']) in name_data.index:
            zt_df.loc[index, '证券名称'] = name_data.loc[pd.to_datetime(str(end_date)), row['证券代码']]['STOCK_NAME'].values[0]
        else:
            zt_df.loc[index, '证券名称'] = str(np.nan)

    event_df['证券类别'] = '股票'
    zt_df['证券类别'] = '股票'

    from dataApi.sendInfo import send_file
    # send_file(event_df)
    time.sleep(5)
    send_file(zt_df)