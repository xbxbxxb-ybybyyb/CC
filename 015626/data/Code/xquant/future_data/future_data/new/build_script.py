import subprocess
import os

# 目标项目的路径
project_path = '/data/user/015626/data/Code/git_space/strategy_back_test/build/temp20240805/'

def build_cython_extension():
    # 切换到目标项目路径
    os.chdir(project_path)
    # 先安装python3 -m pip install --upgrade pip setuptools wheel
# 然后运行python3 setup.py build_ext --inplace 要将py文件改为pyx
    # 执行编译命令
    command = ["python3", "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"]
    result2 = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    command = ["python3", "setup.py", "build_ext", "--inplace"]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print("Standard Output:")
    print(result.stdout)
    
    print("Standard Error:")
    print(result.stderr)
    
    if result.returncode == 0:
        print("Build successful")
    else:
        print("Build failed")

if __name__ == "__main__":
    build_cython_extension()
