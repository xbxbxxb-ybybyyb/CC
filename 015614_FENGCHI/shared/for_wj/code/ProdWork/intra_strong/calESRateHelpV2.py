# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 11:10:38 2019
jupiter和saturn公用
@author: 013551
"""
import numpy as np
from LucienUtil import IO


IO_mother_dir = '/data/group/800080/warehouse_event'
# 获取额外买入信息
def getExtraBuyInfo(df):
    floatColumns = ['成交数量','成交金额','成交均价']
    df[floatColumns] = df[floatColumns].astype(float)
    if len(df) != 0:
        Adate = str(df.iloc[0]['发生日期'])
        date = Adate[:4]+Adate[5:7]+Adate[8:10]

        f_data = IO.read_data([date, date], columns=['open', 'pre_close', 'close','high']
                          , alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        for index,row in df.iterrows():
            stockCode = row['证券代码']
            print(stockCode,date)
            open_,pre_close,close,high = f_data.loc[date,stockCode].values
            highLimitedPrice = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
            if (stockCode[0] == '3') & (date >= '20200824'):
                highLimitedPrice = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
            df.loc[index,'买入当天收盘价'] = close
            df.loc[index,'买入当天开盘价'] = open_
            df.loc[index,'买入当天前收价'] = pre_close
            df.loc[index,'买入当天开盘涨幅(%)'] = (open_/pre_close - 1) * 100
            if (close>=highLimitedPrice):
                df.loc[index,'买入当天是否收盘涨停']=1
            else:
                df.loc[index,'买入当天是否收盘涨停']=0
            if (high>=highLimitedPrice):
                df.loc[index,'买入当天盘中是否涨停']=1
            else:
                df.loc[index,'买入当天盘中是否涨停']=0
            df.loc[index,'买入当天涨停价'] = highLimitedPrice
            df.loc[index,'买入当日收益率(%)'] = (close-row['成交均价'])/row['成交均价'] * 100
    return df
# 获取额外卖出信息
def getExtraSellInfo(df):
    df['卖出日期开盘价'] = ''
    for index,row in df.iterrows():
        # index = 0
        # row = df.loc[0]
        stockCode = df.loc[index,'证券代码']
        date = str(df.loc[index,'发生日期'])
        date_suit = date[0:4]+date[5:7]+date[8:10]
        print(stockCode,date)
        f_data = IO.read_data([date_suit, date_suit],
                              columns=['open','vwap']
                              , alt=IO_mother_dir+'/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
        openPrice,vwapPrice = f_data.loc[date,stockCode].values
        df.loc[index,'卖出日期开盘价'] = openPrice
        df.loc[index,'卖出日期均价'] = vwapPrice
    return df
# 计算jupiter单样本收益情况
def calProfit(df):
    df.replace(np.nan,'',inplace=True)
    for index,row in df.iterrows():
        # index = 299
        # row = df.loc[index]
        if row['卖出比例']=='100.00%':#如果已全部卖出，没必要再算一遍
            continue
        sellVolume = row['卖出数量']
        sellPrice = row['卖出成交均价']
        sellAmt = row['卖出金额']
        sellOpenPrice = row['卖出日期开盘价']
        buyPrice = row['买入成交均价']
        buyUlPrice = row['买入当天涨停价']
        buyVolume = row['买入数量']

        if sellVolume!='':
            sellVolumeList = str(sellVolume).split(',')
            sellPriceList = str(sellPrice).split(',')
            sellOpenPriceList = str(sellOpenPrice).split(',')
            sellAmtList = str(sellAmt).split(',')
            sellVolumeSum = sum([float(x) for x in sellVolumeList])
            sellAmtSum = sum([float(x) for x in sellAmtList])
            sellOpenAmtSum = sum([float(x)*float(y) for x,y in zip(sellOpenPriceList,sellVolumeList)])
            buyPartAmt = sellVolumeSum * buyPrice
            buyPartUlAmt = sellVolumeSum * buyUlPrice
            #df.loc[index,'卖出部分盈利金额'] = sellAmtSum*0.999 - buyPartAmt
            df.loc[index, '卖出部分盈利金额'] = sellAmtSum * 0.999 - buyPartAmt - (buyPartAmt+sellAmtSum)*0.0000887
            df.loc[index,'卖出部分收益率(%)'] = df.loc[index, '卖出部分盈利金额']/buyPartAmt * 100
            if sellVolumeSum==buyVolume:
                df.loc[index,'是否全部卖出'] = 1
                df.loc[index,'实际是否正收益'] = (1 if sellAmtSum*0.999>=buyPartAmt else 0)
                df.loc[index,'理论是否正收益'] = (1 if sellOpenAmtSum>=buyPartUlAmt else 0)
                if (df.loc[index,'买入当天是否收盘涨停']==1)&(df.loc[index,'理论是否正收益']==1):
                    df.loc[index,'理论是否预测正确'] = 1
                else:
                    df.loc[index,'理论是否预测正确'] = 0
            else:
                df.loc[index,'是否全部卖出'] = 0
    return df

# 计算saturn单样本收益情况
def calProfit_pj2(df,strategy='saturn'):
    df.replace(np.nan,'',inplace=True)
    for index,row in df.iterrows():
        if row['卖出比例']=='100.00%':#如果已全部卖出，没必要再算一遍
            continue
        sellVolume = row['卖出数量']
        sellAmt = row['卖出金额']
        buyPrice = row['买入成交均价']
        buyVolume = row['买入数量']
        if strategy == 'saturn':
            label = row['TN_v2o10']
        elif strategy == 'ceres':
            label = row['TN_v2o10d1']
        if label == '':
            label = -1
        if sellVolume!='':
            sellVolumeList = str(sellVolume).split(',')
            sellAmtList = str(sellAmt).split(',')
            sellVolumeSum = sum([float(x) for x in sellVolumeList])
            sellAmtSum = sum([float(x) for x in sellAmtList])
            buyPartAmt = sellVolumeSum * buyPrice
            #df.loc[index,'卖出部分盈利金额'] = sellAmtSum*0.999 - buyPartAmt
            df.loc[index, '卖出部分盈利金额'] = sellAmtSum * 0.999 - buyPartAmt - (buyPartAmt + sellAmtSum) * 0.0000887
            df.loc[index,'卖出部分收益率(%)'] = df.loc[index, '卖出部分盈利金额']/buyPartAmt * 100
            if sellVolumeSum==buyVolume:
                df.loc[index,'是否全部卖出'] = 1
                df.loc[index,'实际是否正收益'] = (1 if sellAmtSum*0.999>=buyPartAmt else 0)
                df.loc[index,'理论是否正收益'] = (1 if label>=0 else 0)
                if (df.loc[index,'理论是否正收益']==1):
                    df.loc[index,'理论是否预测正确'] = 1
                else:
                    df.loc[index,'理论是否预测正确'] = 0
            else:
                df.loc[index,'是否全部卖出'] = 0
    return df

# 写excel
def write_excel(df, path, sheetname):
    import xlsxwriter
    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet(sheetname)
    wformat1 = workbook.add_format({'border':2,'align':'center','valign':'vcenter'})
    wformat2 = workbook.add_format({'border':2,'align':'center','valign':'vcenter','num_format':2})
    end_idx = write_excel_help(worksheet, df, 1, '',wformat1, wformat2)
    workbook.close()
# 写excel
def write_excel_help(worksheet, sampleDf, begin_idx, tip, wformat1, wformat2):
    l = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')+['AA']+['AB']+['AC']+['AD']+['AE']+['AF']+['AG']+['AH']+['AI']+['AJ']+['AK']+['AL']+['AM']+['AN']+['AO']
    format2ColumnList = ['买入当日收益率(%)','涨跌幅(%)','成交均价','卖出部分收益率(%)','买入成交均价','卖出成交均价','未完成原因']
    row_count = 0
    col_count = 0
    for column in sampleDf.columns:
        worksheet.write(l[col_count]+str(begin_idx+row_count),column,wformat1)
        col_count += 1
    row_count += 1
    for index,row in sampleDf.iterrows():
        col_count = 0
        for column in sampleDf.columns:
            if column in format2ColumnList:
                worksheet.write(l[col_count]+str(begin_idx+row_count),row[column],wformat2)
            else:
                worksheet.write(l[col_count]+str(begin_idx+row_count),row[column],wformat1)
            col_count += 1
        row_count += 1
    return begin_idx+row_count
# 写excel
def write_excel_helpTotal(worksheet, sampleDf, begin_idx, col_idx, tip, wformat1, wformat2):
    l = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')+['AA']+['AB']+['AC']+['AD']+['AE']+['AF']+['AG']+['AH']+['AI']+['AJ']+['AK']
    row_count = 1
    col_count = col_idx
    worksheet.merge_range(l[col_count]+str(begin_idx+row_count)+':'+l[col_count+1]+str(begin_idx+row_count),tip,wformat2)
    row_count += 1
    for index,row in sampleDf.iterrows():
        col_count = col_idx
        for column in sampleDf.columns:
            worksheet.write(l[col_count]+str(begin_idx+row_count),row[column],wformat1)
            col_count += 1
        row_count += 1
    return begin_idx+row_count
# 写需要有图的excel（只是加载图不涉及图片如何绘制）
def write_excel_helpTotal_graph(worksheet, sampleDf, begin_idx, col_idx, tip, wformat1, wformat2, img_path):
    print('image path is:%s'%img_path)
    from io import BytesIO
    l = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')+['AA']+['AB']+['AC']+['AD']+['AE']+['AF']
    row_count = 1
    col_count = col_idx
    worksheet.merge_range(l[col_count]+str(begin_idx+row_count)+':'+l[col_count+1]+str(begin_idx+row_count),tip,wformat2)
    row_count += 1
    for index,row in sampleDf.iterrows():
        col_count = col_idx
        for column in sampleDf.columns:
            worksheet.write(l[col_count]+str(begin_idx+row_count),row[column],wformat1)
            col_count += 1
        row_count += 1
    image_file = open(img_path, 'rb')
    image_data = BytesIO(image_file.read())
    image_file.close()
    # 将字节流图片写入单元格，文件名必须显式指定。
    if '_2022' in img_path:
        x_scale, y_scale, placement = 0.8, 1, 'A65'
    elif '收益画图' in img_path:
        x_scale, y_scale, placement = 0.8,1, 'A25'
    elif '卖出画图' in img_path:
        x_scale, y_scale, placement = 0.4,0.5, 'D46'
    else: x_scale, y_scale, placement = 0.4,0.5, 'D2'
    worksheet.insert_image(placement, img_path,
                           {'x_scale': x_scale,
                           'y_scale': y_scale,
                           'image_data': image_data,
                           'positioning': None,
                           })
    return begin_idx+row_count
