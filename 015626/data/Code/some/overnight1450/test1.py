from overnight.factor_generator import *
from overnight.insight_retrieve_mdconstant import *
from overnight.insight_retrieve_alla import *
from overnight.insight_retrieve_misc_minute import *
from overnight.naming_config import *
from overnight.utility import *
from multiprocessing import Process
from xquant.xqutils.helper import link
lm = link.LinkMessage()

    
            
if __name__ == '__main__':
    executor('20220425')