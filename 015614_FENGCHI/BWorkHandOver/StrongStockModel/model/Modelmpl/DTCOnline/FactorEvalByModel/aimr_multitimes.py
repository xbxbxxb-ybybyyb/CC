# coding=utf-8
import pandas as pd
import uuid

import json
import os
import atexit
import signal
import traceback

import pymysql

import re
import requests
import datetime
import sys
import time
import warnings
from xquant.utils import statisticLog
import string
import random
import retrying
from xquant.compute.aimr.dbutils import get_connection_pool

warnings.filterwarnings("ignore")

global id_lis
id_lis = []
global tableName
tableName = 'application'
global databaseIp
databaseIp = []
global databaseName
databaseName = []
global pycharm_group
global userName
global mysql_pool
mysql_pool = None
userName = []
global databasePassword
databasePassword = []
global databasePort
databasePort = []


class tf():
    # 根据实际传入
    @statisticLog("tensorflow")
    def __init__(self):
        pass

    @statisticLog("tensorflow")
    def get(self):
        return


@statisticLog("tensorflow", "aimr")
def term_sig_handler(signum, frame):
    # print('catched singal: %d' % signum)
    if id_lis:
        global mysql_pool
        conn = mysql_pool.connection()
        cursor = conn.cursor()
        sql = "update application set status = 999 where status in (0,1,3,6) and id in %s" % str(id_lis)
        sql = sql.replace('[', '(')
        sql = sql.replace(']', ')')
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
        try:
            mysql_pool.close()
        except:
            pass
    sys.exit()


def set_connection_pool():
    global mysql_pool
    if not mysql_pool:
        mysql_pool = get_connection_pool(databaseIp[0], userName[0], databasePassword[0], databaseName[0], int(databasePort[0]))


@retrying.retry(stop_max_attempt_number=5, wait_fixed=2000)
def get_running_tasks_num(xquant_id):
    try:
        global mysql_pool
        conn = mysql_pool.connection()
        cursor = conn.cursor()
        cursor.execute(
            "select count(*) from application where status in (0,1,3,6) and xquant_id='%s' and fjob_id is not null" % xquant_id)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        count = data[0][0]
        return count
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        print("warning: get_running_tasks_num数据库连接失效，已重新创建连接。错误原因{}。".format(e))
        raise Exception(e)


@retrying.retry(stop_max_attempt_number=5, wait_fixed=2000)
def get_running_tasks_status(xquant_id):
    try:
        global mysql_pool
        conn = mysql_pool.connection()
        cursor = conn.cursor()
        cursor.execute(
            "select * from application where status in (0,1,3,6) and xquant_id='%s' and fjob_id is not null" % xquant_id)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        print("warning: get_running_tasks_status数据库连接失效，已重新创建连接。错误原因{}。".format(e))
        raise Exception(e)


task_status_dict = {
    0: "准备中",
    1: "运行中",
    2: "已完成",
    3: "资源不足等待",
    4: "用户或系统终止",
    5: "运行出错",
    6: "下发AI平台",
    7: "调度失败",
    999: "AIMR待杀任务",
    1000: "AIMR在杀任务",
}


def get_running_tasks_status_detail(xquant_id, pycharm_group=None):
    try:
        global mysql_pool
        conn = mysql_pool.connection()
        cursor = conn.cursor()
        cursor.execute(
            "select * from application where status in (0,1,3,6) and xquant_id='%s' and fjob_id is not null" % xquant_id)
        data = cursor.fetchall()
        cursor.close()

        df = pd.read_sql(
            "select job_id, resource_config, start_time, task_config, status, diagnostics  from application where status in (0,1,3,5,6,7) and xquant_id='%s' and fjob_id is not null" % xquant_id,
            conn)
        conn.close()
        # print(data)
        # df = pd.DataFrame(data, columns = ["job_id", "task_config", "status", "diagnostics"])
        df["parallel_params"] = df["task_config"].apply(lambda x: json.loads(x).get("parallel", 'no parallel key') if x else 'no task_config')
        df["pycharm_group"] = df["resource_config"].apply(lambda x: json.loads(x).get("pycharm_group", 'no pycharm_group key') if x else 'no resource_config')
        df["status"] = df["status"].apply(lambda x: task_status_dict[x])
        df = df.drop(columns=["resource_config", "task_config"])

        df = df.reindex(columns=["pycharm_group", "start_time", "parallel_params", "status", "diagnostics", "job_id"])
        df = df.rename(columns={"diagnostics": "status_detail"})
        if pycharm_group:
            df = df[df["pycharm_group"] == pycharm_group]
        df = df.sort_values(by=["start_time"])
        return data, df
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        print("warning: get_running_tasks_status_detail数据库连接失效，已重新创建连接。错误原因{}。".format(e))
        raise Exception(e)


