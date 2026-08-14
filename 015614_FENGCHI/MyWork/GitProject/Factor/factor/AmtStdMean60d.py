from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd

class AmtStdMean60d(BaseFactor):

	factor_type = "DAY"
	s_amt = 'FactorData.Basic_factor.amt'
	depend_data = [s_amt]
	n = 60
	lag = n-1

	def calc_single(self, database):
		amt = database.depend_data[self.s_amt]
		res = -amt.std(axis=0) / amt.mean(axis=0)
		return res

