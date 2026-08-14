# coding: utf-8
# Author：fengchi863
# Date ：2022/2/14 10:50
from PEWork.CurvePoint.enum_tst import Direction
from dataclasses import dataclass
import datetime as dt


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Segment:
    symbol: str
    direction: Direction
    grad: float
    start_point: Point
    end_point: Point


@dataclass
class TurningPoint:
    symbol: str
    t: dt.datetime
    direction: Direction
    point: Point
    extrem_point: Point