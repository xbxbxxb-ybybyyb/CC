import pandas as pd
import importlib.util

T_factor_type = ["['T1mTransaction']","['T1mTickab']","['T1mTick1s']","['T1mCancel']","['T1mTickfulladdorder']","['T1mOrder']"]
check_excel = pd.read_excel('/data/user/023859/factor_zooZZ/factor_lib/check_res/check_res_tot_neptune_20250619.xlsx')
check_excel = check_excel[check_excel['pre_check'] == 'pass']
check_excel = check_excel[~check_excel['factor_type'].str.contains('xdb_tickex|xdb_trade|xdb_order')]

for idx,row in check_excel.iterrows():
    date = row['提交时间']
    factor_name = row['factor_name']
    factor_type = row['factor_type']
    if 'shortterm' in factor_name:
        continue
    if factor_type in T_factor_type and 'allterm' not in factor_name and 'longterm' not in factor_name:
        continue
    elif factor_type in T_factor_type:
        check_excel.loc[idx, '因子类型'] = str(factor_type)
        continue
    module_path = f'/data/user/023859/fefactorframework_server/factor_lib/neptune/factor_{date}/factor_{factor_name}.py'
    module_name = f'factor_{factor_name}'
    spec = importlib.util.spec_from_file_location(module_name,module_path)
    my_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(my_module)
    cls = getattr(my_module, module_name)
    factor_type = cls.t_1_factor_data_types + cls.t_day_data + [dic['name'] for dic in cls.xdb_data]
    check_excel.loc[idx,'因子类型'] = str(factor_type)

check_excel = check_excel[~check_excel['因子类型'].isna()]
count_series = check_excel['因子类型'].value_counts().sort_index()
total_count = len(check_excel)
ratio_series = count_series / total_count
summary_df = pd.DataFrame({
    '因子个数':count_series,
    '因子占比':ratio_series
})
summary_df = summary_df.sort_values('因子个数', ascending=False)
summary_df.to_excel('/dfs/user/023859/neptune/因子个数统计.xlsx')
