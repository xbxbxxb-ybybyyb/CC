# coding: utf-8
# Author：fengchi863
# Date ：2022/8/25 10:05

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
fd = FactorData()

wind_concept = fd.get_factor_value('WIND_AIndexDescription', S_INFO_WINDCODE="like'884%'")
wind_concept['S_INFO_NAME'] = wind_concept['S_INFO_NAME'].str.replace('指数', '')
wind_concept = wind_concept[wind_concept['CHANGE_HISTORY'].astype(str).str.contains('概念')]  # 筛选概念、题材
wind_concept = wind_concept[~wind_concept['CHANGE_HISTORY'].astype(str).str.contains('停用')]
print(f'Wind剔除前概念数量：{len(wind_concept)}')
wind_concept = wind_concept[~wind_concept['S_INFO_NAME'].str.contains('退市|板|全A|新股|振幅|低价|高价|点位贡献|重组|定增|回购|预增|龙虎榜|领涨龙头|金股|精选|中非合作|国资|台资|陆股通')]
wind_concept_list = wind_concept['S_INFO_WINDCODE'].tolist()
code_concept_dict = wind_concept[['S_INFO_WINDCODE', 'S_INFO_NAME']].set_index('S_INFO_WINDCODE').to_dict()

member0 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE='<20200101', F_INFO_WINDCODE="like'884%'")  # 进出记录需要取全部时间区间，数量超过上限分为两部分。
member1 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE='>=20200101', F_INFO_WINDCODE="like'884%'")
wind_member = pd.concat([member0, member1], ignore_index=True)
wind_member = wind_member.query('CUR_SIGN==1')
member_group = wind_member.groupby('F_INFO_WINDCODE')['S_CON_WINDCODE'].count()
member_group = pd.DataFrame(member_group[wind_concept_list])
member_group['概念名称'] = member_group.index.map(lambda x: code_concept_dict['S_INFO_NAME'][x])

from LucienUtil.FileUtil import FileUtil
FileUtil.save_df2xls(member_group, '/data/user/015614/tmp概念分析/', 'Wind概念成分股数量.xlsx')
from dataApi.sendInfo import send_file
send_file('/data/user/015614/tmp概念分析/Wind概念成分股数量.xlsx')
pass
