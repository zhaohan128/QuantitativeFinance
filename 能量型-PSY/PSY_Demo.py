# -*- coding: utf-8 -*-
#通达信PSY-心理线
#PCNT幅度比指标是考察股票的涨跌幅度代替涨跌值的大小，有利于判断股票的活跃程度。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#pcnt-%E5%B9%85%E5%BA%A6%E6%AF%94
#https://www.zcaijing.com/jdjszb/263725.html
#本文件：主要对PSY进行回测，需要数据包含收盘价['close']
#测试时间：20220318
"""
指标源代码
PSY:COUNT(CLOSE>REF(CLOSE,1),N)/N*100;
PSYMA:MA(PSY,M);

用法注释：
1.PSY>75，形成Ｍ头时，股价容易遭遇压力；
2.PSY<25，形成Ｗ底时，股价容易获得支撑；
3.PSY 与VR 指标属一组指标群，须互相搭配使用。
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

#计算PSY和PSYMA的值
def calc_PSY(mkt_data, N=12, M=6):
    """
    计算PSY 的值
    PSY:COUNT(CLOSE>REF(CLOSE,1),N)/N*100;
    PSYMA:MA(PSY,M);

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含收盘价['close']
    :param M int MAPSY参数M

    :return mkt_data DataFrame 新增2列，PSY和PSYMA的值
    """
    def calc_days(X,N):
        Z = [0] * N
        for i in range(N,len(X)):
            XX = X.loc[i-N:i]
            z=0
            for x, px in zip(XX, XX.shift(1)):
                if x > px:
                    z += 1
            Z.append(z/N * 100)
        return Z

    mkt_data['PSY'] = calc_days(mkt_data['close'],N)
    mkt_data['PSYMA'] = mkt_data['PSY'].rolling(M).mean()

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
    PSY = mkt_data['PSY']
    PSYMA = mkt_data['PSYMA']
    indi.line(dt, PSY, line_width=1, color='green')
    indi.line(dt, PSYMA, line_width=1, color='yellow')

    # p = column(f1,f2,f3,f4)
    p = gridplot([[f1],
                  [indi]
                  ])
    show(p)

#运行部分
data = pd.read_csv('data/000001.csv')
data = calc_PSY(data)
visualize_performance(data)