@retrying.retry(stop_max_attempt_number=5, wait_fixed=2000)
def insert_new_task(tableName, user_id, xquant_id, fjob_id, resource_config, task_config, no, app_id, port_url,
                    password, running_timeout, entry_file, code_path, ro_path_set, rw_path_set,
                    log_keyprefix, priority):
    try:
        global mysql_pool
        conn = mysql_pool.connection()
        cursor = conn.cursor()
        cursor.execute('SET character_set_connection=utf8;')
        ret = cursor.executemany(
            "insert into {}(user_id, xquant_id,fjob_id,resource_config,task_config,status,app_id,port_url,password,running_timeout,entry_file,code_path,ro_path_set,rw_path_set,log_keyprefix,priority)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(
                tableName), [(user_id, xquant_id, fjob_id, resource_config, task_config, no, app_id, port_url,
                              password, running_timeout, entry_file, code_path, ro_path_set, rw_path_set,
                              log_keyprefix, priority)])
        id_lis.append(cursor.lastrowid)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        print("warning: insert_new_task数据库连接失效，已重新创建连接。错误原因{}。".format(e))
        raise Exception(e)


def runTasksYieldStatus(filename, param):
    def subInnerTasks(filename, param, with_status=True):
        t = tf()
        t.get()

        params = json.loads(param)

        envtype = os.getenv("ENV_VERSION")
        if envtype == 'uat':
            databaseIp.append("168.63.1.130")
            databaseName.append("xquant")
            uploadIp = "168.61.10.212"
            cpuimage = "cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:v3.0"
            gpuimage = "cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:uat_v3.0"
            userName.append("xquant")
            databasePassword.append("QQ_jfdf_2289")
            databasePort.append('3309')
        elif envtype == 'sit':
            databaseIp.append("168.61.13.128")
            databaseName.append("tyjk_server")
            uploadIp = "168.61.10.212"
            cpuimage = "cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:uat_v3.0"
            gpuimage = "cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:uat_v3.0"
            userName.append("admin")
            databasePassword.append("ServicePlat@2019")
            databasePort.append('3306')
        elif envtype == 'prd':
            databaseIp.append("168.11.1.5")
            databaseName.append("xquant_tyjk")
            uploadIp = "168.9.64.62"
            cpuimage = "cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:prd_v3.0"
            gpuimage = "cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:prd_gpu_v3.0"
            userName.append("xquant_tyjk")
            databasePassword.append("X7_mJw12m8UW")
            databasePort.append('3306')
        signal.signal(signal.SIGTERM, term_sig_handler)
        signal.signal(signal.SIGINT, term_sig_handler)
        signal.signal(signal.SIGHUP, term_sig_handler)

        set_connection_pool()  # 初始化全局连接池
        conn = pymysql.connect(databaseIp[0], userName[0], databasePassword[0], databaseName[0], int(databasePort[0]),
                               charset="utf8")
        cursor = conn.cursor()
        cursor.execute('SET CHARACTER SET utf8;')
        # is_sync = params["is_sync"]
        parallel_list = params["parallel_list"]

        # f = open("/tmp/xquant_conf","r")

        filepath = os.getenv('XQUANT_CONF_FILE')
        f = open(filepath, "r")
        file = f.read()
        f.close()
        file = file.split('\n')
        entryFileName = filename
        xquant_id = file[2].split('=')[1]

        log_keyprefix = file[3].split('=')[1]
        log_key = log_keyprefix.split('_')[-1]
        task_type = log_keyprefix.split('_')[0]
        user_id = file[4].split('=')[1]
        if log_key == "son":
            print("error : Subtask cannot call AIMR")
            cursor.close()
            conn.close()
        else:
            cursor.execute(
                "select job_id,rw_path_set,ro_path_set,resource_config from {} where xquant_id='{}' limit 1".format(
                    tableName,
                    xquant_id))
            data = cursor.fetchone()
            cursor.close()
            conn.close()
            fjob_id = data[0]
            rw_path_set = data[1]
            ro_path_set = data[2]
            group = json.loads(data[3])["group"]
            appid = json.loads(data[3])["appid"]
            if 'labels' not in json.loads(data[3]).keys():
                labels = 'common'
            else:
                labels = json.loads(data[3])["labels"]
                gpu = params['gpu']
                if labels in ['common', 'common_gpu']:
                    if int(gpu) > 0:
                        labels = 'common_gpu'
                    else:
                        labels = 'common'
            if 'docker_version' not in params.keys():
                gpu = params['gpu']
                if int(gpu) > 0:
                    image = gpuimage
                else:
                    image = cpuimage
            else:
                image = params['docker_version']
            if 'preferred_gpu' not in params.keys():
                preferred_gpu = 0
            else:
                preferred_gpu = params['preferred_gpu']
            if preferred_gpu not in [0, 1]:
                print('please input right preferred_gpu!')
                sys.exit()
            if task_type == 'xquant':
                log_keyprefix = log_keyprefix
                entryFilePath = file[0].split('=')[1]
                global mysql_pool
                conn = mysql_pool.connection()
                cursor = conn.cursor()
                cursor.execute("select count(1) from {} where xquant_id='{}'".format(tableName, xquant_id))
                count = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                if count > 1:
                    print('"error : Subtask cannot call AIMR"')
                    sys.exit()
                resource_config_ = {"entryFilePath": entryFilePath,
                                    "entryFileName": entryFileName,
                                    "memory": params['memory'],
                                    "cpu": params['cpu'],
                                    "tag": "XQuant Common Task",
                                    "image": image,
                                    "preferred_gpu": preferred_gpu,
                                    "gpu": params['gpu'],
                                    "group": group,
                                    "taskParam": '',
                                    "appid": appid,
                                    "labels": labels
                                    }
                pycharm_group = str(uuid.uuid1())
            else:
                log_keyprefix = log_keyprefix + "_son"
                nowTime = (datetime.datetime.now()).strftime('%Y%m%d%H%M%S')
                pwd = os.popen("pwd").read().split()[0]
                tarName = "%s_%s.tar" % (xquant_id, nowTime)
                os.system("mkdir -p /tmp/%s/xquant && cd %s && cp -r * /tmp/%s/xquant" % (nowTime, pwd, nowTime))
                os.system("cd /tmp/%s && tar -cf %s xquant" % (nowTime, tarName))
                url = "http://%s:38033/api/v1/remotefile" % uploadIp
                files = {'file': open("/tmp/%s/%s" % (nowTime, tarName), 'rb')}
                res = requests.post(url, files=files)
                entryFilePath = "/tmp/%s" % xquant_id
                os.system("cd /tmp && rm -rf %s" % (nowTime))
                pycharm_group = ''.join(random.sample(string.ascii_letters + string.digits, 8))
                pycharm_group = str(xquant_id) + "_" + pycharm_group
                resource_config_ = {"entryFilePath": entryFilePath,
                                    "entryFileName": entryFileName,
                                    "packageFileName": tarName,
                                    "memory": params['memory'],
                                    "cpu": params['cpu'],
                                    "tag": "XQuant RemoteSubmit Common Task",
                                    "gpu": params['gpu'],
                                    "preferred_gpu": preferred_gpu,
                                    "image": image,
                                    "group": group,
                                    "taskParam": '',
                                    "pycharm_group": pycharm_group,
                                    "appid": appid,
                                    "labels": labels
                                    }

            app_id = 1
            port_url = ''
            password = ''
            running_timeout = 31104000000
            entry_file = entryFileName
            code_path = entryFilePath
            # ro_path_set = ''
            # rw_path_set = str([{'sourcePath':sourcePath,'targetPath':entryFilePath}])
            priority = 0

            del params["parallel_list"]
            if len(parallel_list) > 10000:
                print('pallerl_list is too long')
                sys.exit()

            if params.get("subtask_limit_num", None):
                assert isinstance(int(params.get("subtask_limit_num")), int), "subtask_limit_num参数类型错误：必须为int型！"
                restrict_task_number = int(params["subtask_limit_num"])
            else:
                restrict_task_number = 10000
            for lidx, line in enumerate(parallel_list):
                resource_config_["taskParam"] = line
                resource_config = json.dumps(resource_config_)
                params["parallel"] = line
                task_config = json.dumps(params)
                if len(task_config) > 90000 or len(resource_config) > 90000:
                    print("aimr task's param is too long !")
                    sys.exit(0)
                while True:
                    # 最多运行十个任务
                    running_task_count = get_running_tasks_num(xquant_id)
                    if running_task_count >= restrict_task_number:
                        if with_status:
                            if task_type == "xquant":
                                data, df = get_running_tasks_status_detail(xquant_id)
                            else:
                                data, df = get_running_tasks_status_detail(xquant_id, pycharm_group)
                            for i in range(lidx, len(parallel_list)):
                                insertRow = pd.DataFrame({"parallel_params": [i], "status": [task_status_dict[0]]})
                                df = df.append(insertRow)
                            df = df.reindex(
                                columns=["pycharm_group", "start_time", "parallel_params", "status", "diagnostics",
                                         "job_id"])
                            df.reset_index(drop=True, inplace=True)
                            yield df
                        time.sleep(10)
                    else:
                        break
                insert_new_task(tableName, user_id, xquant_id, fjob_id, resource_config, task_config, 0, app_id,
                                port_url,
                                password, running_timeout, entry_file, code_path, ro_path_set, rw_path_set,
                                log_keyprefix, priority)
                time.sleep(0.5)
            # db = pymysql.connect(databaseIp[0], userName[0], databasePassword[0], databaseName[0], int(databasePort[0]))
            while True:

                if with_status:
                    data, df = get_running_tasks_status_detail(xquant_id, pycharm_group)
                    yield df
                else:
                    data = get_running_tasks_status(xquant_id)
                count = len(data)
                tmpcount = 0
                pycharm_count = 0
                is_pycharm = 0
                for i in range(count):
                    taskinfo = data[i]
                    status = taskinfo[7]
                    task_group = json.loads(taskinfo[5])
                    if 'pycharm_group' in task_group.keys():
                        is_pycharm = 1
                        if task_group['pycharm_group'] == pycharm_group:
                            pycharm_count += 1
                            if status in (0, 1, 3, 6):
                                time.sleep(13)
                                break
                            else:
                                tmpcount += 1
                    elif status in (0, 1, 3, 6):
                        time.sleep(13)
                        break
                    else:
                        tmpcount += 1
                if tmpcount == pycharm_count and is_pycharm == 1:
                    break
                elif tmpcount == count and is_pycharm == 0:
                    break
        try:
            mysql_pool.close()
        except:
            pass

    task_iterator = subInnerTasks(filename, param, with_status=True)
    next(task_iterator)
    return task_iterator


