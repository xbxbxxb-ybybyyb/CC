# coding: utf-8
# Author：fengchi863
# Date ：2022/11/11 10:20

"""
下午发送上市次新股加股票池事项
"""
import sys
sys.path.append('/data/user/015614/Lucien')

from email.mime.text import MIMEText
import smtplib
from MixedWork.SendStockEmail.password import password
from email.mime.multipart import MIMEMultipart
import os
import pandas as pd
import datetime as dt
from xquant.xqutils.helper import link
from xquant.factordata import FactorData
import base64

s = FactorData()

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
                   f'(S_INFO_LISTBOARDNAME == "创业板" & S_INFO_LISTDATE == "{today_date}") |' + \
                   f'(S_INFO_LISTBOARDNAME == "科创板" & S_INFO_LISTDATE == "{today_date}") |' + \
                   f'(S_INFO_LISTBOARDNAME == "北证" & S_INFO_LISTDATE == "{tommorow}") '
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


lm = link.LinkMessage()
try:
    today = dt.datetime.now().strftime('%Y%m%d')
    # today = '20250414'
    tommorow = s.tradingday(today, 2)[1]
    last_tradingday = s.tradingday(today, -1)[0]
    if last_tradingday == today:
        # ！！！注意，修改为自己的邮箱账号密码，每半年修改办公密码记得同步修改
        cm = CoreMailer()

        # to_recipients = ['lijianfeng@htsc.com']
        # cc_recipients = ['panxiaoming@htsc.com', 'wuyushuang@htsc.com', 'zhouyou@htsc.com',
        #                 'yangshiwei@htsc.com', 'zhaoyuming@htsc.com', 'xiangwanyu@htsc.com','wangjing013550@htsc.com',
        #                 'xieluyao@htsc.com','sunshaosen@htsc.com','fengchi@htsc.com', 'yiwenxiu@htsc.com',
        #                 'xuxinyi@htsc.com', 'kongjianyang@htsc.com', 'zhangjinkang@htsc.com']
        # ht_recipients = ['minhuang@htsc.com']

        # DEBUG用
        to_recipients = ['fengchi@htsc.com']
        cc_recipients = ['sunshaosen@htsc.com']
        ht_recipients = []

        raw_data, new_stock_str = get_new_stock(tommorow)
        if len(raw_data) > 0:
            print(raw_data, '\n', new_stock_str)
            ht_str = ''

            if raw_data['ht'].sum() > 0:
                cc_recipients = cc_recipients + ht_recipients
                ht_str = '!!!（华泰联合）'
            if raw_data['agency_num'].min() < 1:
                lm.sendMessage('！警告：股票无中介机构数据')

            body = f'李老师，您好！\n\n      麻烦把{new_stock_str}加一下证投部交易证券池，谢谢！\n​\n' + \
                    '祝好\n--------------------------------------------------------------\n\n冯 炽\n证券投资部 金融工程团队\n' + \
                    '华泰证券股份有限公司\n手机：(+86) 15150687511\n邮件：fengchi@htsc.com\n邮编：210019\n地址：南京市江东中路228号华泰证券广场一号楼7层'

            cm.send_mail(subject='上市股票入池申请-%s' % today,
                         body=body,
                         to_recipients=to_recipients,
                         cc_recipients=cc_recipients)
            message = ht_str + '已发送邮件，明日上市新股：' + new_stock_str
        else:
            message = '未发送邮件，明日没有上市新股'
            print(message)
        lm.sendMessage(message)
    else:
        print('今天是非交易日，不查询')
except Exception as e:
    lm.sendMessage('！！！错误：入库报错')
