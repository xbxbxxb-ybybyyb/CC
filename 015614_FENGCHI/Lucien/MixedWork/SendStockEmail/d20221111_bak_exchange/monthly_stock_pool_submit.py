# coding: utf-8
# Author：fengchi863
# Date ：2022/8/31 20:38

import numpy as np
import pandas as pd
from MixedWork.GreyStockGenerator import IO
from exchangelib import Message, Mailbox, Credentials, Account, FileAttachment
from MixedWork.SendStockEmail.password import password
from tqdm import tqdm
import time
import warnings
warnings.filterwarnings('ignore')

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
        messeage = Message(account=self.account, subject=subject, body=body, to_recipients=to_recipients, cc_recipients=cc_recipients)
        for attachment_file in attachment_files:
            attachment_name = attachment_file[attachment_file.rindex('\\') + 1:]
            myfile = FileAttachment(name=attachment_name, content=open(attachment_file, 'rb').read())
            messeage.attach(myfile)
        messeage.send()
        print('邮件发送成功')

    def check_title_in_received(self, title_str, sender=None, check_num=100):
        res_dic = {}
        items = self.account.inbox.all().order_by('-datetime_received')[:check_num]
        for item in tqdm(items):
            tradingday = int(item.datetime_sent.strftime('%Y%m%d'))
            if (tradingday < start_date) or (tradingday > end_date):
                continue
            if ((item.subject is not None) and (title_str in item.subject)) and ((sender is None) | (item.sender.name == sender)):
                key = item.subject + '-%s' % tradingday
                if key in res_dic:
                    res_dic[key + str(item.datetime_sent)[-10:]] = item.text_body
                else:
                    res_dic[key] = item.text_body
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
        mailer = ExchangeMailer('015614', password, 'fengchi@htsc.com')
        flag = True
    except Exception as e:
        print(e)
    start_date, end_date = 20221001, 20221031
    # email_dic1 = mailer.check_title_in_received('入池申请', sender='王伟地', check_num=1000)
    # email_dic2 = mailer.check_title_in_received('入池申请', sender='孙少森', check_num=1000)
    email_dic2 = mailer.check_title_in_received('入池申请', sender='冯炽', check_num=1000)
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
    event_df['股票代码'] = event_list
    event_df['股票代码'] = event_df['股票代码'].apply(lambda x: x[:6] + '.SH' if x[0] == '6' else x[:6] + '.SZ')

    name_data = IO.read_data([end_date, end_date], alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
    for index, row in event_df.iterrows():
        if (pd.to_datetime(str(end_date)), row['股票代码']) in name_data.index:
            event_df.loc[index, '证券名称'] = name_data.loc[pd.to_datetime(str(end_date)), row['股票代码']]['STOCK_NAME'].values[0]
        else:
            event_df.loc[index, '证券名称'] = str(np.nan)

    zt_list = [stock for stock in zt_list if '华泰联合' not in stock]
    zt_list = np.unique([stock[:stock.index("(")] if '(' in stock else stock[:stock.index("（")] for stock in zt_list])
    zt_df = pd.DataFrame()
    zt_df['股票代码'] = zt_list
    zt_df['股票代码'] = zt_df['股票代码'].apply(lambda x: x[:6] + '.SH' if x[0] == '6' else x[:6] + '.SZ')
    for index, row in zt_df.iterrows():
        if (pd.to_datetime(str(end_date)), row['股票代码']) in name_data.index:
            zt_df.loc[index, '证券名称'] = name_data.loc[pd.to_datetime(str(end_date)), row['股票代码']]['STOCK_NAME'].values[0]
        else:
            zt_df.loc[index, '证券名称'] = str(np.nan)

    from dataApi.sendInfo import send_file
    send_file(event_df)
    time.sleep(5)
    send_file(zt_df)