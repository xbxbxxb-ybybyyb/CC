from common.link_messager import *
from params.params_generator import *
from request.request_generator import *


class Generator:
	def __init__(self, user_ids=USER_IDS, real_env=True):
		self.real_env = real_env
		self.user_ids = user_ids

	# base_date: for history indicator generation
	def write_params_file(self, base_path, gen_trading_day, baseline_date=None, backend_params_filepath=None):
		if baseline_date is None:
			baseline_date = gen_trading_day
		params_generator = ParamsGenerator(self.real_env, self.user_ids)
		content = params_generator.generate(gen_trading_day, baseline_date)
		date_dir_path = os.path.join(base_path, gen_trading_day)
		if not os.path.exists(date_dir_path):
			os.makedirs(date_dir_path)
		filepath = os.path.join(date_dir_path, "settings.json")
		serialize_to_file(content, filepath)
		if backend_params_filepath is not None:
			filepath = backend_params_filepath
		frontend_content = params_generator.generate_frontend(gen_trading_day, filepath)
		frontend_filepath = os.path.join(date_dir_path, "params.json")
		serialize_to_file(frontend_content, frontend_filepath)

	def write_request_file(self, base_path, date):
		request_generator = RequestGenerator()
		content = request_generator.generate(date)
		date_dir_path = os.path.join(base_path, date)
		if not os.path.exists(date_dir_path):
			os.makedirs(data_dir_path)
		filepath = os.path.join(date_dir_path, "request.json")
		serialize_to_file(content, filepath)


if __name__ == "__main__":
	base_path = "/data/user/018728/cpp_projects/csi_calculator/testcase"
	generator = Generator()
	generator.write_request_file(base_path, "20230615")
