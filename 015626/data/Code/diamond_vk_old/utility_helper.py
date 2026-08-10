import warnings, os
import json
import re
import pandas as pd
import numpy as np
from retry import retry
from retry.api import retry_call
import sched, time
import subprocess
import ftplib
import io
import hashlib
from Crypto.Cipher import AES
from Crypto import Random

warnings.simplefilter('ignore')

ftp_address = '168.8.2.68'
ftp_username = 'xquant'
ftp_password = 'Xquant-32'
ftp_home = '/XQuant/012245'
ftp_stage_path = ftp_home + '/stage'

def get_default_secret(aes_mode = AES.MODE_CFB):
    dt = pd.Timestamp.now().date().strftime('%Y%m%d')
    return f'{dt}-MAAL-{aes_mode}'

def encrypter(msg, secret, aes_mode=AES.MODE_CFB, initial_vec=None):
    assert isinstance(msg, str) or isinstance(msg, bytes)
    assert isinstance(secret, str)
    # Prepare initial vector
    if initial_vec is None:
        initial_vec = Random.new().read(AES.block_size)
    # Encrypt message
    hasher = hashlib.sha256()
    hasher.update(secret.encode('utf-8'))
    encryption_cipher = AES.new(hasher.digest(), aes_mode, initial_vec)
    if isinstance(msg, str):
        return initial_vec + encryption_cipher.encrypt(msg.encode('utf-8'))
    elif isinstance(msg, bytes):
        return initial_vec + encryption_cipher.encrypt(msg)
    else:
        raise AssertionError


def decrypter(msg, secret, aes_mode=AES.MODE_CFB, dtype=str):
    assert isinstance(msg, str) or isinstance(msg, bytes)
    assert isinstance(secret, str)
    # Decrypt message
    hasher = hashlib.sha256()
    hasher.update(secret.encode('utf-8'))
    decryption_cipher = AES.new(hasher.digest(), aes_mode, msg[:AES.block_size])
    if dtype == str:
        return decryption_cipher.decrypt(msg[AES.block_size:]).decode('utf-8')
    elif dtype == bytes:
        return decryption_cipher.decrypt(msg[AES.block_size:])
    else:
        raise AssertionError


def get_encrypted_file_name(file_name, secret=None, aes_mode=AES.MODE_CFB):
    if secret is None:
        secret = get_default_secret(aes_mode)
    initial_vec = bytes((secret * AES.block_size).encode('utf-8'))[:AES.block_size]
    encrypted_file_name = encrypter(os.path.basename(file_name), secret,
                                   initial_vec=initial_vec).hex()
    return encrypted_file_name + '.bin'


def get_decrypted_file_name(file_name, secret=None, aes_mode=AES.MODE_CFB):
    if secret is None:
        secret = get_default_secret(aes_mode)
    assert file_name[-4:] == '.bin'
    return decrypter(bytes.fromhex(os.path.basename(file_name[:-4])), secret, dtype=str)


def file_encrypter(file_name, output_path=None, secret=None, aes_mode=AES.MODE_CFB, encrypt_file_name=False):
    if secret is None:
        secret = get_default_secret(aes_mode)
    if output_path is None:
        if encrypt_file_name:
            encrypted_file_name = get_encrypted_file_name(file_name, secret, aes_mode)
            output_path = os.path.join(os.path.dirname(file_name), encrypted_file_name)
        else:
            output_path = file_name + '.bin'
    with open(file_name, 'rb') as fin:
        msg = fin.read()
    encrypted_msg = encrypter(msg, secret)
    with open(output_path, 'wb') as fout:
        fout.write(encrypted_msg)


def file_decrypter(file_name, output_path=None, secret=None, aes_mode=AES.MODE_CFB, decrypt_file_name=False):
    if secret is None:
        secret = get_default_secret(aes_mode)
    if output_path is None:
        assert file_name[-4:] == '.bin'
        if decrypt_file_name:
            decrypted_file_name = get_decrypted_file_name(file_name, secret, aes_mode)
            output_path = os.path.join(os.path.dirname(file_name), decrypted_file_name)
        else:
            output_path = file_name[:-4]
    with open(file_name, 'rb') as fin:
        msg = fin.read()
    decrypted_msg = decrypter(msg, secret, dtype=bytes)
    with open(output_path, 'wb') as fout:
        fout.write(decrypted_msg)



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
            file_name = get_encrypted_file_name(file_name)
        with open(os.path.join(output_path, output_name), 'wb') as fout:
            if stealth_mode:
                with io.BytesIO() as efout:
                    ftp_handle.retrbinary(f'RETR {file_name}', efout.write)
                    efout.seek(0)
                    decrypted_msg = decrypter(efout.read(), get_default_secret(), dtype=bytes)
                    fout.write(decrypted_msg)
            else:
                ftp_handle.retrbinary(f'RETR {file_name}', fout.write)
        if delete_upon_finish:
            ftp_handle.delete(file_name)
    except Exception as _exp:
        release_ftp_handle()
        print(_exp)
        raise _exp


def get_ftp_file_with_retry(tries=10, delay=5, jitter=1, **kwargs):
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
                output_name = get_encrypted_file_name(output_name)
                encrypted_msg = encrypter(fin.read(), get_default_secret())
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


def slot_even_filler(slots, total_quota):
    # given slot quotas in ascending list and total quota,
    # try to fill each and every slot in a most possibly even form
    assert isinstance(slots, list) and slots == sorted(slots)
    if total_quota >= sum(slots):
        return slots
    n_slots = len(slots)
    even_quota = total_quota / n_slots
    if even_quota > slots[0]:
        left_overs = slot_even_filler([item - slots[0] for item in slots[1:]], total_quota - slots[0] * n_slots)
        return [slots[0] + item for item in [0] + left_overs]
    else:
        return [even_quota] * n_slots


def vec_normalize(vec, norm=1):
    _vec = np.fabs(np.array(vec)).reshape(-1)
    _sum = _vec[~np.isnan(_vec)].sum()
    if _sum != 1 and _sum != 0:
        _vec = _vec * norm / _sum
        _vec = [i * abs(j) / j if j !=0 else 0 for i, j in zip(_vec, vec)]
        if type(vec) == np.ndarray:
            return np.array(_vec)
        elif type(vec) == list:
            return _vec
        elif type(vec) == pd.Series:
            _vec = pd.Series(_vec, index=vec.index)
            _vec.name = vec.name
            return _vec
        else:
            raise AssertionError
    else:
        return vec


def read_json(path):
    with open(path, 'r') as fin:
        try:
            data = json.load(fin)
        except json.JSONDecodeError:
            data = None
    return data


def dump_json(path, value):
    with open(path, 'w') as fout:
        json.dump(value, fout)

