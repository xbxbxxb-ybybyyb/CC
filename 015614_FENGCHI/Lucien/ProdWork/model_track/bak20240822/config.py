# coding: utf-8
# Author：fengchi863
# Date ：2023/5/22 14:05
import os
import matplotlib.pyplot as plt
from ProdWork.model_track.modeltrack_Tool_v2 import *

# year_start_date = '20221230'
year_start_date = '20230101'
end_date = '20240627' # TODO: change this: 本周三，复盘前一天
end_date_str = end_date[0:4] + '-' + end_date[4:6] + '-' + end_date[6:8]
# end_date_lw ='20240816' # TODO: change this: 本周二，复盘前一天的再前一天
end_date_lw ='20240628'
year_start_date_h = year_start_date[0:4] + '-' + year_start_date[4:6] + '-' + year_start_date[6:8]
end_date_h = end_date_lw[0:4] + '-' + end_date_lw[4:6] + '-' + end_date_lw[6:8]

savepath = '/data/user/015614/daily/复盘/策略模拟跟踪/%s/' % end_date_lw
picture_savepath = savepath + 'picture/'
os.makedirs(savepath, exist_ok=True)

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

def basic_sample_out_nice(data_in):
    data_in_temp = data_in.reset_index()
    data_in_temp['dt'] = data_in_temp['dt'].apply(lambda x: x.strftime('%Y-%m-%d'))
    return data_in_temp

def generate_sheet(workbook, savepath, strategy, tot_local_predict_summary, tot_local_return, model_num, version_num):
    wformat1 = workbook.add_format({'border': 2, 'align': 'center', 'valign': 'vcenter'})
    tot_local_predict_summary_outv1 = tot_local_predict_summary.T.reset_index().rename(columns={'index': 'model'})

    data = basic_sample_out_nice(tot_local_return).set_index('dt')
    plt.clf()
    plt.figure(figsize=(30, 20))
    if model_num <= 7:
        plt.plot(data.index, data[data.columns[0:model_num]])
    else:
        plt.plot(data.index, data[data.columns[0:7]])
        plt.plot(data.index, data[data.columns[7:model_num]], '--')

    plt.xticks(rotation=45)
    plt.rcParams['font.size'] = 15
    plt.legend(data.columns, loc='best')
    plt.savefig('%s模型跟踪%s策略_%s_%s.png' % (savepath, strategy, year_start_date, end_date_lw))
    worksheet = workbook.add_worksheet('本地样本跟踪v%s' % version_num)
    end_idx = write_excel_helpTotal_graph(worksheet, tot_local_predict_summary_outv1, 1, wformat1, '%s模型跟踪%s策略_%s_%s.png' % (savepath, strategy, year_start_date, end_date_lw))

