from loguru import logger
from xquant.factordata import FactorData
from xquant.futuredata import FutureData

factor_query_service = FactorData()
future_query_service = FutureData()


def get_index_constituent_stock(variety, trading_day):
	stocks = []
	res = factor_query_service.hset('INDEX', trading_day, variety, weightType=1)
	for index, row in res.iterrows():
		stocks.append(row['stock'])
	return stocks


class ConstituentStock:
	def __init__(self, base_date):
		self.base_date = base_date
		self.hs300_stock_list = get_index_constituent_stock('HS300', base_date)
		self.zz500_stock_list = get_index_constituent_stock('ZZ500', base_date)
		self.zz1000_stock_list = get_index_constituent_stock('ZZ1000', base_date)
		self.sh50_stock_list = get_index_constituent_stock('SH50', base_date)
		self.merged = set(self.hs300_stock_list + self.zz500_stock_list + self.zz1000_stock_list + self.sh50_stock_list)
		self.sorted_merge_stocks = sorted(self.merged)

	def get_sorted_constituent_stock(self):
		return self.sorted_merge_stocks

	def find_index_flag(self, stock):
		if stock in self.hs300_stock_list:
			return "HS300"
		elif stock in self.zz500_stock_list:
			return "ZZ500"
		elif stock in self.zz1000_stock_list:
			return "ZZ1000"
		elif stock in self.sh50_stock_list:
			return "SH50"

	def union(self, const_stock):
		stocks_1 = self.sorted_merge_stocks
		stocks_2 = const_stock.get_sorted_constituent_stock()
		union_ret = (list(set(stocks_1).union(stocks_2)))
		return union_ret

	def intersection(self, const_stock):
		stocks_1 = self.sorted_merge_stocks
		stocks_2 = const_stock.get_sorted_constituent_stock()
		intersection = (list(set(stocks_1).intersection(stocks_2)))
		return intersection

	def difference(self, const_stock):
		stocks_1 = self.sorted_merge_stocks
		stocks_2 = const_stock.get_sorted_constituent_stock()
		diff = (list(set(stocks_1).difference(stocks_2)))
		return diff


def check_constituent_stock_change(pre_date, next_date):
	const_stock_1 = ConstituentStock(pre_date)
	const_stock_2 = ConstituentStock(next_date)
	intersection = const_stock_1.intersection(const_stock_2)
	diff1 = const_stock_1.difference(const_stock_2)
	diff2 = const_stock_2.difference(const_stock_1)
	tag_changed_stocks = []
	for stock in intersection:
		tag1 = const_stock_1.find_index_flag(stock)
		tag2 = const_stock_2.find_index_flag(stock)
		if tag1 != tag2:
			tag_changed_stocks.append((stock, tag1, tag2))
	kick_out_stocks = []
	for stock in diff1:
		tag = const_stock_1.find_index_flag(stock)
		kick_out_stocks.append((stock, tag))
	get_into_stocks = []
	for stock in diff2:
		tag = const_stock_2.find_index_flag(stock)
		get_into_stocks.append((stock, tag))
	check_result = True
	if len(diff1) > 0 or len(diff2) > 0 or len(tag_changed_stocks) > 0:
		check_result = False
		logger.info("Constituent stock changed, date1={}, date2={}", d, nd)
		logger.info("index_tag_changed={}", tag_changed_stocks)
		logger.info("kick_out={}", kick_out_stocks)
		logger.info("get_into={}", get_into_stocks)
	return check_result


# for s in diff2:
# 	print(const_stock_2.find_index_flag(s))

# ['20231129', '20231130', '20231201', '20231204', '20231205', '20231206', '20231207', '20231208', '20231211', '20231212',
#  '20231213', '20231214', '20231215', '20231218', '20231219', '20231220', '20231221', '20231222', '20231225', '20231226',
#  '20231227', '20231228', '20231229', '20240102', '20240103', '20240104', '20240105', '20240108', '20240109', '20240110']

if __name__ == '__main__':
	# cur_date = datetime.datetime.now().strftime("%Y%m%d")
	# all_dates = factor_query_service.tradingday(cur_date, -30)
	# print(all_dates)
	all_dates = ['20231201', '20231204', '20231205', '20231206', '20231207', '20231208', '20231211', '20231212',
	             '20231213', '20231214', '20231215', '20231218', '20231219', '20231220', '20231221', '20231222',
	             '20231225', '20231226',
	             '20231227', '20231228', '20231229', '20240102', '20240103', '20240104', '20240105', '20240108',
	             '20240109', '20240110']
	# all_dates = ['20231211', '20231212', '20231213', '20231214', '20231215', '20231218', '20231219', '20231220',
	#              '20231221', '20231222',
	#              '20231225', '20231226', '20231227', '20231228', '20231229', '20240102', '20240103', '20240104',
	#              '20240105', '20240108', '20240109', '20240110']
	print(len(all_dates))
	for i in range(0, len(all_dates) - 1):
		d = all_dates[i]
		nd = all_dates[i + 1]
		check_constituent_stock_change(d, nd)
