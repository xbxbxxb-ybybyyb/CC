import paramiko
import warnings, os
import requests, urllib, ssl
import json
import re
import time
import pandas as pd
from retry import retry
from retry.api import retry_call
import sched, time
import subprocess
import ftplib
import io
import multifactor.utility.common as ut

warnings.simplefilter('ignore')

host = '160.10.28.120'
user = 'appadmin'
port = 3344
pem = '/data/user/015626/projects/vars/appadmin.pem'
file_api_url = 'https://harlighet.synology.me:8888'
fast_api_url = 'https://harlighet.synology.me:40001'
bark_messenger = 'https://harlighet.synology.me:40000/nGoXxJeXGBw7wPJtzAdksn/'
ftp_address = '168.8.2.68'
ftp_username = 'xquant'
ftp_password = 'Xquant-32'
ftp_home = '/XQuant/015626'
curl_path = r'D:\Roaming\curl\curl'
magneto_path = '/data/user/015626/projects/SimHF/genesis/Data/Magneto'
project_base_path = '/data/user/015626/projects/SimHF/genesis'
internet_stage_path = r'D:\Research\stage'
local_stage_path = '/data/user/015626/projects/stage'
ftp_stage_path = ftp_home + '/stage'


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


@static_vars(ftp_handle=None)
def get_ftp_handle(address=None, username=None, password=None, encoding='gbk'):
    if get_ftp_handle.ftp_handle is None:
        address = ftp_address if address is None else address
        username = ftp_username if username is None else username
        password = ftp_password if password is None else password
        ftp = ftplib.FTP(address)
        ftp.encoding = encoding
        ftp.login(username, password)
        get_ftp_handle.ftp_handle = ftp
    return get_ftp_handle.ftp_handle


def release_ftp_handle():
    if isinstance(get_ftp_handle.ftp_handle, ftplib.FTP):
        get_ftp_handle.ftp_handle.close()
        get_ftp_handle.ftp_handle = None
    else:
        raise AssertionError


def list_ftp_dir(ftp_handle=None, **kwargs):
    if not isinstance(ftp_handle, ftplib.FTP):
        ftp_handle = get_ftp_handle(**kwargs)
    ftp_handle.retrlines('LIST')


