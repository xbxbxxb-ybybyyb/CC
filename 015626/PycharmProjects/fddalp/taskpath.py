import os

class TaskPath:
    def __init__(self, rootpath = '/data/user/015626/data/share/MD/alpha'):
        self.rootpath = rootpath
        self.rootpath1 = r'E:\pywork\prod\CHINA_STOCK'
        self.featurepath = os.path.join(rootpath, 'feature')
        self.fittingpath = os.path.join(rootpath, 'fitting')
        self.modelpath = os.path.join(self.rootpath1, 'model')
        self.strategypath = os.path.join(self.rootpath1, 'strategy')
        self.simpath = os.path.join(self.rootpath1,'sim')
    def check(self):
        pass
    