# -*- coding: utf-8 -*-
#通达信PCNT-幅度比
#PCNT幅度比指标是考察股票的涨跌幅度代替涨跌值的大小，有利于判断股票的活跃程度。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#pcnt-%E5%B9%85%E5%BA%A6%E6%AF%94
#https://www.zcaijing.com/jdjszb/263725.html
#本文件：主要对MASS进行回测，需要数据包含收盘价['close']、波动率['pct_chg']
#测试时间：20220318
"""
指标源代码
幅度比＝（收盘价－昨收价）＋收盘价X100
并计算PCNT的M日加权平滑平均

用法注释：
1.PCNT 重视价格的涨跌幅度，排除观察涨跌跳动值；
2.较高的PCNT 值，表示该股波动幅度大；
3.较低的PCNT 值，表示该股波动幅度小。
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

#计算PCNT 和 MAPCNT 的值
def calc_PCNT(mkt_data, M=5):
    """
    计算PCNT 和 MAPCNT 的值
    幅度比＝（收盘价－昨收价）＋收盘价X100
    并计算PCNT的M日加权平滑平均

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含收盘价['close']
    :param M int MAMASS参数M

    :return mkt_data DataFrame 新增2列，PCNT 和 MAPCNT 的值
    """

    mkt_data['PCNT'] = (mkt_data['close'] - mkt_data['close'].shift(1)) / mkt_data['close'] * 100
    mkt_data['MAPCNT'] = calc_WMA(mkt_data['PCNT'], M)

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
    PCNT = mkt_data['PCNT']
    MAPCNT = mkt_data['MAPCNT']
    indi.line(dt, PCNT, line_width=1, color='green')
    indi.line(dt, MAPCNT, line_width=1, color='yellow')

    # p = column(f1,f2,f3,f4)
    p = gridplot([[f1],
                  [indi]
                  ])
    show(p)

#运行部分
data = pd.read_csv('data/000001.csv')
data = calc_PCNT(data)
visualize_performance(data)

