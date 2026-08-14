from FactorCalculator_old.UsefulList import ResearchMinuteList
import numpy as np


def reduce_first(arr, period):
    first_idx = ResearchMinuteList[1:-1:period]
    first_idx[0] = ResearchMinuteList[0]
    first_idx = [ResearchMinuteList.index(x) for x in first_idx]
    return arr[:, first_idx]


def reduce_last(arr, period):
    last_idx = ResearchMinuteList[period:-1:period]
    last_idx[-1] = ResearchMinuteList[-1]
    last_idx = [ResearchMinuteList.index(x) for x in last_idx]
    return arr[:, last_idx]


def reduce_sum(arr, period):
    first_idx = ResearchMinuteList[1:-1:period]
    first_idx[0] = ResearchMinuteList[0]
    first_idx = [ResearchMinuteList.index(x) for x in first_idx]
    return np.add.reduceat(arr, first_idx, axis=1)


def reduce_mean(arr, period):
    first_idx = ResearchMinuteList[1:-1:period]
    first_idx[0] = ResearchMinuteList[0]
    first_idx = [ResearchMinuteList.index(x) for x in first_idx]
    reduce_num = np.add.reduceat(np.ones(242, dtype='float32'), first_idx)
    return np.add.reduceat(arr, first_idx, axis=1) / reduce_num[:, None]


def reduce_max(arr, period):
    first_idx = ResearchMinuteList[1:-1:period]
    first_idx[0] = ResearchMinuteList[0]
    first_idx = [ResearchMinuteList.index(x) for x in first_idx]
    return np.maximum.reduceat(arr, first_idx, axis=1)


def reduce_min(arr, period):
    first_idx = ResearchMinuteList[1:-1:period]
    first_idx[0] = ResearchMinuteList[0]
    first_idx = [ResearchMinuteList.index(x) for x in first_idx]
    return np.minimum.reduceat(arr, first_idx, axis=1)


class ReduceMaterial(object):
    def __init__(self, period=5):
        first_idx = ResearchMinuteList[1:-1:period]
        first_idx[0] = ResearchMinuteList[0]
        first_idx = [ResearchMinuteList.index(x) for x in first_idx]
        last_idx = ResearchMinuteList[period:-1:period]
        last_idx[-1] = ResearchMinuteList[-1]
        last_idx = [ResearchMinuteList.index(x) for x in last_idx]
        reduce_num = np.add.reduceat(np.ones(242, dtype='float32'), first_idx)[:, None]
        self.first_idx = first_idx
        self.last_idx = last_idx
        self.reduce_num = reduce_num

    def first(self, arr):
        return arr[:, self.first_idx]

    def last(self, arr):
        return arr[:, self.last_idx]

    def sum(self, arr):
        return np.add.reduceat(arr, self.first_idx, axis=1)

    def mean(self, arr):
        return np.add.reduceat(arr, self.first_idx, axis=1) / self.reduce_num

    def max(self, arr):
        return np.maximum.reduceat(arr, self.first_idx, axis=1)

    def min(self, arr):
        return np.minimum.reduceat(arr, self.first_idx, axis=1)
