# coding: utf-8
# Author：fengchi863
# Date ：2022/8/3 18:20
import sys
sys.path.append('/data/user/015614/Lucien')

try:
    from exchangelib import Message, Mailbox, Credentials, Account, FileAttachment
except:
    import os
    print('开始安装库')
    os.system('pip3 install exchangelib')
    print('exchangelib安装成功')
    from exchangelib import Message, Mailbox, Credentials, Account, FileAttachment
from MixedWork.SendStockEmail.password import password

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


if __name__ == '__main__':
    stock_str = '000981.SZ（银亿股份）'
    #！！！注意：如果是st股票摘帽，需要是证投部交易证券池。如果是王敬的非次新股策略，需要是事件型交易证券池。
    univ = '证投部交易证券池'  # '证投部交易证券池' or '事件型交易证券池'
    mailer = None
    try:
        mailer = ExchangeMailer('fengchi@htsc.com', password, 'fengchi@htsc.com') #！！！注意，修改为自己的邮箱账号密码，每半年修改办公密码记得同步修改
    except Exception as e:
        print(e)

    # to_recipients = ['chenminhang@htsc.com']
    # cc_recipients = ['panxiaoming@htsc.com', 'zhouyou@htsc.com', 'wuyushuang@htsc.com', 'wuchenggang@htsc.com',
    #                  'yangshiwei@htsc.com', 'zhaoyuming@htsc.com', 'xiangwanyu@htsc.com',
    #                  'wangjing013550@htsc.com', 'xieluyao@htsc.com', 'sunshaosen@htsc.com', 'fengchi@htsc.com']

    # DEBUG用
    to_recipients = ['sunshaosen@htsc.com']
    cc_recipients = ['fengchi@htsc.com']

    body = f'陈老师，您好！\n\n      麻烦把{stock_str}加一下{univ}，谢谢。\n​\n' + \
           '祝好\n--------------------------------------------------------------\n\n冯 炽\n证券投资部 金融工程团队\n' + \
           '华泰证券股份有限公司\n手机：(+86) 15150687511\n邮件：fengchi@htsc.com\n邮编：210019\n地址：南京市江东中路228号华泰证券广场一号楼7层'

    mailer.send_mail(subject='股票入池申请', body=body,
                     to_recipients=to_recipients, cc_recipients=cc_recipients)