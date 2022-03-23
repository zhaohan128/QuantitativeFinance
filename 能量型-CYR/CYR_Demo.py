# -*- coding: utf-8 -*-
#CYR-市场强弱
#CYR市场强弱指标是成本均线派生出的一个指标，就是13日成本均线的升降速度。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#cyr-%E5%B8%82%E5%9C%BA%E5%BC%BA%E5%BC%B1
#https://www.zcaijing.com/jdjszb/263724.html
#本文件：主要对CYR进行回测，需要包含成交额['amount']、成交量['volume']
#测试时间：20220316
"""
DIVE=0.01X成交额（元）的N日加权移动平均＋成交量（手）的N日加权移动平均
CYR市场强弱=(DIVE÷昨日DIVE-1)X100

用法注释：
1.CYR是成本均线派生出的指标,是13日成本均线的升降幅度;
2.使用CYR可以对股票的强弱进行排序,找出其中的强势和弱势股票。
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

#加权平均WMA(X, n)
def calc_WMA(X, n):
    """
    计算WMA(X, n)
    WMA(X,n)_t = (n * X_t + (n-1) * X_{t-1} +...+ 2 * X_{t-n+2} + X_{t-n+1}) / (n + (n-1) +...+ 2 + 1)

    :param X Series WMA(X, n)的X
    :param n int WMA(X, n)参数N

    :return Y Series WMA(X, n)的值
    """
    weights = np.array(range(1, n+1))
    sum_weights = np.sum(weights)

    res = X.rolling(window=n).apply(lambda x: np.sum(weights*x) / sum_weights, raw=False)
    return res

#计算CYR 和 MACYR 的值
def calc_CYR(mkt_data, n=13, m=5):
    """
    计算CYR 和 MACYR 的值。
    DIVE=0.01X成交额（元）的N日加权移动平均＋成交量（手）的N日加权移动平均
    CYR市场强弱=(DIVE÷昨日DIVE-1)X100

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含成交额['amount']、成交量['volume']
    :param n int CYR参数n
    :param m int MACYR参数m

    :return mkt_data DataFrame 新增3列,B, VAR2和绝路航标的值。
    """
    close = mkt_data['close']
    high = mkt_data['high']
    low = mkt_data['low']
    """计算指标"""
    DIVE = 0.01 * calc_WMA(mkt_data['amount'], n) + calc_WMA(mkt_data['volume'], n)
    CYR = (DIVE / DIVE.shift(1) - 1) * 100
    MACYR = CYR.rolling(m).mean()
    """指标赋值"""
    mkt_data['CYR'] = CYR
    mkt_data['MACYR'] = MACYR

    return mkt_data

#可视化
def visualize_performance(mkt_data):
    """
    可视化;

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含日期['date']、收盘价['close']

    :return plot html 可交互式图
    """
    mkt_data['trade_datetime'] = mkt_data['date'].apply(lambda x: datetime.datetime.strptime(str(x), '%Y-%m-%d'))
    dt = mkt_data['trade_datetime']

    f1 = figure(height=300, width=700,
                sizing_mode='stretch_width',
                title='Target Trend',
                x_axis_type='datetime',
                x_axis_label="trade_datetime", y_axis_label="close")

    indi = figure(height=200, sizing_mode='stretch_width',
                  title='Factor',
                  x_axis_type='datetime',
                  x_range=f1.x_range
                  )

    # 绘制行情
    close = mkt_data['close']
    f1.line(dt, close / close.tolist()[0], line_width=1)

    # 绘制指标
    CYR = mkt_data['CYR']
    MACYR = mkt_data['MACYR']
    indi.line(dt, CYR, line_width=1, color='green')
    indi.line(dt, MACYR, line_width=1, color='yellow')

    # p = column(f1,f2,f3,f4)
    p = gridplot([[f1],
                  [indi]
                  ])
    show(p)

#运行部分
data = pd.read_csv('data/000001.csv')
data = calc_CYR(data)
visualize_performance(data)

