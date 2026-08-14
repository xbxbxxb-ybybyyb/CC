# coding: utf-8
# Author：fengchi863
# Date ：2022/8/18 16:06

"""
用于个人docker初始化（每次重启后运行该文件）
"""
import os

#%% matplotlib相关，解决中文字体问题
os.system('cp /data/user/015614/python_package/simhei.ttf /opt/anaconda3/lib/python3.6/site-packages/matplotlib/mpl-data/fonts/ttf/')
os.system('cp /data/user/015614/python_package/matplotlibrc /opt/anaconda3/lib/python3.6/site-packages/matplotlib/mpl-data/')

import matplotlib
plt_cache_dir = matplotlib.get_cachedir()
os.system(f'rm -rf {plt_cache_dir}')
# 之后便可以使用下面的字段设置中文字体了
# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['font.family'] = ['sans-serif']

#%% 安装部分依赖的包
os.system('pip3 install shap')  # 用于模型特征解释
os.system('pip3 install tscv')  # 用于交叉验证
# os.system('pip3 install plotly')  # 用于绘图

