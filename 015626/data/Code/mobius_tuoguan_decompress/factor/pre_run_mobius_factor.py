
import sys
import os
import subprocess
import time
import threading
from notice import LinkMessage



def monitor_log_file(log_path, stop_event, error_event):

    try:
        with open(log_path, 'r', encoding='utf-8') as file:
            while not stop_event.is_set():
                lines = file.readlines()
                if not lines:
                    time.sleep(1)
                    continue

                for line in lines:
                    if 'error' in line.lower():
                        if '静态信息查询失败' not in line.lower():
                            error_event.set()
                            print("Error detected in log file.")
                            print(line)
                            stop_event.set()
                            break
                    if 'market data replay finished' in line.lower():
                        stop_event.set()

                if error_event.is_set():
                    break

            print("Log monitoring stopped.")

    except FileNotFoundError:
        print(f"Log file not found at path: {log_path}")
        stop_event.set()
    except Exception as e:
        print(f"Error monitoring log file: {str(e)}")
        stop_event.set()


def main():
    if len(sys.argv) != 3:
        print("Usage: python run_mobius_factor.py tradedate offset")
        return

    tradedate = sys.argv[1]
    offset = sys.argv[2]
    jar_path = "/dfs/user/666466/02_data_runner/factor/strategy-MobiusFactor-1.0-20250416-065343.jar"
    l = LinkMessage()
    # 设置参数
    java_opts = "-Xms6536m -Xmx120000m"
    main_class = "com.huatai.strategy.MobiusFactor.localTest.LocalTestRunner"
    base_path = "/dfs/user/666466/01_params"
    sub_dir = f"{tradedate}/offset_{offset}/factor"
    flag_root = f'/dfs/user/666466/04_flags/{sub_dir}/'
    pre_sub_dir = f"{tradedate}_check/offset_{offset}/factor"


    # 构建文件路径
    request_file = f"{base_path}/{pre_sub_dir}/request.json"
    params_file = f"{base_path}/{pre_sub_dir}/params.json"
    log_file = f"/dfs/user/666466/11_log/{pre_sub_dir}/MobiusFactor.log"
    log_dir = os.path.dirname(log_file)
    contract_flag = f'/dfs/group/900001/XDB_flags/marketdata_flags/future/UHFData/ContractInfo/{tradedate}_contract_univ.success'
    index_flag = f'/dfs/group/900001/XDB_flags/marketdata_flags/index/IndexWeight/{tradedate}_inx_ixcsiwgtnd.success'
    daily_flag = f'/dfs/group/900001/XDB_flags/marketdata_flags/stock/UHFData/DailyData/{tradedate}.success'
    
    if not os.path.exists(contract_flag):
        print(f'Error: {tradedate} contract file not exist')
        l.sendMessage(f'[Mobius因子]Error: {tradedate} contract file not exist')  
        return

    if not os.path.exists(index_flag):
        print(f'Error: {tradedate} index file not exist')
        l.sendMessage(f'[Mobius因子]Error: {tradedate} index file not exist')
        return

    if not os.path.exists(daily_flag):
        print(f'Error: {tradedate} stock daily file not exist')
        l.sendMessage(f'[Mobius因子]Error: {tradedate} stock daily file not exist')
        return



    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)

    # 检查文件是否存在
    if not os.path.exists(request_file) or not os.path.exists(params_file):
        print(f"Error: Required JSON files not found.")
        print(f"Request file path: {request_file}")
        print(f"Params file path: {params_file}")
        l.sendMessage(f"[Mobius因子]Error: Required JSON files not found with {tradedate} {offset}")
        return

    # 创建停止事件
    stop_event = threading.Event()
    stop_event.clear()
    # 创建错误事件
    error_event = threading.Event()
    error_event.clear()

    os.makedirs(flag_root, exist_ok=True)
    flag_path_start = flag_root + '/PreMobiusFactor.start'
    with open(flag_path_start, 'w') as file:
        pass

    l.sendMessage(f"[Mobius因子]Mobius Factor Check Start With {tradedate} {offset}")
    # 启动Java程序
    print("Starting Mobius Application...")
    java_command = f"java {java_opts} -cp {jar_path} {main_class} \"{request_file}\" \"{params_file}\""

    # 启动Java进程并重定向输出到日志文件
    with open(log_file, 'w') as log:
        process = subprocess.Popen(java_command, shell=True, stdout=log, stderr=log)
    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_log_file, args=(log_file, stop_event, error_event))
    monitor_thread.start()
    print('Log monitoring started')


    # 等待Java程序完成或停止事件被设置
    while process.poll() is None and not stop_event.is_set():
        time.sleep(1)

    # 如果监控线程检测到错误，终止Java进程
    if stop_event.is_set() and error_event.is_set():
        print("Error detected, terminating Java process...")
        process.terminate()
        process.wait()
        print("Java process terminated.")
        l.sendMessage(f"[Mobius因子]Mobius Factor Calc Error Detected With {tradedate} {offset}")
        return

    monitor_thread.join()
    if stop_event.is_set() and not error_event.is_set():
        process.terminate()
        process.wait()
        print("Application started successfully.")
        print("Log file check pass.")

    flag_path_success = flag_root + '/PreMobiusFactor.success'
    with open(flag_path_success, 'w') as file:
        pass

    print("Create flag  successfully.")

    l.sendMessage(f"[Mobius因子]Mobius Factor Check Success With {tradedate} {offset}")



if __name__ == "__main__":
    main()