def get_ftp_file(file_name, output_path, file_path=None, output_name=None, delete_upon_finish=False, ftp_handle=None, stealth_mode=True, **kwargs):
    try:
        if file_path is None:
            file_path = ftp_stage_path
        if output_name is None:
            output_name = file_name
        print(f'Getting {file_name} at {file_path}')
        if not isinstance(ftp_handle, ftplib.FTP):
            ftp_handle = get_ftp_handle(**kwargs)
        ftp_handle.cwd(file_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        if stealth_mode:
            file_name = ut.get_encrypted_file_name(file_name)
        with open(os.path.join(output_path, output_name), 'wb') as fout:
            if stealth_mode:
                with io.BytesIO() as efout:
                    ftp_handle.retrbinary(f'RETR {file_name}', efout.write)
                    efout.seek(0)
                    decrypted_msg = ut.decrypter(efout.read(), ut.get_default_secret(), dtype=bytes)
                    fout.write(decrypted_msg)
            else:
                ftp_handle.retrbinary(f'RETR {file_name}', fout.write)
        if delete_upon_finish:
            ftp_handle.delete(file_name)
    except Exception as _exp:
        release_ftp_handle()
        print(_exp)
        raise _exp


def get_ftp_file_with_retry(tries=500, delay=10, jitter=1, **kwargs):
    def get_ftp_file_helper():
        return retry_call(get_ftp_file, fkwargs=kwargs, tries=tries, delay=delay, jitter=jitter)
    get_ftp_file_helper()


def put_ftp_file(file_name, file_path, output_path=None, output_name=None, ftp_handle=None, stealth_mode=True, **kwargs):
    try:
        if output_path is None:
            output_path = ftp_stage_path
        if output_name is None:
            output_name = file_name
        print(f'Putting {file_name} at {file_path}')
        if not isinstance(ftp_handle, ftplib.FTP):
            ftp_handle = get_ftp_handle(**kwargs)
        ftp_handle.cwd(output_path)
        with open(os.path.join(file_path, file_name), 'rb') as fin:
            if stealth_mode:
                output_name = ut.get_encrypted_file_name(output_name)
                encrypted_msg = ut.encrypter(fin.read(), ut.get_default_secret())
                with io.BytesIO(encrypted_msg) as efin:
                    ftp_handle.storbinary(f'STOR {output_name}', efin)
            else:
                ftp_handle.storbinary(f'STOR {output_name}', fin)
    except Exception as _exp:
        release_ftp_handle()
        print(_exp)
        raise _exp


def put_ftp_file_with_retry(tries=10, delay=5, jitter=1, **kwargs):
    def put_ftp_file_helper():
        return retry_call(put_ftp_file, fkwargs=kwargs, tries=tries, delay=delay, jitter=jitter)
    put_ftp_file_helper()


def scheduler(func, target_trigger_time, delay=0):
    # init func at given time with delay as in milliseconds
    assert isinstance(target_trigger_time, pd.Timedelta)
    assert callable(func)
    target_trigger_time = (pd.Timestamp(pd.Timestamp.now().date()) + target_trigger_time).to_pydatetime().timestamp() + delay / 1000
    s = sched.scheduler(time.time, time.sleep)
    s.enterabs(target_trigger_time, 0, func)
    s.run(blocking=True)


def wait_ftp_file(target_trigger_time, tries=50, delay=5, jitter=0, **kwargs):
    def wait_ftp_file_helper():
        return retry_call(get_ftp_file, fkwargs=kwargs, tries=tries, delay=delay, jitter=jitter)
    scheduler(wait_ftp_file_helper, target_trigger_time)


def upload_file(file_path, file_name, curl_location=None, url_location=None, destination_name=None, timeout=10, pipe_encoding='gbk'):
    if curl_location is None:
        curl_location = curl_path
    if url_location is None:
        url_location = file_api_url
    if destination_name is None:
        destination_name = file_name
    print(f'Uploading {file_name} at {file_path}')
    try:
        resp = subprocess.run([curl_location, '-k', '-S', '-s', '--upload-file',
                               os.path.join(file_path, file_name),
                               f'{url_location}/{destination_name}'],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               check=False, timeout=timeout)
    except subprocess.TimeoutExpired as _exp:
        print(_exp)
        raise TimeoutError
    finally:
        resp_out = resp.stdout.decode(pipe_encoding)
        resp_err = resp.stderr.decode(pipe_encoding)
        if resp_err:
            print(resp_err)
            raise RuntimeError(resp_err)
        else:
            print('https://' + resp_out.split('https://')[1].strip())
    return resp_out


def upload_file_with_retry(tries=10, delay=1, jitter=1, **kwargs):
    def upload_file_helper():
        return retry_call(upload_file, fkwargs=kwargs, tries=tries, delay=delay, jitter=jitter)
    upload_file_helper()


def send_bark_msg(msg, messenger=None, timeout=10, ignore_ssl=False):
    print(f'Sending bark message: {msg}')
    if messenger is None:
        messenger = bark_messenger
    if ignore_ssl:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        ctx = None
    urllib.request.urlopen(messenger + urllib.parse.quote_plus(msg), context=ctx, timeout=timeout)


def send_bark_msg_with_retry(tries=10, delay=1, jitter=1, **kwargs):
    def send_bark_msg_helper():
        return retry_call(send_bark_msg, fkwargs=kwargs, tries=tries, delay=delay, jitter=jitter)
    send_bark_msg_helper()


def upload_signal_by_ftp(signal_name, target_trigger_time, ref_date=None, ignore_ssl=True):
    print(f'Sending {signal_name}')
    if ref_date is None:
        ref_date = pd.Timestamp.now().date().strftime('%Y%m%d')
    else:
        ref_date = str(ref_date)
    target_name = f'{signal_name}_{ref_date}.sig'
    wait_ftp_file(target_trigger_time, file_name=target_name, output_path=internet_stage_path, delete_upon_finish=True)
    send_bark_msg_with_retry(msg=f'{signal_name} retrieved from FTP', ignore_ssl=ignore_ssl)
    upload_file_with_retry(file_path=internet_stage_path, file_name=target_name)



def download_file(url_name, curl_location=None, url_location=None, output_path=None, output_name=None, timeout=10, pipe_encoding='gbk'):
    assert '/' == url_name[0]
    file_name = os.path.basename(url_name)
    if curl_location is None:
        curl_location = curl_path
    if url_location is None:
        url_location = file_api_url
    if output_path is None:
        output_path = internet_stage_path
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if output_name is None:
        output_name = file_name
    print(f'Downloading {url_name} at {url_location}')
    try:
        resp = subprocess.run([curl_location, '-k', '-S', '-s',
                               url_location + url_name,
                               '--create-dirs', '-o',
                               os.path.join(output_path, output_name)],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               check=False, timeout=timeout)
    except subprocess.TimeoutExpired as _exp:
        print(_exp)
        raise TimeoutError
    finally:
        resp_out = resp.stdout.decode(pipe_encoding)
        resp_err = resp.stderr.decode(pipe_encoding)
        if resp_err:
            print(resp_err)
            raise RuntimeError(resp_err)
        else:
            print(resp_out)
    return resp_out


def download_file_with_retry(tries=10, delay=1, jitter=1, **kwargs):
    def download_file_helper():
        return retry_call(download_file, fkwargs=kwargs, tries=tries, delay=delay, jitter=jitter)
    download_file_helper()


def find_url_by_fastapi(pattern, url_location=None, strip_url_base=True):
    if url_location is None:
        url_location = fast_api_url
    url_names = requests.get(f'{url_location}/re/{pattern}', verify=False).json()
    if isinstance(url_names, list):
        url_names = [item for item in url_names if '.metadata' not in item]
    else:
        url_names = [url_names]
    if strip_url_base:
        url_names = [item.split('/get')[1] for item in url_names]
    return url_names


def send_file(file_path, file_name, destination_name=None):
    pkey = paramiko.RSAKey.from_private_key_file(pem, password=secret)
    # establish sftp for file transfer
    scp = paramiko.Transport((host, port))
    scp.connect(username=user, pkey=pkey)
    sftp = paramiko.SFTPClient.from_transport(scp)
    # establish ssh for remote commands
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=user, pkey=pkey, port=port)
    # the real deal
    # purse remote stage
    stdin, stdout, stderr = ssh.exec_command('cmd /K cd /d D:\Research & rmdir stage /S /Q & mkdir stage & exit')
    time.sleep(1)
    # upload target file
    sftp.put(os.path.join(file_path, file_name), f'Research\stage\{file_name}')
    time.sleep(1)
    # sync status
    if destination_name is None:
        destination_name = file_name
    stdin, stdout, stderr = ssh.exec_command(f'{curl_path} -k --upload-file D:\Research\stage\{file_name} {file_api_url}/{destination_name}')
    response = stdout.read().decode('gbk')
    print('https://' + response.split('https://')[1].strip())
    # close connections
    sftp.close()
    ssh.close()



