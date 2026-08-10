# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:36:35 2021

@author: appadmin
"""


from future_factor import FutureFactor
import pandas as pd
import datetime

class month_12(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.month == 12:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:35:33 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class month_9(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.month == 9:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:31:36 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class month_1(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.month == 1:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 09:27:09 2021

@author: appadmin
"""


from future_factor import FutureFactor
import pandas as pd
import datetime

class minute_seg_1(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if (t.time() >= datetime.time(9, 30)) and (t.time() <= datetime.time(10, 29)):
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:31:59 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class month_2(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.month == 2:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 09:30:12 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class minute_seg_2(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if (t.time() >= datetime.time(10, 30)) and (t.time() <= datetime.time(11, 29)):
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:34:06 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class month_8(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.month == 8:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 09:33:16 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class minute_seg_4(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if (t.time() >= datetime.time(14, 0)) and (t.time() <= datetime.time(15, 0)):
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 09:46:37 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class week_3(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.weekday() == 2:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 09:47:20 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class week_5(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.weekday() == 4:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:33:22 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class month_6(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.month == 6:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:32:14 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class month_3(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.month == 3:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:35:54 2021

@author: appadmin
"""


from future_factor import FutureFactor
import pandas as pd
import datetime

class month_10(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.month == 10:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 09:45:28 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class week_1(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.weekday() == 0:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 09:32:23 2021

@author: appadmin
"""


from future_factor import FutureFactor
import pandas as pd
import datetime

class minute_seg_3(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if (t.time() >= datetime.time(13, 0)) and (t.time() <= datetime.time(13, 59)):
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:32:58 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class month_5(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.month == 5:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 09:46:05 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class week_2(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.weekday() == 1:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:32:40 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class month_4(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.month == 4:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 09:46:59 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class week_4(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.weekday() == 3:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:33:44 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class month_7(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.month == 7:
            factor = 1
        else:
            factor = 0
        return factor
##########
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:36:15 2021

@author: appadmin
"""

from future_factor import FutureFactor
import pandas as pd
import datetime

class month_11(FutureFactor):

    data_type = 'Future'
    days_past = 0
    data_dict = dict()
    data_dict['Index_Id'] = {'000300.SH':['close']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000300.SH']).iloc[-1:]
        t = hclose.index[0]
        if t.month == 11:
            factor = 1
        else:
            factor = 0
        return factor
##########
