from param_generator.params.params_generator import *
from param_generator.request.request_generator import *
from param_generator.conf.md_templates_sim import *
from param_generator.conf.md_templates_prod import *


class Generator:
    def __init__(self, real_env=True, use_h5_data=False):
        self.real_env = real_env
        # self.user_ids = user_ids
        self.use_h5_data = use_h5_data
        # self.link_messager = LinkMessage(user_ids)
        self.message_prefix = "[Mobius截面指标计算通知]"

    # def send_link_message(self, msg: str):
    #     self.link_messager.sendMessage(self.message_prefix + msg)

    # base_date: for history indicator generation
    def write_params_file(self, mode, base_path, gen_trading_day, baseline_date=None, backend_params_dirpath=None,
                          mock=False, replay=False, strategy_name='MobiusCrossSectionCalculator', zone='${zone_id}',
                          zone_ids=[], batch_run_stock_list=None, load_his_data=None, work_indicator_folder=None,
                          minute_shift=0, work_index_weight_folder=None):
        if baseline_date is None:
            baseline_date = gen_trading_day
        params_generator = ParamsGenerator(self.real_env, self.use_h5_data)
        content = params_generator.generate(gen_trading_day, baseline_date, mock, batch_run_stock_list=batch_run_stock_list,
                                            load_his_data=load_his_data, work_indicator_folder=work_indicator_folder,
                                            minute_shift=minute_shift, work_index_weight_folder=work_index_weight_folder)
        # if int(gen_trading_day) <= 20250214 and "302132.SZ" in content:
        #     content = content.replace("302132.SZ", "300114.SZ")

        self.date_dir_path = base_path
        if not os.path.exists(self.date_dir_path):
            os.makedirs(self.date_dir_path)
        config_folder = os.path.join(self.date_dir_path, f"offset_{minute_shift}")
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)
        filepath = os.path.join(config_folder, "config.json")
        serialize_to_file(content, filepath)
        if backend_params_dirpath is None:
            backend_params_dirpath = os.path.dirname(filepath)
        frontend_content = params_generator.generate_frontend(gen_trading_day, backend_params_dirpath)
        frontend_filepath = os.path.join(self.date_dir_path, "front_{}#{}.json".format(strategy_name, zone))
        serialize_to_file(frontend_content, frontend_filepath)
        if mode == 'sim':
            replay = True
        self.write_bundle_config_file(params_generator, gen_trading_day, filepath, replay, zone_ids, minute_shift=minute_shift)
        self.write_md_cert_file(mode)
        # self.send_link_message(" 一体化参数准备完成!")

    def write_bundle_config_file(self, params_generator: ParamsGenerator, trading_day: str, filepath: str, replay: bool, zone_ids: list,
                                 minute_shift=0):
        config_content = params_generator.generate_config(trading_day, filepath, replay, zone_ids, minute_shift=minute_shift)
        config_filepath = os.path.join(self.date_dir_path, "settings.json")
        serialize_to_file(config_content, config_filepath)

    def write_md_cert_file(self, mode):
        md_cert_file = os.path.join(self.date_dir_path, "md.cert")
        if mode == 'sim':
            serialize_to_file(md_cert_tpl_sim, md_cert_file)
        elif mode == 'prod':
            serialize_to_file(md_cert_tpl_prod, md_cert_file)
        pass

    def write_request_file(self, base_path, date, version='v2', replay_data_date=None):
        request_generator = RequestGenerator()
        if replay_data_date is None:
            content = request_generator.generate(date)
        else:
            content = request_generator.generate(replay_data_date)
        # date_dir_path = os.path.join(base_path, date)
        date_dir_path = base_path
        if not os.path.exists(date_dir_path):
            os.makedirs(date_dir_path)
        filepath = os.path.join(date_dir_path, "request.json")
        serialize_to_file(content, filepath)
        params_generator = ParamsGenerator(self.real_env, self.use_h5_data)
        backend_params_dirpath = base_path
        frontend_content = params_generator.generate_frontend(date, backend_params_dirpath)
        frontend_filepath = os.path.join(backend_params_dirpath, "params.json")
        serialize_to_file(frontend_content, frontend_filepath)

    def write_request_file_for_channel(self, base_path, date, channel_name):
        request_generator = RequestGenerator(channel_name)
        content = request_generator.generate(date)
        # date_dir_path = os.path.join(base_path, date, channel_name)
        date_dir_path = os.path.join(base_path, channel_name)
        if not os.path.exists(date_dir_path):
            os.makedirs(date_dir_path)
        filepath = os.path.join(date_dir_path, "request.json")
        serialize_to_file(content, filepath)
        params_generator = ParamsGenerator(self.real_env, self.use_h5_data)

        backend_params_dirpath = date_dir_path
        frontend_content = params_generator.generate_frontend(date, backend_params_dirpath)
        frontend_filepath = os.path.join(backend_params_dirpath, "params.json")
        serialize_to_file(frontend_content, frontend_filepath)


if __name__ == "__main__":
    base_path = "/data/user/019906/018728/cpp_projects/csi_calculator/testcase_v3"
    generator = Generator()
    # generator.write_request_file(base_path, "20240805", 'v3')

    front_param_zone = '503304'
    generator.write_params_file(mode='sim', base_path=base_path, gen_trading_day="20240805", zone=front_param_zone,zone_ids=[front_param_zone])
