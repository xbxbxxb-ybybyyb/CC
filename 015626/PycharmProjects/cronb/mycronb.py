import os
import sys
import pandas as pd
from multifactor.data.semaphore import *
import multifactor.utility.dt as tdt
import datetime as dt
from subprocess import PIPE

if __name__ == '__main__':

    zk = ZooKeeper(log_name='cronbtd')

    x = zk.fire('cv1', [], '/data/user/015626/PycharmProjects/wyc_docker/cronb/cv1.py', process_type='multiprocess', stdout = PIPE, stderr = PIPE)
    y = zk.fire('cv2', [], '/data/user/015626/PycharmProjects/wyc_docker/cronb/cv2.py', process_type='multiprocess', stdout = PIPE, stderr = PIPE)

    print(x.stdout.decode('utf-8'))
    print(x.stderr.decode('utf-8'))