def get_file(file_name):
    pkey = paramiko.RSAKey.from_private_key_file(pem, password=secret)
    # establish sftp for file transfer
    scp = paramiko.Transport((host, port))
    scp.connect(username=user, pkey=pkey)
    sftp = paramiko.SFTPClient.from_transport(scp)
    # establish ssh for remote commands
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=user, pkey=pkey, port=port)
    # the real deal
    if file_name[0] == '/':
        tag, file_name = os.path.dirname(file_name), os.path.basename(file_name)
        stdin, stdout, stderr = ssh.exec_command(f'cmd /K cd /d D:\Research\stage & {curl_path} -k {file_api_url}{tag}/{file_name} -O {file_name}')
        time.sleep(1)
        sftp.get(f'Research\stage\{file_name}', f'{file_name}')
        time.sleep(1)
        try:
            if not os.path.exists(file_name):
                raise FileNotFoundError
            with open(file_name, 'r') as fin:
                try:
                    line = fin.readline()
                except UnicodeDecodeError:
                    line = ''
                if 'Not Found' in line:
                    raise NameError
                else:
                    print(f'{file_name} retrieved')
        except FileNotFoundError:
            print('Remote URL Unreachable')
        except NameError:
            os.remove(file_name)
            print('Remote URL Illegal')
    else:
        try:
            sftp.get(f'Research\stage\{file_name}', f'{file_name}')
            time.sleep(1)
            print(f'{file_name} retrieved')
        except FileNotFoundError:
            print(f'{file_name} Not Found on Stage')
    # close connections
    sftp.close()
    ssh.close()

