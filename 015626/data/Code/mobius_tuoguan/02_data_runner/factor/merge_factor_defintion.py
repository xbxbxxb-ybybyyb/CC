import json
import os

def merge_json_files():
    # 定义输入目录
    input_dir = "/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition_v7.0.1/"
    
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        print(f"输入目录 '{input_dir}' 不存在。")
        return
    
    # 获取目录中的所有JSON文件
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    
    # 初始化合并后的因子列表
    merged_factors = []
    
    # 遍历每个JSON文件
    for file in json_files:
        file_path = os.path.join(input_dir, file)
        with open(file_path, 'r') as f:
            data = json.load(f)
            merged_factors.extend(data)
    
    
    # 定义输出文件路径
    output_file = "/dfs/user/666466/01_params/factor_definition_set_V7.0.1.json"
    
    # 将合并后的数据写入新的JSON文件
    with open(output_file, 'w') as f:
        json.dump(merged_factors, f, indent=4)
    
    print(f"成功合并 {len(json_files)} 个JSON文件，结果保存在 '{output_file}'。")

if __name__ == "__main__":
    merge_json_files()
