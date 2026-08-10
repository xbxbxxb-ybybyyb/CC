from ftplib import FTP            #加载ftp模块



def downloadfile(remotepath, localpath):
	# remotepath = "/home/pub/dog.jpg";  
	# localpath = 'f:\\test\\dog.jpg'  
	fp = open(localpath,'wb') #以写模式在本地打开文件
	bufsize = 1024
	ftp.retrbinary('RETR ' + remotepath,fp.write,bufsize) 
 #退出ftp服务器

if __name__ == '__main__':
	ftp=FTP()
	ftp.set_debuglevel(2)             #打开调试级别2，显示详细信息
	ftp.connect('168.8.2.68')          #连接的ftp sever和端口
	ftp.login("XTrader","XTrader@123")      #连接的用户名，密码
	file_list = ftp.nlst('/XQuant/013160') 
	# print(ftp.dir('/XQuant/013160'))
	date_list = [20180808]
 
	for file in date_list:
		file = str(file) + '.csv'
		remotepath = '/XQuant/013160/index/' + file
		localpath = 'D:\\index1\\' + file
		print(remotepath, localpath)
		downloadfile(remotepath, localpath)
		print('download finish')
	for file in stock_min_list:
		remotepath = '/XQuant/013160/stock/' + file
		localpath = 'D:\\stock1\\' + file
		print(remotepath, localpath)
		downloadfile(remotepath, localpath)
		print('download finish')


	ftp.set_debuglevel(0) #关闭调试  
	# ftp.close()  
	ftp.quit()