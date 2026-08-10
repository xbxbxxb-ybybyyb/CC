import os
from datetime import datetime
from loguru import logger


from generator import Generator

def prepare_history_dates():
    # dates = [
    # "20231012",
    # "20231013",
    # "20231016",
    # "20231017",
    # "20231018",
    # "20231019",
    # "20231020",
    # "20231023",
    # "20231024",
    # "20231025",
    # "20231026",
    # "20231027",
    # "20231030",
    # "20231031",
    # "20231101",
    # "20231102",
    # "20231103",
    # "20231106",
    # "20231107",
    # "20231108",
    # "20231109",
    # "20231110",  # calculate this day
    # # "20231113",# 变化
    # ]
    #
    base_date = "20231120"
    dates = ["20231120"]
    # 参数文件生成所在路径
    # testcase_base_path = os.getcwd()
    testcase_base_path = "/data/user/018728/cpp_projects/csi_calculator/testcase"
    # dates = ["20231031"]
    # 后端参数地址
    # backend_params_dirpath = os.path.join(os.getcwd(), dates[0])
    generator = Generator()
    for dt in dates:
        logger.info("Begin preparing parameters, history_date={}, base_date={}", dt, base_date)
        generator.write_params_file(testcase_base_path, dt, base_date)
        generator.write_request_file(testcase_base_path, dt)

        logger.info("Finish preparing parameters done, base_date={}", dt)


if __name__ == '__main__':
    prepare_history_dates()
