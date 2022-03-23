# -*- coding: utf-8 -*-
#通达信MASS-梅斯线
#梅斯线（MASS），是唐纳德·道尔西（Donald Dorsey）累积股价波幅宽度之后，所设计的震荡曲线。本指标最主要的作用，在于寻找快速上涨股票或者极度弱势股票的重要趋势反转点。
#MASS指标是所有区间震荡指标中，风险系数最小的一个。股价高低点之间的价差波带忽而宽忽而窄，并且不断的重复循环。利用这种重复循环的波带，可以准确地预测股价的趋势反转点。一般市场上的技术指标通常不具备这方面的功能。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#mass-%E6%A2%85%E6%96%AF%E7%BA%BF
#http://cftsc.com/liangjiazhibiao/651.html
#本文件：主要对MASS进行回测，需要数据包含最高价['high']、最低价['low']、波动率['pct_chg']
#测试时间：20220318
"""
指标源代码
1.MASS:SUM(MA(HIGH-LOW,N1)/MA(MA(HIGH-LOW,N1),N1),N2);
2.MAMASS:MA(MASS,M);

用法注释：
1.MASS>27 后，随后又跌破26.5，此时股价若呈上涨状态，则卖出；
2.MASS<27 后，随后又跌破26.5，此时股价若呈下跌状态，则买进；
3.MASS<20 的行情，不宜进行投资。
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

#计算MASS和MAMASS 的值
def calc_MASS(mkt_data, N1=9, N2=25, M=6):
    """
    计算CR和MA1，MA2，MA3，MA4 的值
    1.MASS:SUM(MA(HIGH-LOW,N1)/MA(MA(HIGH-LOW,N1),N1),N2);
    2.MAMASS:MA(MASS,M);

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含最高价['high']、最低价['low']
    :param N1 int MASS参数N1
    :param N2 int MASS参数N2
    :param M int MAMASS参数M

    :return mkt_data DataFrame 新增2列，MASS和MAMASS的值
    """

    mkt_data['MASS'] = ((mkt_data['high'] - mkt_data['low']).rolling(N1,min_periods=1).mean() / ((mkt_data['high'] - mkt_data['low']).rolling(N1,min_periods=1).mean()).rolling(N1,min_periods=1).mean()).rolling(N2,min_periods=1).sum()
    mkt_data['MAMASS'] = (mkt_data['MASS']).rolling(M,min_periods=1).mean()

    return mkt_data

#计算信号
def calc_signal(mkt_data):
    """
    计算信号，1为买进，-1为卖出;
    1.MASS>27 后，随后又跌破26.5，此时股价若呈上涨状态，则卖出；
    2.MASS<27 后，随后又跌破26.5，此时股价若呈下跌状态，则买进；
    3.MASS<20 的行情，不宜进行投资。

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含MASS或MAMASS的值

    :return mkt_data DataFrame 新增1列['signal']
    """
    MASS = mkt_data['MASS']
    MAMASS = mkt_data['MAMASS']

    """ 计算信号 """
    signals = []
    for mass, pre_mass in zip(MASS, MASS.shift(1)):
        signal = None
        if (mass < 26.5) & (pre_mass > 27):
            signal = -1
        elif (mass < 26.5) & (pre_mass < 27):
            signal = 1
        signals.append(signal)

    """ 信号赋值 """
    mkt_data['signal'] = signals
    return mkt_data

#计算持仓
def calc_position(mkt_data):
    """
    计算持仓;

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含信号['signal']

    :return mkt_data DataFrame 新增1列['position']
    """
    #mkt_data['position'] = mkt_data['signal'].fillna(method='ffill').shift(1).fillna(0)
    mkt_data['position'] = mkt_data['signal'].fillna(method='ffill').shift(1).fillna(1)

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
    MASS = mkt_data['MASS']
    MAMASS = mkt_data['MAMASS']
    indi.line(dt, MASS, line_width=1, color='green')
    indi.line(dt, MAMASS, line_width=1, color='yellow')

    # p = column(f1,f2,f3,f4)
    p = gridplot([[f1],
                  [indi]
                  ])
    show(p)

#运行部分
data = pd.read_csv('data/000001.csv')
data = calc_MASS(data)
data = calc_signal(data)
visualize_performance(data)

