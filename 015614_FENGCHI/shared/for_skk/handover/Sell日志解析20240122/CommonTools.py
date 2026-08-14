import pandas as pd
import numpy as np
import datetime as dt
import ftplib
import os
import re
import shutil
from io import BytesIO
#import win32com.client
def excel_saver(output_dict, excel_name):
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer, sheet_name=key)
    writer.save()
    print('create sheets %s for %s！！！！！！！！！！' % (list(output_dict.keys()), excel_name))
    return
def judge_updatedate(data_path, date):
    if data_path.split('.')[-1] == 'h5':
        data = pd.read_hdf(data_path).sort_index()
    elif data_path.split('.')[-1] == 'pkl':
        data = pd.read_pickle(data_path).sort_index()
    Flag = 1 if data.index.tolist()[-1][0] >= pd.Timestamp(str(date)) else 0
    return Flag
def write_excel_helpTotal_graph(worksheet, sampleDf, begin_idx, wformat1, img_path=None):
    l = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    row_count = 0
    col_count = 0
    for column in sampleDf.columns:
        worksheet.write(l[col_count] + str(begin_idx + row_count), column, wformat1)
        col_count += 1
    row_count += 1
    for index, row in sampleDf.iterrows():
        col_count = 0
        for column in sampleDf.columns:
            worksheet.write(l[col_count] + str(begin_idx + row_count), row[column], wformat1)
            col_count += 1
        row_count += 1
    if img_path is not None:
        # 将字节流图片写入单元格，文件名必须显式指定。
        x_scale, y_scale, placement = 0.4, 0.5, 'C3'
        image_file = open(img_path, 'rb')
        image_data = BytesIO(image_file.read())
        image_file.close()
        worksheet.insert_image(placement, img_path,
                               {'x_scale': x_scale,
                                'y_scale': y_scale,
                                'image_data': image_data,
                                'positioning': None,
                                })
    return begin_idx + row_count
def int_2_stock_code(number):
    str_number = str(number)
    if number < 99999:
        while len(str_number) < 6:
            str_number = '0' + str_number
    if str_number[0] == '6':
        str_number = str_number + '.SH'
    else:
        str_number = str_number + '.SZ'
    return str_number
def list_to_df(list_need,date,name):
    if len(list_need) == 0:
        return pd.DataFrame()
    else:
        out_df = pd.DataFrame(list_need,columns = ['Ticker'])
        out_df['dt'] = pd.Timestamp(date)
        out_df[name] = 1
        return out_df.set_index(['dt','Ticker'])
def ftp_download(f,file_remote, file_local, show=True):
    '''以二进制形式下载文件'''
    bufsize = 8192  # 设置缓冲器大小
    fp = open(file_local, 'wb')
    f.retrbinary('RETR %s' % file_remote, fp.write, bufsize)
    fp.close()
    if show: print(file_remote, 'to%s,下载成功' % file_local)

def ftp_upload(f, file_remote, file_local):
    '''以二进制形式上传文件'''
    bufsize = 8192  # 设置缓冲器大小
    fp = open(file_local, 'rb')
    f.storbinary('STOR ' + file_remote, fp, bufsize)
    fp.close()
    print(file_local, 'from%s,上传成功' % file_remote)

def createPath(predict_file_save_path):# = r'/data/group/800463/日内强势股/log_parse/模型差异/%s/预测概率差异/' % (tradeDatestr)
    if not os.path.exists(predict_file_save_path):
        os.makedirs(predict_file_save_path)
        print('create path:%s'%predict_file_save_path)
        return
    else:
        return
# 检查行情延迟
def cal_time_delta(start, end):
    start_str = str(start)
    end_str = str(end)
    time_delta = (int(end_str[:~6]) - int(start_str[:~6])) * 3600000 + \
                 (int(end_str[~6:~4]) - int(start_str[~6:~4])) * 60000 + \
                 (int(end_str[~4:~2]) - int(start_str[~4:~2])) * 1000 + \
                 (int(end_str[~2:]) - int(start_str[~2:]))
    if (start < 120000000) & (end > 120000000):
        time_delta = time_delta - 5400000
    return time_delta
def cal_delay_time(start, end):
    start_str = str(start).zfill(9)
    end_str = str(end).zfill(9)
    time_delta = (int(end_str[:~6]) - int(start_str[:~6])) * 3600000 + \
                 (int(end_str[~6:~4]) - int(start_str[~6:~4])) * 60000 + \
                 (int(end_str[~4:~2]) - int(start_str[~4:~2])) * 1000 + \
                 (int(end_str[~2:]) - int(start_str[~2:]))
    if (start < 120000000) & (end > 120000000):
        time_delta = time_delta - 5400000
    return time_delta
