import pandas as pd
import IO

md_data = IO.read_data([20150901, 20240331],
                       # columns=['amt', 'high','open','close','pre_close'],
                        alt='/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
md_data = md_data.sort_values(['dt','Ticker'])
'''
Index(['OBJECT_ID', 'CRNCY_CODE', 'S_DQ_PRECLOSE', 'S_DQ_OPEN', 'S_DQ_HIGH',
       'S_DQ_LOW', 'S_DQ_CLOSE', 'S_DQ_CHANGE', 'S_DQ_PCTCHANGE',
       'S_DQ_VOLUME', 'S_DQ_AMOUNT', 'SEC_ID', 'OPDATE', 'OPMODE'],
      dtype='object')
分3个档位：
1、前日收盘在5日线下，10日线下，20日线下，且5日线<20日线，最低 （长短期都GG）
2、前日收盘超过5，10，20的任意均线 和 5日线<20均线 只满足1个，中档
3、高档
'''
md_data = md_data.query('Ticker == "000852.SH"')
# md_data = md_data.set_index(['dt','Ticker'])
md_data['mean5'] = md_data['S_DQ_CLOSE'].unstack().rolling(5,1).mean().stack()
md_data['mean10'] = md_data['S_DQ_CLOSE'].unstack().rolling(10,1).mean().stack()
md_data['mean20'] = md_data['S_DQ_CLOSE'].unstack().rolling(20,1).mean().stack()
md_data['1_1'] = md_data['S_DQ_CLOSE'] < md_data['mean5']
md_data['1_2'] = md_data['S_DQ_CLOSE'] < md_data['mean10']
md_data['1_3'] = md_data['S_DQ_CLOSE'] < md_data['mean20']
md_data['1'] = md_data['1_1']&md_data['1_2']&md_data['1_3']
md_data['2_1'] = md_data['mean5'] < md_data['mean20']
md_data['res'] = 3
md_data.loc[(md_data['1']) & (md_data['2_1']),'res'] = 1
md_data.loc[(~(md_data['1'])) | (~(md_data['2_1'])),'res'] = 2
md_data.loc[(~(md_data['1'])) & (~(md_data['2_1'])),'res'] = 3

md_data['res_final'] = md_data['res'].unstack().shift(1).stack()

md_data['label'] = md_data['S_DQ_PCTCHANGE'].unstack().shift(-1).stack()
md_data[['res_final']].to_pickle('/data/user/015585/share_file/for_wj/仓位控制.pkl')