# -*- coding: utf-8 -*-
#通达信VR-成交量变异率
#VR成交量变异率指标是成交量的强弱指标，主要的作用在于以成交量的角度测量股价的热度，不同于AR、BR、CR等指标的价格角度，但是却同样基于“反市场操作＂的原理为出发点，运用在过热市场及低速盘局中，对辨别头部及底部的形成有很重要的作用。VR值能表现股市买卖的气势，进而掌握股价之趋向。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#vr-%E6%88%90%E4%BA%A4%E9%87%8F%E5%8F%98%E5%BC%82%E7%8E%87
#https://www.zcaijing.com/jdjszb/263722.html
#本文件：主要对VR进行回测，需要数据包含收盘价['close']、成交量['volume']
#测试时间：20220318
"""
指标源代码
1.AV=N日内股价上升日成交量；AVS=N日内LAV
2.BV=N日内股价下跌日成交量；BVS=N日内LBV
3.CV=N日内股价平盘日成交量；CVS=N日内LCV
4.VR=(AVS+1/2CVS)/(BVS+1/2CVS)
5.MAVR=VR的M日简单移动平均

用法注释：
1.VR>450，市场成交过热，应反向卖出；
2.VR<40 ，市场成交低迷，人心看淡的际，应反向买进；
3.VR 由低档直接上升至250，股价仍为遭受阻力，此为大行情的前兆；
4.VR 除了与PSY为同指标群外，尚须与BR、AR、CR同时搭配研判
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span


def calc_days(X, N):
    VR = [None] * N
    for i in range(N, len(X)):
        XX = X.loc[i - N:i]
        av = 0
        bv = 0
        cv = 0
        for j in range(1, len(XX)):
            if XX['close'].iloc[j] > XX['close'].iloc[j - 1]:
                av += XX['volume'].iloc[j]
            elif XX['close'].iloc[j] < XX['close'].iloc[j - 1]:
                bv += XX['volume'].iloc[j]
            else:
                cv = cv + XX['volume'].iloc[j]
        VR.append((av + 1 / 2 * cv) / (bv + 1 / 2 * cv))

    return VR

#计算VR和MAVR 的值
def calc_VR(mkt_data, N=26, M=6):
    """
    计算VR和MAVR 的值
    1.AV=N日内股价上升日成交量；AVS=N日内LAV
    2.BV=N日内股价下跌日成交量；BVS=N日内LBV
    3.CV=N日内股价平盘日成交量；CVS=N日内LCV
    4.VR=(AVS+1/2CVS)/(BVS+1/2CVS)
    5.MAVR=VR的M日简单移动平均

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含收盘价['close']
    :param M int MAPSY参数M

    :return mkt_data DataFrame 新增2列，VR和MAVR 的值
    """

    mkt_data['VR'] = calc_days(mkt_data[['close','volume']],N)
    mkt_data['MAVR'] = mkt_data['VR'].rolling(M).mean()

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
    VR = mkt_data['VR']
    MAVR = mkt_data['MAVR']
    indi.line(dt, VR, line_width=1, color='green')
    indi.line(dt, MAVR, line_width=1, color='yellow')

    # p = column(f1,f2,f3,f4)
    p = gridplot([[f1],
                  [indi]
                  ])
    show(p)

#运行部分
data = pd.read_csv('data/000300.csv')
data = calc_VR(data)
visualize_performance(data)

