import sys

def check_log_file(log_path):
    has_error = False
    has_ready = False

    try:
        with open(log_path, 'r', encoding='utf-8') as file:
            for line in file:
                if 'error' in line.lower():
                    if '静态信息查询失败' not in line.lower():
                        has_error = True
                if 'ready to finish' in line.lower():
                    has_ready = True

        if has_error:
            raise Exception("Find error in log file.")
        if not has_ready:
            raise Exception("Keyword 'ready to finish' not found in log file.")

        print("Log file check pass.")

    except FileNotFoundError:
        raise Exception(f"Log file not found at path: {log_path}")
    except Exception as e:
        raise e


def main():
    tradedate = sys.argv[1]
    offset = sys.argv[2]
    log_file_path = f'/dfs/user/666466/11_log/{tradedate}/offset_{offset}/factor/MobiusFactor.log'
    check_log_file(log_file_path)


if __name__ == "__main__":
    main()
