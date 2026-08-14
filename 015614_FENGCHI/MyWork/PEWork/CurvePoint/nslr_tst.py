# coding: utf-8
# Author：fengchi863
# Date ：2022/2/14 8:55

import sys
import os
sys.path.append('/data/group/800442/800319')
import numpy as np
import pandas as pd
from dataApi import getData, tradeDate, stockList
import datetime as dt
from PEWork.Package.nslr.nslr import fit_gaze
from PEWork.CurvePoint.point_struct import Point, Segment, TurningPoint
from PEWork.CurvePoint.enum_tst import Direction
from multiprocessing import Pool

data_path = '/data/group/800442/800319/Afengchi/junk_data/300750_minute_data/'
turning_data_path = '/data/group/800442/800319/Afengchi/junk_data/300750_turning_data/'


def calc_grad(point1, point2):
    grad = (point2.y - point1.y) / (point2.x - point1.x)
    return grad


def calc_dt_diff(t, base_t):
    t = dt.datetime.strptime(str(t), "%Y%m%d%H%M%S")
    base_t = dt.datetime.strptime(str(base_t), "%Y%m%d%H%M%S")
    diff = (t - base_t).seconds / 60
    if base_t.strftime("%H%M") <= "1130" and t.strftime("%H%M") >= "1300":
        diff -= 90
    return diff


def wrapper(stk_id, cur_dt):
    stk_code = stockList.trans_int2windcode(stk_id)
    cur_dt = cur_dt
    minute_data = pd.read_pickle(data_path + f'{cur_dt}.pkl')['close'].values[:, None]
    trade_minutes = tradeDate.trade_minutes
    ts = np.arange(0, len(trade_minutes))
    turning_lst = list()
    for idx, bar in enumerate(trade_minutes):
        segment_lst = list()
        cur_minute = trade_minutes[idx]
        cur_struct_dt = dt.datetime.strptime(str(cur_dt * 1000000 + cur_minute * 100), '%Y%m%d%H%M%S')
        if idx == 0:
            continue
        reconstruction = fit_gaze(ts[:idx+1], minute_data[:idx+1], structural_error=1.2, optimize_noise=False)
        for segment in reconstruction.segments:
            t = np.array(segment.t)
            x = np.array(segment.x)
            grad = calc_grad(Point(t[0], x[0]), Point(t[1], x[1]))
            segment_lst.append(Segment(symbol=stk_code,
                                       direction=Direction.Up if grad > 0 else Direction.Down,
                                       grad=grad,
                                       start_point=Point(trade_minutes[t[0]], x[0]),
                                       end_point=Point(trade_minutes[t[1]], x[1])))
        if len(segment_lst) <= 1:
            turning_lst.append(TurningPoint(symbol=stk_code,
                                            t=cur_struct_dt,
                                            direction=segment_lst[0].direction,
                                            point=Point(idx, minute_data[idx]),
                                            extrem_point=Point(trade_minutes[0], minute_data[0])))

        else:
            seg_a = segment_lst[-2]
            seg_b = segment_lst[-1]
            if seg_b.direction != seg_a.direction and turning_lst[-1].extrem_point.x < seg_a.end_point.x:
                turning_lst.append(TurningPoint(symbol=stk_code,
                                                t=cur_struct_dt,
                                                direction=seg_b.direction,
                                                point=Point(trade_minutes[idx], minute_data[idx]),
                                                extrem_point=seg_a.end_point))

    """转换成表格存储"""
    rec_lst = list()
    for tmp in turning_lst:
        t = int(tmp.t.strftime("%Y%m%d%H%M%S"))
        extrem_point_t = tmp.extrem_point.x
        extrem_point_t = int(tmp.t.strftime("%Y%m%d")) * 1000000 + extrem_point_t * 100
        diff = calc_dt_diff(t, extrem_point_t)
        direction = -1 if tmp.direction == Direction.Down else 1
        rec_lst.append([str(t), str(extrem_point_t), direction, diff])
    df = pd.DataFrame(rec_lst, columns=['更新时间', '最近一个极值点的时间', '拐点类型', '延迟时间'])
    df = df.drop_duplicates(['最近一个极值点的时间'], keep='first')
    os.makedirs(turning_data_path, exist_ok=True)
    df.to_excel(turning_data_path + f'{cur_dt}.xlsx')


if __name__ == '__main__':
    # wrapper(300750, 20210114)
    date_list = tradeDate.get_date_range(20210101, 20211231)
    pool = Pool(8)
    for dat in date_list:
        pool.apply_async(wrapper, (300750, dat,))
    pool.close()
    pool.join()
