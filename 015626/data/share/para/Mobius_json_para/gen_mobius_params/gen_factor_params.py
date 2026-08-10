import datetime
import json
import os
import sys

# 获取当前日期
current_date = '20250421'

# 计算路径列表
compute_paths = ['0', '50', '55']

# 父目录路径（根据交易日期生成）
parent_dir = f"/data/user/666466/01_params/{current_date}"

# 遍历计算路径列表，生成每个路径对应的文件
for compute_path in compute_paths:
    # 构建完整路径（包含 offset 文件夹）
    offset_folder = f"offset_{compute_path}"
    full_path = os.path.join(parent_dir, offset_folder,'factor')

    # 确保目标目录存在，如果不存在则创建
    os.makedirs(full_path, exist_ok=True)

    # 生成 config.json 文件
    config = {
        "交易日期": current_date,
        "历史数据目录": "/data/user/666466/06_prod_data/02_FactorData",
        "日频数据目录": "/data/user/666466/06_prod_data/00_MarketData",
        "因子配置文件": "/data/user/666466/06_prod_data/factor_definition_set_V7.0.1.json",
        "是否记录因子值": "True",
        "静态信息查询失败时是否使用本地文件": "True",
        "是否校验历史数据": "False",
        "开始处理分钟聚合数据时间": "09:30:00",
        "计算路径": compute_path
    }

    # 生成 config.json 文件路径
    config_filename = f"params.json"
    config_file_path = os.path.join(full_path, config_filename)

    with open(config_file_path, 'w') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)