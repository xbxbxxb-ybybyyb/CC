import os

path = os.getcwd()
print(path)
os.system("python3 %s/bak/cpp_params_transfer_20230911.py"%path)
os.system("python3 %s/upload_cpp_to_xtrader.py"%path)
os.system("python3 %s/upload_to_xtrader.py"%path)


from xquant.xqutils.helper import link
lm = link.LinkMessage()
lm.sendMessage('cpp prod param ready')