def cal_ul_price(md_close_pre_close):
    md_close_pre_close['ul_price'] = np.floor(md_close_pre_close['pre_close'] * 100 * 1.1 + 0.5) / 100
    md_close_pre_close['new_300'] = (md_close_pre_close.reset_index()['Ticker'].apply(lambda x: x[0] == '3') & (
            md_close_pre_close.reset_index()['dt'] >= '20200824')).values
    md_close_pre_close.loc[md_close_pre_close['new_300'], 'ul_price'] = np.floor(
        md_close_pre_close.loc[md_close_pre_close['new_300'], 'pre_close'] * 100 * 1.2 + 0.5) / 100
    return md_close_pre_close['ul_price']
def del_file(filepath):
    """
    删除某一目录下的所有文件或文件夹
    :param filepath: 路径
    :return:
    """
    del_list = os.listdir(filepath)
    for f in del_list:
        file_path = os.path.join(filepath, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

def isException(line):
    keyWordForException = {'ERROR', 'Exception', 'WARN'}
    for keyWord in keyWordForException:
        if keyWord in line:
            return True
    return False

def trans_str2dic(str_line):
    #print(str_line)
    if str_line.find('NaN')>=0:
        print(str_line)
    str_line = str_line.replace('NaN', '0')
    str_line = str_line.replace('nan', '0')
    str_line = str_line.replace('null', '0')
    str_line = str_line.replace('{', "{'")
    str_line = str_line.replace('=', "':")
    str_line = str_line.replace(' ', " '")
    str_line = str_line.replace(', \'}', "}")
    str_line = str_line.replace('Infinity', "0")

    return eval(str_line)

def strTime2MDTime(str_time):
    time_str_time = str_time[str_time.index('T') + 1:str_time.index('T') + 9].split(':')
    return time_str_time[0] + time_str_time[1] + time_str_time[2] + str_time[str_time.index('.') + 1:str_time.index('.') + 4]


def inttime2str(time):
    if np.isnan(time):
        time_str_out = '150000000'
    else:
        time_str = str(time)
        if time_str[0] == '9':
            time_str = '0' + time_str
        time_str_out = time_str[0] + time_str[1] + ':' + time_str[2] + time_str[3] + ':' + time_str[4] + time_str[5] + '.' + \
                       time_str[6] + time_str[7] + \
                       time_str[8]
    return time_str_out

def getValueByKeyFromLine2(line, by, form='(.*?)[,\\\\n\n}]'):
    """给cpp日志解析symbol时使用，有时symbol在最后需要解析\\n，但如果java用这个OrderType有时候会出问题"""
    if by not in line:
        return ''
    try:
        return re.findall(r"%s=%s" % (by, form), line)[0]
    except:
        return 'other'

def getValueByKeyFromLine(line, by, form='(.*?)[,\n]'):
    """给java日志使用，或者cpp日志使用"""
    if by not in line:
        return ''
    try:
        return re.findall(r"%s=%s" % (by, form), line)[0]
    except:
        return 'other'

def getRejectReason(line, by1, by2, form='(.*?)[,\n]'):
    if by1 not in line or by2 not in line:
        return ''#getValueByKeyFromLine(line, by=by1)
    try:
        info_list = line.split(';')
        for tmp_line in info_list:
            if by1 not in tmp_line or by2 not in tmp_line:
                pass
            else:
                operation = re.findall(r"%s=%s" % (by1, form), tmp_line)[0]
                type = getValueByKeyFromLine(tmp_line, by=by2)#re.findall(r"%s=%s" % (by2, form), tmp_line)[0]
                if str(operation).find('2')>=0:# and str(type).find('Z')>=0:
                    return type
                else:
                    continue
        return getValueByKeyFromLine(line, by=by2)#
    except:
        return getValueByKeyFromLine(line, by=by2)#

# by fengc 20230605
def getRiskViolateRemark(line, by1, form='(.*?)[,}\n]'):
    if by1 not in line and '隔离池' not in line:
        return ''
    try:
        hegui_list = re.findall(r"%s=%s" % (by1, form), line)
        return list(filter(lambda x: '隔离池' in x, hegui_list))[0]
    except:
        return 'other'
    return

def getMriskFlag(line, by1, by2, form='(.*?)[,\n]'):
    if by1 not in line or by2 not in line:
        return ''
    try:
        info_list = line.split(';')
        for tmp_line in info_list:
            if by1 not in tmp_line or by2 not in tmp_line:
                pass
            else:
                operation = re.findall(r"%s=%s" % (by1, form), tmp_line)[0]
                type = re.findall(r"%s=%s" % (by2, form), tmp_line)[0]
                if str(operation).find('2')>=0 and str(type).find('Z')>=0:
                    return 'Mrisk'
                else:
                    continue
        return 'otherReason'
    except:
        return 'other'
def getMriskInfo(line, by1, form='(.*?)[,\n]'):
    try:
        info_list = line.split(';')
        for tmp_line in info_list:
            if by1 not in tmp_line:
                pass
            else:
                operation = re.findall(r"%s=%s" % (by1, form), tmp_line)[0]
                if str(operation).find('拉抬打压')>=0:
                    return operation
                else:
                    continue
        return operation
    except:
        return 'other'

def cal_time_delta(start, end):
    start_str = str(start)
    end_str = str(end)
    time_delta = (int(end_str[:~6]) - int(start_str[:~6])) * 3600000 + \
                 (int(end_str[~6:~4]) - int(start_str[~6:~4])) * 60000 + \
                 (int(end_str[~4:~2]) - int(start_str[~4:~2])) * 1000 + \
                 (int(end_str[~2:]) - int(start_str[~2:]))
    if (start < 120000000) & (end > 120000000):
        time_delta = time_delta - 5400000
    return time_delta
def strTime2MDTime(str_time):
    time_str_time = str_time[str_time.index('T') + 1:str_time.index('T') + 9].split(':')
    return time_str_time[0] + time_str_time[1] + time_str_time[2] + str_time[str_time.index('.') + 1:str_time.index('.') + 4]
def isException(line):
    keyWordForException = {'ERROR', 'Exception', 'WARN'}
    for keyWord in keyWordForException:
        if keyWord in line:
            return True
    return False
# def trans_str2dic(str_line):
#     str_line = str_line.replace('{', "{'")
#     str_line = str_line.replace('=', "':")
#     str_line = str_line.replace(' ', " '")
#     return eval(str_line)
def number2stockcode(x):
    x_str = str(int(x))
    while len(x_str) < 6:
        x_str = '0'+ x_str
    if x_str[0] == '6':
        x_str = x_str+'.SH'
    else: x_str = x_str+'.SZ'
    return x_str
def cal_cumsum_mean(df,step_num):
    ret = pd.DataFrame(index = df.index, columns = ['cumulated_average_by_sample'])
    index_set = ret.index.tolist()
    ret['cumulated_average_by_sample']=0
    for tmp_num in list(range(step_num-1,len(ret))):
        tmp_index = index_set[tmp_num]
        ret.loc[tmp_index,'cumulated_average_by_sample'] = float(df.iloc[:tmp_num+1].mean())
    return ret

def format_unix2dt(unix_int):
    timeStamp = float(unix_int) / 1000
    ret_datetime = dt.datetime.utcfromtimestamp(timeStamp) + dt.timedelta(hours=8)
    ret_datetime = ret_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")
    ret_datetime = ret_datetime[:-3] + '+0800'
    return ret_datetime

def format_lastMatchTime2dt(unix_int):
    """为了处理当时lastMatchTime时间格式不匹配的情况，一种是168开头的可以用正常转换的，一种是正常时间94430000"""
    today_date = dt.datetime.today().strftime('%Y-%m-%d')
    if len(unix_int) > 8:
        timeStamp = float(unix_int) / 1000
        ret_datetime = dt.datetime.utcfromtimestamp(timeStamp) + dt.timedelta(hours=8)
        ret_datetime = ret_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")
        ret_datetime = ret_datetime[:-3] + '+0800'
    else:
        unix_int = unix_int.zfill(9)
        ret_datetime = today_date + 'T' + unix_int[:2] + ':' + unix_int[2:4] + ':' + unix_int[4:6] + '.' + '000+0800'
    return ret_datetime

'''def pwd_xlsx(old_filename, new_filename, pwd_str, pw_str=''):
    xcl = win32com.client.Dispatch("Excel.Application")
    # pw_str为打开密码, 若无 访问密码, 则设为 ''
    wb = xcl.Workbooks.Open(old_filename, False, False, None, pw_str)
    xcl.DisplayAlerts = False

    # 保存时可设置访问密码.
    wb.SaveAs(new_filename, None, pwd_str, '')

    xcl.Quit()'''
