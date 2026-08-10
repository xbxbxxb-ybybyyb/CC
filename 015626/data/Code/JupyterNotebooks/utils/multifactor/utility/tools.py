import zipfile
import os
from xquant.xqutils.helper import link

def send_link(message):
    lm = link.LinkMessage()
    lm.sendMessage(str(message))
    del(lm)

import requests
import json

def send_file(users, file):
    corpid = 'wwd53282142c96185d'
    corpsecret = 'Pk0ewu3nuo6JhEaBj_EkuPS_A0-ku8KHi6fsSbsCipk'
    agentid = 1000033
    token_url = 'http://168.9.11.148:1080/cgi-bin/gettoken?corpid={0}&corpsecret={1}'.format(corpid, corpsecret)
    send_url = 'http://168.9.11.148:1080/cgi-bin/message/send?access_token={}'

    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    img_url = "http://168.9.11.148:1080/cgi-bin/media/upload?access_token={}&type=file".format(access_token)
    files = {'file': open(file, 'rb')}
    media_id = requests.post(img_url, files=files).json()['media_id']

    if isinstance(users, list):
        users = '|'.join(users)

    media = {"touser": users,
             "msgtype": "file",
             "agentid": 1000033,
             "file": {"media_id": media_id}}
    json_media = json.dumps(media, ensure_ascii=False).encode('utf-8')
    requests.post(post_url, json_media)
    
def extract_zip(zip_path, extract_to=None):
    """
    解压 ZIP 文件

    参数:
    zip_path (str): ZIP 文件的路径
    extract_to (str): 解压路径，默认是压缩文件所在目录
    """
    if extract_to is None:
        extract_to = os.path.dirname(zip_path)

    os.makedirs(extract_to, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        print(f"文件已解压到: {extract_to}")

def extract_7z(seven_z_file, extract_to=None):
    import subprocess
    subprocess.check_call(["pip", "install", 'py7zr'])
    import py7zr
    if extract_to is None:
        extract_to = os.path.dirname(seven_z_file)

    os.makedirs(extract_to, exist_ok=True)

    archive = py7zr.SevenZipFile(seven_z_file, mode='r')
    archive.extractall(path=extract_to)
    print(f"文件已解压到: {extract_to}")