import zipfile
import os
from xquant.xqutils.helper import link

def send_link(message):
    lm = link.LinkMessage()
    lm.sendMessage(str(message))
    del(lm)
    
def extract_zip(zip_path, extract_to=None):
    """
    解压 ZIP 文件

    参数:
    zip_path (str): ZIP 文件的路径
    extract_to (str): 解压路径，默认是当前工作目录
    """
    if extract_to is None:
        extract_to = os.getcwd()

    os.makedirs(extract_to, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        print(f"文件已解压到: {extract_to}")

def extract_7z(seven_z_file, extract_to=None):
    import subprocess
    subprocess.check_call(["pip", "install", 'py7zr'])
    import py7zr
    if extract_to is None:
        extract_to = os.getcwd()

    os.makedirs(extract_to, exist_ok=True)

    archive = py7zr.SevenZipFile(seven_z_file, mode='r')
    archive.extractall(path=extract_to)
    print(f"文件已解压到: {extract_to}")