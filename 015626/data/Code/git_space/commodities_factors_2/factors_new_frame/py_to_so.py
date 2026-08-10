import os
import shutil
import subprocess
import tempfile
from Cython.Build import cythonize
from setuptools import setup
from distutils.core import Extension
import sys

# 用户需要填写的路径
py_folder  = "/data/user/015626/data/Code/git_space/commodities_factors_2/factors_new_frame/"  # 替换为你的 .py 文件夹路径
output_folder = "/data/user/015626/data/Code/git_space/commodities_factors_2/factors_so/"  # 替换为你想生成 .so 的文件夹路径

# 创建输出目录
os.makedirs(output_folder, exist_ok=True)

# 安装依赖：确保系统中安装了 Cython 和 setuptools
try:
    import Cython
    from setuptools import setup
except ImportError:
    print("正在安装 Cython 和 setuptools，请稍等...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Cython", "setuptools"])

# 遍历py文件并编译
for py_file in os.listdir(py_folder):
    print(py_file)
    if py_file.endswith(".py") and not py_file.startswith("__") and 'py_to_so' not in py_file:
        py_path = os.path.join(py_folder, py_file)
        base_name = os.path.splitext(py_file)[0]

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_cy_file = os.path.join(tmpdir, f"{base_name}.pyx")
            setup_py = os.path.join(tmpdir, "setup.py")

            # 将 .py 文件复制为 .pyx
            with open(temp_cy_file, 'w') as f:
                with open(py_path, 'r') as src:
                    f.write(src.read())

            # 创建 setup.py
            with open(setup_py, 'w') as f:
                f.write(f'''from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

ext = Extension("{base_name}", ["{base_name}.pyx"], language="c")
setup(
    name="{base_name}",
    ext_modules=cythonize([ext], language_level = 3),
    script_args=["build_ext", "--inplace"]
)
''')

            # 切换到临时目录
            os.chdir(tmpdir)

            # 打印 setup.py 内容用于调试
            print(f"\n正在编译 {py_file}...")

            # 使用 try-except 捕获错误
            try:
                subprocess.check_call([sys.executable, setup_py])
            except subprocess.CalledProcessError as e:
                print(f"❌ 编译失败: {py_file}，错误代码 {e.returncode}")
                print("请检查 setup.py 是否正常运行")
                continue

            # 查找生成的 so 或 pyd 文件
            built_files = [f for f in os.listdir(tmpdir) if f.endswith(".so") or f.endswith(".pyd")]
            if built_files:
                built_file = built_files[0]
                so_path = os.path.join(tmpdir, built_file)
                dest_so = os.path.join(output_folder, f"{base_name}.so")
                shutil.copy(so_path, dest_so)
                print(f"✅ 编译成功: {py_file} -> {dest_so}")
            else:
                print(f"❌ 编译失败: {py_file} 没有生成 .so 文件")

            # 删除临时生成的 .pyx 和 .c 文件
            if os.path.exists(temp_cy_file):
                os.remove(temp_cy_file)
            temp_c_file = os.path.join(tmpdir, f"{base_name}.c")
            if os.path.exists(temp_c_file):
                os.remove(temp_c_file)