import sys
import os
import subprocess
import time, datetime
import threading


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
    log_file = f"/data/user/015626/data/share/LOCAL_DATA/Mobius/my_log/factor-{str(datetime.datetime.now())}.log"
    log_dir = os.path.dirname(log_file)

    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)

    # 创建停止事件
    stop_event = threading.Event()
    stop_event.clear()
    # 创建错误事件
    error_event = threading.Event()
    error_event.clear()


    # 启动Java程序
    print("Starting Mobius Application...")
    # java_command = f"java {java_opts} -cp {jar_path} {main_class} \"{request_file}\" \"{params_file}\""
    java_command = f"java -Xms6536m -Xmx120000m -cp . com.huatai.strategy.MobiusFactor.localTest.LocalTestRunner /dfs/user/666466/01_params/20250530/offset_0/factor/request.json /dfs/user/666466/01_params/20250530/offset_0/factor/params.json"
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
        # l.sendMessage(f"[Mobius因子]Mobius Factor Calc Error Detected With {tradedate} {offset}")
        return

    monitor_thread.join()
    if stop_event.is_set() and not error_event.is_set():
        process.terminate()
        process.wait()
        print("Application started successfully.")
        print("Log file check pass.")



    print("Create flag  successfully.")

    # l.sendMessage(f"[Mobius因子]Mobius Factor Calc Success With {tradedate} {offset}")



if __name__ == "__main__":
    main()