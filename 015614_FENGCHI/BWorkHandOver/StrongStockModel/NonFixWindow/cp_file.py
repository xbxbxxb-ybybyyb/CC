# @Time : 2022/2/23 23:09
# @Author : Zhichen Lu
# @File : cp_file.py
import os
for bar in range(1,9):
    for tag in ['catboost','lightgbm']:
        a = os.system(f'cp /data/group/800442/800319/wyl/model_record/nonfix/future_{bar}_bar/{tag}_out_of_sample_ic_all_t/*  '
                  f'/data/group/800442/800319/wyl/model_record/nonfix/future_{bar}_bar/{tag}_in_sample_ic_all_t/')
        b = os.system(f'cp /data/group/800442/800319/wyl/model_record/nonfix/future_{bar}_bar/{tag}_out_of_sample_ic_all_t_val_pred/*  '
                  f'/data/group/800442/800319/wyl/model_record/nonfix/future_{bar}_bar/{tag}_in_sample_ic_all_t_val_pred/')
        print(a)
        print(b)
    # os.system(f'cp /data/group/800442/800319/wyl/model_record/nonfix/future_{bar}_bar/lightgbm_out_of_sample_ic_all_t/*  /data/group/800442/800319/wyl/model_record/nonfix/future_{bar}_bar/lightgbm_in_sample_ic_all_t/')
    # os.system(f'cp /data/group/800442/800319/wyl/model_record/nonfix/future_{bar}_bar/lightgbm_out_of_sample_ic_all_t_val_pred/*  /data/group/800442/800319/wyl/model_record/nonfix/future_{bar}_bar/lightgbm_in_sample_ic_all_t_val_pred/')






