import sys
from loguru import logger
import notice


def send_link_message(msg):
    lm = notice.LinkMessage()
    lm.sendMessage(msg)


def check_log_file(log_path):
    has_error = False
    has_ready = False

    try:
        with open(log_path, 'r', encoding='utf-8') as file:
            for line in file:
                if 'error' in line.lower():
                    if '静态信息查询失败' not in line.lower():
                        logger.info("check error {}", line)
                        has_error = True
                if 'ready to finish' in line.lower():
                    logger.info("check ready", line)
                    has_ready = True

        if has_error:
            send_link_message("模型日志分析出现ERROR, 文件名{}".format(log_path))
            return -1
        if not has_ready:
            send_link_message("模型日志分析,未出现Ready, 文件名{}".format(log_path))
            return -2

        logger.info("Log file check pass.")
        send_link_message("模型日志分析通过, 文件名{}".format(log_path))
        return 0

    except FileNotFoundError:
        raise Exception(f"Log file not found at path: {log_path}")
    except Exception as e:
        raise e



if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_log_file(sys.argv[1])
    else:
        logger.error("should input log file")
