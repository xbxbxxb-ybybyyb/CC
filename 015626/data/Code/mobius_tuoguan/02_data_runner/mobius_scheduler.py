from apscheduler.schedulers.blocking import BlockingScheduler
import os
import datetime

def task_17_20():
    print("任务run_main：17:20 执行")
    os.system('python3 /dfs/user/666466/02_data_runner/run_0.py')
    # 在此处添加你的任务逻辑

def task_19_40():
    print("任务run_check：19:40 执行")
    os.system('python3 /dfs/user/666466/02_data_runner/pre_run_0.py')


def main():
    scheduler = BlockingScheduler()

    # 添加任务1：每天 17:20 执行
    scheduler.add_job(task_17_20, 'cron', hour=17, minute=20)

    # 添加任务2：每天 19:40 执行
    scheduler.add_job(task_19_40, 'cron', hour=19, minute=40)

    print("调度已启动，等待任务执行...")
    scheduler.start()

if __name__ == "__main__":
    main()
