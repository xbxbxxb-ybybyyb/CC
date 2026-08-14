# coding: utf-8
# Author：fengchi863
# Date ：2022/11/11 10:20
import sys
sys.path.append('/data/user/015614/Lucien')

from email.mime.text import MIMEText
import smtplib
from MixedWork.SendStockEmail.password import password
from email.mime.multipart import MIMEMultipart
import os
import base64


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

if __name__ == '__main__':
    stock_str = '688449.SH（联芸科技）、688605.SH（先锋精科）、688615.SH（合合信息）、688708.SH（佳驰科技）、688710.SH（益诺思）、688721.SH（龙图光罩）、688726.SH（拉普拉斯）、688750.SH（金天钛业）'
    # stock_str = '600182.SH（S佳通）、000995.SZ（皇台酒业）'
    # ！！！注意：如果是st股票摘帽，需要是证投部交易证券池。如果是王敬的非次新股策略，需要是事件型交易证券池。
    # univ = '事件型交易证券池'  # '证投部交易证券池' or '事件型交易证券池'
    univ = '证投部交易证券池'  # '证投部交易证券池' or '事件型交易证券池'
    cm = None
    try:
        cm = CoreMailer()
    except Exception as e:
        print(e)

    # to_recipients = ['lijianfeng@htsc.com']
    # cc_recipients = ['panxiaoming@htsc.com', 'zhouyou@htsc.com', 'wuyushuang@htsc.com',
    #                  'yangshiwei@htsc.com', 'zhaoyuming@htsc.com', 'xiangwanyu@htsc.com', 'yiwenxiu@htsc.com',
    #                  'wangjing013550@htsc.com', 'xieluyao@htsc.com', 'sunshaosen@htsc.com', 'fengchi@htsc.com',
    #                  'zhangjinkang@htsc.com']

    # DEBUG用
    to_recipients = ['fengchi@htsc.com']
    cc_recipients = ['sunshaosen@htsc.com']

    body = f'李老师，您好！\n\n      麻烦把{stock_str}加一下{univ}，谢谢。\n​\n' + \
           '祝好\n--------------------------------------------------------------\n\n冯 炽\n证券投资部 金融工程团队\n' + \
           '华泰证券股份有限公司\n手机：(+86) 15150687511\n邮件：fengchi@htsc.com\n邮编：210019\n地址：南京市江东中路228号华泰证券广场一号楼7层'

    cm.send_mail(subject='股票入池申请', body=body,
                     to_recipients=to_recipients, cc_recipients=cc_recipients)
    print('已成功发送邮件')