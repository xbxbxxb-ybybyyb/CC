import json
from common.tools import *
from request.templates import *

class RequestGenerator:

	def __init__(self):
		self.thread_num = "40"
		self.request_template = template_request

	def generate(self, date):
		request = self.request_template.copy()
		fdate = format_date(date)
		request['StartDate'] = fdate
		request['EndDate'] = fdate
		request['TradeDate'] = str(date)
		content = json.dumps(request, indent=4, ensure_ascii=False)
		content = content.replace('${TRADING_DATE}', date)
		source = 'udp'
		filepath = os.path.join('/data/group/800445/Insight/shm/', date, 'sh_market_data_udp_1.gz')
		if not os.path.exists(filepath):
			source = 'parquet'
		content = content.replace('${DATA_SOURCE}', source)
		return content

def write_request_file(base_path, date):
	request_generator = RequestGenerator()
	content = request_generator.generate(date)
	date_dir_path = os.path.join(base_path, date)
	if not os.path.exists(date_dir_path):
		os.makedirs(data_dir_path)
	filepath = os.path.join(date_dir_path, "request.json")
	serialize_to_file(content, filepath)


if __name__ == "__main__":
	base_path = "/data/user/018728/cpp_projects/csi_calculator/testcase"
	write_request_file(base_path, "20230615")