@statisticLog("tensorflow", "aimr")
def runTasks(filename, param, with_status=False):
    t = tf()
    t.get()

    params = json.loads(param)

    envtype = os.getenv("ENV_VERSION")
    if envtype == 'uat':
        databaseIp.append("168.63.1.130")
        databaseName.append("xquant")
        uploadIp = "168.61.10.212"
        cpuimage = "cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:v3.0"
        gpuimage = "cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:uat_v3.0"
        userName.append("xquant")
        databasePassword.append("QQ_jfdf_2289")
        databasePort.append('3309')
    elif envtype == 'sit':
        databaseIp.append("168.61.13.128")
        databaseName.append("tyjk_server")
        uploadIp = "168.61.10.212"
        cpuimage = "cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:uat_v3.0"
        gpuimage = "cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:uat_v3.0"
        userName.append("admin")
        databasePassword.append("ServicePlat@2019")
        databasePort.append('3306')
    elif envtype == 'prd':
        databaseIp.append("168.11.1.5")
        databaseName.append("xquant_tyjk")
        uploadIp = "168.9.64.62"
        cpuimage = "cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:prd_v3.0"
        gpuimage = "cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:prd_gpu_v3.0"
        userName.append("xquant_tyjk")
        databasePassword.append("X7_mJw12m8UW")
        databasePort.append('3306')
    signal.signal(signal.SIGTERM, term_sig_handler)
    signal.signal(signal.SIGINT, term_sig_handler)
    signal.signal(signal.SIGHUP, term_sig_handler)

    set_connection_pool()  # 初始化全局连接池
    conn = pymysql.connect(databaseIp[0], userName[0], databasePassword[0], databaseName[0], int(databasePort[0]), charset="utf8")
    cursor = conn.cursor()
    cursor.execute('SET CHARACTER SET utf8;')
    # is_sync = params["is_sync"]
    parallel_list = params["parallel_list"]

    # f = open("/tmp/xquant_conf","r")

    filepath = os.getenv('XQUANT_CONF_FILE')
    f = open(filepath, "r")
    file = f.read()
    f.close()
    file = file.split('\n')
    entryFileName = filename
    xquant_id = file[2].split('=')[1]

    log_keyprefix = file[3].split('=')[1]
    log_key = log_keyprefix.split('_')[-1]
    task_type = log_keyprefix.split('_')[0]
    user_id = file[4].split('=')[1]
    if log_key == "son":
        print("error : Subtask cannot call AIMR")
        cursor.close()
        conn.close()
    else:
        cursor.execute(
            "select job_id,rw_path_set,ro_path_set,resource_config from {} where xquant_id='{}' limit 1".format(tableName,
                                                                                                                xquant_id))
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        fjob_id = data[0]
        rw_path_set = data[1]
        ro_path_set = data[2]
        group = json.loads(data[3])["group"]
        appid = json.loads(data[3])["appid"]
        if 'labels' not in json.loads(data[3]).keys():
            labels = 'common'
        else:
            labels = json.loads(data[3])["labels"]
            gpu = params['gpu']
            if labels in ['common', 'common_gpu']:
                if int(gpu) > 0:
                    labels = 'common_gpu'
                else:
                    labels = 'common'
        if 'docker_version' not in params.keys():
            gpu = params['gpu']
            if int(gpu) > 0:
                image = gpuimage
            else:
                image = cpuimage
        else:
            image = params['docker_version']
        if 'preferred_gpu' not in params.keys():
            preferred_gpu = 0
        else:
            preferred_gpu = params['preferred_gpu']
        if preferred_gpu not in [0, 1]:
            print('please input right preferred_gpu!')
            sys.exit()
        if task_type == 'xquant':
            log_keyprefix = log_keyprefix
            entryFilePath = file[0].split('=')[1]
            global mysql_pool
            conn = mysql_pool.connection()
            cursor = conn.cursor()
            cursor.execute("select count(1) from {} where xquant_id='{}'".format(tableName, xquant_id))
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            # if count > 1:
            #     print('"error : Subtask cannot call AIMR"')
            #     sys.exit()
            resource_config_ = {"entryFilePath": entryFilePath,
                                "entryFileName": entryFileName,
                                "memory": params['memory'],
                                "cpu": params['cpu'],
                                "tag": "XQuant Common Task",
                                "image": image,
                                "preferred_gpu": preferred_gpu,
                                "gpu": params['gpu'],
                                "group": group,
                                "taskParam": '',
                                "appid": appid,
                                "labels": labels
                                }
        else:
            log_keyprefix = log_keyprefix + "_son"
            nowTime = (datetime.datetime.now()).strftime('%Y%m%d%H%M%S')
            pwd = os.popen("pwd").read().split()[0]
            tarName = "%s_%s.tar" % (xquant_id, nowTime)
            os.system("mkdir -p /tmp/%s/xquant && cd %s && cp -r * /tmp/%s/xquant" % (nowTime, pwd, nowTime))
            os.system("cd /tmp/%s && tar -cf %s xquant" % (nowTime, tarName))
            url = "http://%s:38033/api/v1/remotefile" % uploadIp
            files = {'file': open("/tmp/%s/%s" % (nowTime, tarName), 'rb')}
            res = requests.post(url, files=files)
            entryFilePath = "/tmp/%s" % xquant_id
            os.system("cd /tmp && rm -rf %s" % (nowTime))
            pycharm_group = ''.join(random.sample(string.ascii_letters + string.digits, 8))
            pycharm_group = str(xquant_id) + "_" + pycharm_group
            resource_config_ = {"entryFilePath": entryFilePath,
                                "entryFileName": entryFileName,
                                "packageFileName": tarName,
                                "memory": params['memory'],
                                "cpu": params['cpu'],
                                "tag": "XQuant RemoteSubmit Common Task",
                                "gpu": params['gpu'],
                                "preferred_gpu": preferred_gpu,
                                "image": image,
                                "group": group,
                                "taskParam": '',
                                "pycharm_group": pycharm_group,
                                "appid": appid,
                                "labels": labels
                                }

        app_id = 1
        port_url = ''
        password = ''
        running_timeout = 31104000000
        entry_file = entryFileName
        code_path = entryFilePath
        # ro_path_set = ''
        # rw_path_set = str([{'sourcePath':sourcePath,'targetPath':entryFilePath}])
        priority = 0

        del params["parallel_list"]
        if len(parallel_list) > 1000000:
            print('pallerl_list is too long')
            sys.exit()

        if params.get("subtask_limit_num", None):
            assert isinstance(int(params.get("subtask_limit_num")), int), "subtask_limit_num参数类型错误：必须为int型！"
            restrict_task_number = int(params["subtask_limit_num"])
        else:
            restrict_task_number = 10000
        for lidx, line in enumerate(parallel_list):
            resource_config_["taskParam"] = line
            resource_config = json.dumps(resource_config_)
            params["parallel"] = line
            task_config = json.dumps(params)
            if len(task_config) > 90000 or len(resource_config) > 90000:
                print("aimr task's param is too long !")
                sys.exit(0)
            while True:
                # 最多运行十个任务
                running_task_count = get_running_tasks_num(xquant_id)
                if running_task_count >= restrict_task_number:
                    # if with_status:
                    #     data,df = get_running_tasks_status_detail(xquant_id, pycharm_group)
                    #     for i in range(lidx, len(parallel_list)):
                    #         insertRow = pd.DataFrame({"parallel_params":[i], "status":[task_status_dict[0]] })
                    #         df = df.append(insertRow)
                    #     df = df.reindex(columns=["pycharm_group", "start_time", "parallel_params", "status", "diagnostics",
                    #                      "job_id"])
                    #     df.reset_index(drop = True, inplace = True)
                    #     yield df
                    time.sleep(10)
                else:
                    break
            insert_new_task(tableName, user_id, xquant_id, fjob_id, resource_config, task_config, 0, app_id, port_url,
                            password, running_timeout, entry_file, code_path, ro_path_set, rw_path_set,
                            log_keyprefix, priority)
            time.sleep(0.5)
        # db = pymysql.connect(databaseIp[0], userName[0], databasePassword[0], databaseName[0], int(databasePort[0]))
        while True:

            if with_status:
                pass
                # data, df = get_running_tasks_status_detail(xquant_id, pycharm_group)
                # yield df
            else:
                data = get_running_tasks_status(xquant_id)
            count = len(data)
            tmpcount = 0
            pycharm_count = 0
            is_pycharm = 0
            for i in range(count):
                taskinfo = data[i]
                status = taskinfo[7]
                task_group = json.loads(taskinfo[5])
                if 'pycharm_group' in task_group.keys():
                    is_pycharm = 1
                    if task_group['pycharm_group'] == pycharm_group:
                        pycharm_count += 1
                        if status in (0, 1, 3, 6):
                            time.sleep(13)
                            break
                        else:
                            tmpcount += 1
                elif status in (0, 1, 3, 6):
                    time.sleep(13)
                    break
                else:
                    tmpcount += 1
            if tmpcount == pycharm_count and is_pycharm == 1:
                break
            elif tmpcount == count and is_pycharm == 0:
                break
    try:
        mysql_pool.close()
    except:
        pass


@statisticLog("tensorflow", "aimr")
def getParam():
    # f = open("/tmp/xquant_conf","r")
    filepath = os.getenv('XQUANT_CONF_FILE')
    f = open(filepath, "r")
    file = f.read()
    f.close()
    file = file.split('\n')
    param = file[5].split('=')[1]
    return param
# userid,xquant_id,task_config,fjob_id(),resource_config,

# param = {
#     "parallel_list": ["sfdsff","dddd","dsdgdgd"],
#     "docker_version": "htsc:latest",
#     "type": "gpu",
#     "is_sync":False,
#     "cpu":1,
#     "tag":"xquant",
#     "gpu":1,
#     "memory":12
# }
# run_tensorflow("a.py",json.dumps(param))


