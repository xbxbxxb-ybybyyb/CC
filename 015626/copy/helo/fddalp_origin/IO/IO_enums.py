from enum import Enum, unique

@unique
class DType(Enum):
	STOCK   = 1
	FUTURES = 2
	SPOT    = 3
	INDEX   = 4

@unique
class DFreq(Enum):
	TICK      = 1
	MINUTE    = 2
	DAILY     = 3
	WEEKLY    = 4
	QUARTERLY = 5
	MONTHLY   = 6
	YEARLY    = 7

@unique
class DSource(Enum):
	HTSC = 1
	WIND = 2
	OPTM = 3
	STYLEFACTOR = 4
	STYLE = 5
	WEIGHT = 6
	SUNTIME = 7
	DERIVED = 8
	MAIN = 9
	SECONDMAIN = 10
	CSI  = 11
	STYLEFACTOR2 = 12
	

@unique
class UniType(Enum):
	HS300 = 1
	ZZ500 = 2
	SZ50  = 3

@unique
class MktType(Enum):
	CHINA = 1
	HK    = 2
	US    = 3

@unique
class FType(Enum):
	FDD      = 1 # Fundamental Data
	MD       = 2 # Market Data
	FCD      = 3 # Forcast Data
	FACTOR   = 4 # Factor Data
	ALPHA    = 5 # Alpha Factor
	RISK     = 6 # Risk Factor
	UNIV     = 7 # Universe Data
	INDUSTRY = 8 # Industry Data
	CALENDAR = 9 # Calendar Data
	FWD5     = 10
	FWD10    = 11
	FWD      = 12
	INDEXWEIGHT = 13
	VD		 = 14

@unique
class DTable(Enum):
	DERIVED_barra   = 1
	DERIVED_barra_descriptor = 2
	DERIVED_blacklist_filter = 3
	DERIVED_custom_descriptor = 4
	DERIVED_custom_universe = 5 
	DERIVED_fundamental_fix = 6
	DERIVED_market_descriptor = 7
	DERIVED_minute_block = 8
	DERIVED_risk = 9
	DERIVED_RTD = 10
	DERIVED_technical_indicator = 11
	DERIVED_market_base = 12
	AShareEODDerivativeIndicator = 13
