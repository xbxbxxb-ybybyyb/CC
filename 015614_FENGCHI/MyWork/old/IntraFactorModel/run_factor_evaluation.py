# @Time : 2020/5/15 10:37
# @Author : Zhichen Lu
# @File : run_factor_evaluation.py

import os
import time
from multiprocessing import Pool

import pandas as pd

from RoughBackTest.FactorBackTest import FactorBackTest
from conf.feature_config import drop_list

e = time.time()
ft = FactorBackTest()
print('initialization',time.time()-e)
file_dir = r'/data/group/800319/storeFactor/original_intrafactor/'
factor_name_list = sorted([os.path.splitext(x)[0] for x in os.listdir(file_dir)])
factor_name_list = list(filter(lambda x: x.strip('.h5') not in drop_list, factor_name_list))
def wraper(factor_name):
    if os.path.exists('/data/group/800319/junkData/IntraFactorModel/FactorEvaluation_1min/%s.xlsx' % factor_name):
        print(factor_name,'exist')
        return 0
    try:
        factor = pd.read_hdf(file_dir+factor_name+'.h5',factor_name)
        ft.calc_out_result(factor, file_name=factor_name, n=1, path='/data/group/800319/junkData/IntraFactorModel/FactorEvaluation_1min/')
        print(factor_name,'done')
    except:
        print(factor_name,'Wong')
        pd.DataFrame().to_excel('/data/group/800319/junkData/IntraFactorModel/FactorEvaluation_1min/Wrong_%s.xlsx' % factor_name)


if not os.path.exists('/data/group/800319/junkData/IntraFactorModel/FactorEvaluation_1min/'):
    os.mkdir('/data/group/800319/junkData/IntraFactorModel/FactorEvaluation_1min/')


def main(i):
    # wraper(factor_name_list[14])
    pool = Pool(4)
    r = pool.map(wraper, factor_name_list)
    # r = pool.map(wraper, factor_name_list[(i - 1) * len(factor_name_list) // 4:i ** len(factor_name_list) // 4])
    pool.close()
    pool.join()


def integration(path):
    file_list = os.listdir(path)
    file_list = list(filter(lambda x: 'Wrong' not in x and 'result' not in x, file_list))
    result = pd.DataFrame()
    for file_name in file_list:
        temp_df = pd.read_excel(path + file_name, index_col=0)
        temp_df = temp_df.drop([2019, 'all'])
        temp_df.loc['all'] = temp_df.mean()
        temp_df.loc['all', '累计单利'] = temp_df.drop('all')['累计单利'].sum()
        temp_df['盈亏比'] = temp_df['盈亏比'] * -1
        temp_df = temp_df.stack().reset_index()
        temp_df.index = temp_df['level_1'] + '_' + temp_df['year'].astype(str)
        temp_df = temp_df[[0]].rename(columns={0: file_name.strip('.xlsx')}).T
        result = pd.concat([result, temp_df])
        print(file_name)
    all_list = list(filter(lambda x: 'all' in x, result.columns.tolist()))
    evaluation_indicator = result[all_list].rank(pct=True)
    factor_rank = evaluation_indicator.drop('日均信号次数_all', axis=1).sum(axis=1).sort_values(ascending=False)
    factor_list = factor_rank[:50].index.tolist()
    print(factor_list)
    result.to_excel(path + 'result_integration.xlsx')
if __name__=="__main__":
    main(4)
    integration('/data/group/800319/junkData/IntraFactorModel/FactorEvaluation/')
