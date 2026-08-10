import os
import subprocess
from pathlib import Path
import shutil

def decompile_all_class_files(src_dir, dst_dir, cfr_path):
    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.class'):
                class_file = Path(root) / file
                # 保持目录结构
                rel_path = class_file.relative_to(src_dir)
                # print(class_file)
                # print(rel_path)
                # print(rel_path.parent)
                output_dir = dst_dir / rel_path.parent
                rel_path = file
                # output_dir.mkdir(parents=True, exist_ok=True)
                # print(output_dir)
                
                cmd = [
                    'java',
                    '-jar', str(cfr_path),
                    str(class_file),
                    '--outputpath', str(dst_dir),
                    '--silent', 'true'
                ]
                try:
                    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    print(f"Decompiled: {class_file} -> {output_dir}")
                    # exit()
                except subprocess.CalledProcessError as e:
                    print(f"Failed to decompile {class_file}: {e.stderr}")
            else:
                class_file = Path(root) / file
                # 保持目录结构
                rel_path = class_file.relative_to(src_dir)
                
                output_dir = dst_dir / rel_path.parent
                output_dir.mkdir(parents=True, exist_ok=True)
                # print(file)
                # print(class_file)
                # print(rel_path)
                # print(output_dir)
                shutil.copyfile(class_file, os.path.join(output_dir, file))

                

# 示例用法
decompile_all_class_files(f'/data/user/015626/data/Code/mobius_tuoguan_decompress/factor/strategy-MobiusFactor-1.0-20250416-065343/com', f'/data/user/015626/data/Code/mj/strategy-MobiusFactor-1.0-20250416-065343', f'/data/user/015626/data/Code/mj/cfr-0.152.jar')