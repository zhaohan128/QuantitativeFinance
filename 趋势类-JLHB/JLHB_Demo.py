# -*- coding: utf-8 -*-
#JLHB-绝路航标
#反趋势类选股指标。综合了动量观念、强弱指标与移动平均线的优点，在计算过程中主要研究高低价位与收市价的关系，反映价格走势的强弱和超买超卖现象。在市场短期超买超卖的预测方面又较敏感。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#jlhb-%E7%BB%9D%E8%B7%AF%E8%88%AA%E6%A0%87
#http://www.360doc.com/content/10/1128/21/235269_73250842.shtml
#本文件：主要对JLHB进行回测，需要包含收盘价['close']、最高价['high']、最低价['low']
#测试时间：20220314
"""
反趋势类选股指标。综合了动量观念、强弱指标与移动平均线的优点，在计算过程中主要研究高低价位与收市价的关系，反映价格走势的强弱和超买超卖现象。
在市场短期超买超卖的预测方面又较敏感。
VAR1 := (CLOSE - LLV(LOW,60))/(HHV(HIGH,60)-LLV(LOW,60))*80
B = SMA(VAR1,N,1)
VAR2 = SMA(B,M,1)
JLHB = IF(CROSS(B,VAR2) AND B<40,50,0)
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

#Y=SMA(X,N,M) 则 Y=(M*X+(N-M)*Y')/N，其中Y'表示上一周期Y值，N必须大于M。
def calc_SMA(X, N, M):
    """
    计算SMA(X,N,M)
    Y=SMA(X,N,M) 则 Y=(M*X+(N-M)*Y')/N，其中Y'表示上一周期Y值，N必须大于M。

    :param X Series SMA(X,N,M)的X
    :param N int SMA(X,N,M)参数N
    :param M int SMA(X,N,M)参数M

    :return Y list EMA(X，N)的值
    """
    Y = []
    Y.append(X[0])
    for i in range(1, len(X)):
        Y.append((M * X[i] + (N - M) * Y[i-1]) / N)

    return Y

#计算B, VAR2和绝路航标的值。
def calc_JLHB(mkt_data, n=7, m=5):
    """
    计算B, VAR2和绝路航标的值。
    VAR1 := (CLOSE - LLV(LOW,60))/(HHV(HIGH,60)-LLV(LOW,60))*80
    B = SMA(VAR1,N,1)
    VAR2 = SMA(B,M,1)
    JLHB = IF(CROSS(B,VAR2) AND B<40,50,0)

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含收盘价['close']、最高价['high']、最低价['low']
    :param n int B参数n
    :param m int VAR2参数M

    :return mkt_data DataFrame 新增3列,B, VAR2和绝路航标的值。
    """
    close = mkt_data['close']
    high = mkt_data['high']
    low = mkt_data['low']
    """计算指标"""
    LLV = low.rolling(60, min_periods=1).min()
    HHV = high.rolling(60, min_periods=1).min()
    VAR1 = (close - LLV) / (HHV-LLV) * 80
    B = calc_SMA(VAR1,n,1)
    VAR2 = calc_SMA(B, m, 1)
    """指标赋值"""
    mkt_data['B'] = B
    mkt_data['VAR2'] = VAR2
    temp1 = (mkt_data['VAR2'] > mkt_data['B'])
    temp2 = (mkt_data['VAR2'].shift(1) > mkt_data['B'].shift(1))
    mkt_data['JLHB'] = np.where((temp1==False)&(temp2==True)&(mkt_data['B']<40), 50, 0)

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
    B = mkt_data['B']
    VAR2 = mkt_data['VAR2']
    JLHB = mkt_data['JLHB']
    indi.line(dt, B, line_width=1, color='green')
    indi.line(dt, VAR2, line_width=1, color='yellow')
    indi.line(dt, JLHB, line_width=1, color='blue')

    # p = column(f1,f2,f3,f4)
    p = gridplot([[f1],
                  [indi]
                  ])
    show(p)

#运行部分
data = pd.read_csv('data/000016.csv')
data = calc_JLHB(data)
visualize_performance(data)

