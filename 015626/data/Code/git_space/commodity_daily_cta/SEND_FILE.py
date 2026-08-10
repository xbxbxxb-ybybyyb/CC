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