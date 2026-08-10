from common.link_messager import *

from params.params_generator import *
from request.request_generator import *
from conf.templates_sim import *
from conf.templates_prod_new import *


class Generator:
    def __init__(self, user_ids=USER_IDS, real_env=True, use_h5_data=False):
        self.real_env = real_env
        self.user_ids = user_ids
        self.use_h5_data = use_h5_data
        self.link_messager = LinkMessage(user_ids)
        self.message_prefix = "[Mobius截面指标计算通知]"

    def send_link_message(self, msg: str):
        self.link_messager.sendMessage(self.message_prefix + msg)

    # base_date: for history indicator generation
    def write_params_file(self, mode, base_path, gen_trading_day, baseline_date=None, backend_params_dirpath=None,
                          mock=False, replay=False, strategy_name='MobiusCrossSectionCalculator', zone='${zone_id}', zone_ids=[], ami_context=None):
        if baseline_date is None:
            baseline_date = gen_trading_day
        params_generator = ParamsGenerator(self.real_env, self.user_ids, self.use_h5_data)
        content = params_generator.generate(gen_trading_day, baseline_date, mock, ami_context)
        self.date_dir_path = os.path.join(base_path, gen_trading_day, zone)
        if not os.path.exists(self.date_dir_path):
            os.makedirs(self.date_dir_path)
        filepath = os.path.join(self.date_dir_path, "config.json")
        serialize_to_file(content, filepath)
        if backend_params_dirpath is None:
            backend_params_dirpath = os.path.dirname(filepath)
        frontend_content = params_generator.generate_frontend(gen_trading_day, backend_params_dirpath)
        frontend_filepath = os.path.join(self.date_dir_path, "front_{}#{}.json".format(strategy_name, zone))
        serialize_to_file(frontend_content, frontend_filepath)
        self.write_bundle_config_file(params_generator, gen_trading_day, filepath, replay, zone_ids)
        self.write_md_cert_file(mode)
        self.send_link_message(f" {zone} 一体化参数准备完成!")

    def write_bundle_config_file(self, params_generator: ParamsGenerator, trading_day: str, filepath: str, replay: bool, zone_ids: list):
        config_content = params_generator.generate_config(trading_day, filepath, replay, zone_ids)
        config_filepath = os.path.join(self.date_dir_path, "settings.json")
        serialize_to_file(config_content, config_filepath)

    def write_md_cert_file(self, mode):
        md_cert_file = os.path.join(self.date_dir_path, "md.cert")
        if mode == 'sim':
            serialize_to_file(md_cert_tpl_sim, md_cert_file)
        elif mode == 'prod':
            serialize_to_file(md_cert_tpl_prod, md_cert_file)
        pass

    def write_request_file(self, base_path, date, version='v2'):
        request_generator = RequestGenerator()
        content = request_generator.generate(date, version)
        date_dir_path = os.path.join(base_path, date)
        if not os.path.exists(date_dir_path):
            os.makedirs(date_dir_path)
        filepath = os.path.join(date_dir_path, "request.json")
        serialize_to_file(content, filepath)
        params_generator = ParamsGenerator(self.real_env, self.user_ids, self.use_h5_data)
        backend_params_dirpath = os.path.join(base_path, date)
        frontend_content = params_generator.generate_frontend(date, backend_params_dirpath)
        frontend_filepath = os.path.join(backend_params_dirpath, "params.json")
        serialize_to_file(frontend_content, frontend_filepath)


if __name__ == "__main__":
    base_path = "/data/user/018728/cpp_projects/csi_calculator/testcase_v2"
    generator = Generator()
    generator.write_request_file(base_path, "20240509", 'v3')
