# coding: utf-8
# Author：fengchi863
# Date ：2020/5/14 15:18

import pickle

import pandas as pd


class DataUtil:
    def save_pickle_file(self, data, file_path, filetype="wb", prot=-1):
        with open(file_path, filetype) as f:
            pickle.dump(data, f, prot)
        print("Saved data in the %s " % file_path)

    def open_pickle_file(self, file_path, file_type='rb'):
        with open(file_path, file_type) as f:
            data = pickle.load(f)
        return data

    @staticmethod
    def save_pkl(path, pkl_name, **args_dict):
        if not pkl_name.endswith('.pkl'):
            pkl_name += '.pkl'
        pd.to_pickle(args_dict, path + pkl_name)
        print('saved %s in %s' % (','.join(list(args_dict.keys())), path + pkl_name))

DataUtil = DataUtil()
