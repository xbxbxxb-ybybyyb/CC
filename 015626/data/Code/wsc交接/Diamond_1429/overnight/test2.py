from overnight.factor_generator import *
from overnight.insight_retrieve_mdconstant import *
from overnight.insight_retrieve_alla import *
from overnight.insight_retrieve_misc_minute import *
from overnight.utility import *
from overnight.naming_config import *
import multifactor.utility.dt as udt
from multiprocessing import Process
import datetime
from xquant.xqutils.helper import link
lm = link.LinkMessage()





if __name__ == '__main__':
    retrieve_misc_minute_helper(release_resource=True)

