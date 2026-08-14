import os

import pandas as pd
import shutil
path_dict = {
'/data/group/800463/data/projectZZ_public/factor_lib/Basic_closed_hf_finish_20160101_20201231.h5':'/dfs/group/800463/public/projectZZ_public/factor_lib/Basic_closed_hf_finish_20160101_20201231.h5',
'/data/group/800463/data/projectZZ_public/factor_lib/sft_basic_formal_931_20160101_20201231.h5':'/dfs/group/800463/public/projectZZ_public/factor_lib/sft_basic_formal_931_20160101_20201231.h5',
'/data/group/800463/data/projectZZ_public/factor_lib/sft_update_931_20160101_20201231.pkl':'/dfs/group/800463/public/projectZZ_public/factor_lib/sft_update_931_20160101_20201231.pkl',
'/data/group/800463/data/projectZZ_public/factor_lib/check_res_tot_neptune.xlsx':'/dfs/group/800463/public/projectZZ_public/factor_lib/check_res_tot_neptune.xlsx',
}
for ori in path_dict.keys():
    new = path_dict[ori]
    print(new)
    shutil.copy(ori, new)
