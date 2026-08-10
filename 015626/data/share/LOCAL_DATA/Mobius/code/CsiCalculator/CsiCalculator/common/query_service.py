from xquant.factordata import FactorData
from xquant.futuredata import FutureData
from xquant.marketdata import MarketData

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

	def get_sorted_constituent_stock(self):
		return sorted(self.merged)

	def find_index_flag(self, stock):
		if stock in self.hs300_stock_list:
			return "HS300"
		elif stock in self.zz500_stock_list:
			return "ZZ500"
		elif stock in self.zz1000_stock_list:
			return "ZZ1000"
		elif stock in self.sh50_stock_list:
			return "SH50"

	def difference(self, const_stock):
		stocks_1 = self.get_sorted_constituent_stock()
		stocks_2 = const_stock.get_sorted_constituent_stock()
		diff = (list(set(stocks_1).difference(stocks_2)))
		return diff


if __name__ == '__main__':
	# const_stock_1 = ConstituentStock("20231115")
	const_stock_1 = ConstituentStock("20231012")
	const_stock_2 = ConstituentStock("20231113")
	diff1 = const_stock_1.difference(const_stock_2)
	diff2 = const_stock_2.difference(const_stock_1)
	print(diff1, diff2)
	for s in diff2:
		print(const_stock_2.find_index_flag(s))
