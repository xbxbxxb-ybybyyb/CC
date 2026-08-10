from xquant.compute.aimr import AIMR
import json, os
print("start")


# for signame in ['mom_ac_s100','mom_ac', 'mom_ac_s50', 'mom_ac_s200', ]:
for signame in ['mom_etc', 'mom_adj', 'lmrt', 'rs_mod', 'trm']:
    para_list = []
    sig_rootpath = '/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/zf_all/'
    sig_pkl_name_list = [x.replace('.pkl', '') for x in os.listdir(sig_rootpath) if x.startswith(signame)]
    if signame == 'mom_ac':
        sig_pkl_name_list = [x for x in sig_pkl_name_list if not x.startswith('mom_ac_s')]
    for sig_pkl_name in sig_pkl_name_list:
        # for is_filter in [False]:
            # for periods in [('20180101', '20221231'), ('20230101', '20241231')]:
        para_list.append(str([signame, sig_pkl_name]))
    if len(para_list) >= 100:
        pp_list1 = para_list[:100]
        pp_list2 = para_list[100:200]
        pp_list3 = para_list[200:]
        for pp in [pp_list1, pp_list2, pp_list3]:
            params = {
                "parallel_list": pp, 
                "docker_version":'cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:dol_genesis_cpu',  
                "tag":"xquant",
                "cpu":1,
                "gpu":0,
                "memory":12000,
                "preferred_gpu":0,
                "subtask_limit_num":100 
            }
            from xquant.xqutils.helper import link
            lm = link.LinkMessage()
            lm.sendMessage(f"start qiefen {signame}")

            print(f"start {signame}")
            #job.py文件为用户自定义的并行任务文件    
            result = AIMR.runTasks('bt_signals_aimr_job.py',json.dumps(params))

        continue

    params = {
        "parallel_list": para_list, 
        "docker_version":'cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:dol_genesis_cpu',  
        "tag":"xquant",
        "cpu":1,
        "gpu":0,
        "memory":12000,
        "preferred_gpu":0,
        "subtask_limit_num":100 
    }
    from xquant.xqutils.helper import link
    lm = link.LinkMessage()
    lm.sendMessage(f"start {signame}")

    print(f"start {signame}")
    #job.py文件为用户自定义的并行任务文件    
    result = AIMR.runTasks('bt_signals_aimr_job.py',json.dumps(params))
    lm.sendMessage(f"{signame} done")
    del(lm)
    print(f"{signame} done")

print("end")
from xquant.xqutils.helper import link
lm = link.LinkMessage()
lm.sendMessage(f"aimr all done")


'''


para_list = []
for signame in ['mom_ac_s100']:
# for signame in ['mom_ac', 'mom_ac_s50', 'mom_ac_s100', 'mom_ac_s200', 'mom_etc', 'mom_adj', 'lmrt', 'rs_mod', 'trm']:
    sig_rootpath = '/dfs/group/800466/warehouse/test/alpha/CHINA_COMMODITIES/1MIN/zf_all/'
    sig_pkl_name_list = [x.replace('.pkl', '') for x in os.listdir(sig_rootpath) if x.startswith(signame)]
    if signame == 'mom_ac':
        sig_pkl_name_list = [x for x in sig_pkl_name_list if not x.startswith('mom_ac_s')]
    for sig_pkl_name in sig_pkl_name_list:
        for is_filter in [False]:
            # for periods in [('20180101', '20221231'), ('20230101', '20241231')]:
            for periods in [('20180101', '20221231')]:
                para_list.append(str([signame, sig_pkl_name, is_filter, periods]))

params = {
    "parallel_list": para_list, 
    "docker_version":'cgcregistry.azurecr.io/cgc/jupyter_hadoop26_spark22:dol_genesis_cpu',  
    "tag":"xquant",
    "cpu":1,
    "gpu":0,
    "memory":12000,
    "preferred_gpu":0,
    "subtask_limit_num":100 
}
#job.py文件为用户自定义的并行任务文件    
result = AIMR.runTasks('bt_signals_aimr_job.py',json.dumps(params))

print("end")
from xquant.xqutils.helper import link
lm = link.LinkMessage()
lm.sendMessage(f"aimr done!")
'''