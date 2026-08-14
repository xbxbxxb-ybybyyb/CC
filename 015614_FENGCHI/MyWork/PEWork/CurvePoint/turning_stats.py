# coding: utf-8
# Author：fengchi863
# Date ：2022/2/14 16:25
import os
import sys
import pandas as pd

turning_data_path = '/data/group/800442/800319/Afengchi/junk_data/300750_turning_data/'

if __name__ == '__main__':
    filenames = os.listdir(turning_data_path)
    filenames.sort()
    rec_dict = dict()
    for fn in filenames:
        df = pd.read_excel(turning_data_path + fn, index_col=0)
        turning_num = len(df)
        diff_mean = df['延迟时间'].mean()
        rec_dict[int(fn.split('.')[0])] = [turning_num, diff_mean]
    df = pd.DataFrame().from_dict(rec_dict, orient='index', columns=['拐点个数', '延迟平均时间'])
