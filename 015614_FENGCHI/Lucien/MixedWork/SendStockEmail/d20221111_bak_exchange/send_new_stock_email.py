# coding: utf-8
# Author：fengchi863
# Date ：2022/8/3 17:24

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
    tommorow = s.tradingday(today, 2)[1]
    last_tradingday = s.tradingday(today, -1)[0]
    if last_tradingday == today:
        # ！！！注意，修改为自己的邮箱账号密码，每半年修改办公密码记得同步修改
        # mailer = ExchangeMailer('fengchi@htsc.com', password, 'fengchi@htsc.com')

        # to_recipients =['chenminhang@htsc.com']
        # cc_recipients =['panxiaoming@htsc.com', 'wuyushuang@htsc.com', 'zhouyou@htsc.com','wuchenggang@htsc.com',
        #                 'yangshiwei@htsc.com', 'zhaoyuming@htsc.com', 'xiangwanyu@htsc.com','wangjing013550@htsc.com',
        #                 'xieluyao@htsc.com','sunshaosen@htsc.com','fengchi@htsc.com',
        #                 'xuxinyi@htsc.com', 'kongjianyang@htsc.com']
        # ht_recipients =['minhuang@htsc.com']

        # DEBUG用
        to_recipients = ['sunshaosen@htsc.com']
        cc_recipients = ['fengchi@htsc.com']
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

            body = f'陈老师，您好！\n\n      麻烦把{new_stock_str}加一下事件型交易证券池和证投部交易证券池，谢谢！\n​\n' + \
                    '祝好\n--------------------------------------------------------------\n\n冯 炽\n证券投资部 金融工程团队\n' + \
                    '华泰证券股份有限公司\n手机：(+86) 15150687511\n邮件：fengchi@htsc.com\n邮编：210019\n地址：南京市江东中路228号华泰证券广场一号楼7层'

            # mailer.send_mail(subject='上市股票入池申请-%s' % today, body=body,
            #                  to_recipients=to_recipients, cc_recipients=cc_recipients)
            message = ht_str + '已发送邮件，明日上市新股：' + new_stock_str
        else:
            message = '未发送邮件，明日没有上市新股'
            print(message)
        lm.sendMessage(message)
    else:
        print('今天是非交易日，不查询')
except Exception as e:
    lm.sendMessage('！！！错误：入库报错')
