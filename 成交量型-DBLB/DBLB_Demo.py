# -*- coding: utf-8 -*-
#通达信DBLB-对比量比.对比量比(DBLB)指标是用于测度成交量放大程度或萎缩程度的指标。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#amo-%E6%88%90%E4%BA%A4%E9%87%91%E9%A2%9D
#http://www.yingjia360.com/cjl/2015-12-07/24118.html
#本文件：主要对DBLB进行回测，需要数据包含成交量['volume']
#测试时间：20220321
"""
指标公式：
GG=成交量(手)/昨日成交量(手)的N日累和
ZS=大盘成交量/昨日大盘成交量的N日累和
DBLB=GG/ZS
MADBLB=DBLB的M日简单移动平均

用法注释：
对比量比指标用于用于测度成交量放大程度或萎缩程度的指标。对比量比值越大，说明成交量较前期成交量放大程度越大，对比量比值越小，说明成交量较前期成交量萎缩程度越大，一般认为:
1.对比量比大于20可以认为成交量极度放大；
2.对比量比大于3,可以认为成交量显著放大；
3.对比量比小于0.2,可以认为成交量极度萎缩；
4.对比量比小于0.4,可以认为成交量显著萎缩。
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

#计算DBLB和MADBLB 的值
def calc_DBLB(mkt_data_gg, mkt_data_zs, N=5, M=5):
    """
    计算DBLB和MADBLB 的值
    GG=成交量(手)/昨日成交量(手)的N日累和
    ZS=大盘成交量/昨日大盘成交量的N日累和
    DBLB=GG/ZS
    MADBLB=DBLB的M日简单移动平均

    :param mkt_data_gg DataFrame 个股历史行情数据，日维度，需要包含成交量['volume']
    :param mkt_data_zs DataFrame 指数历史行情数据，日维度，需要包含成交量['volume']
    :param N int DBLB参数N
    :param M int MADBLB参数M

    :return mkt_data_gg DataFrame 新增2列，DBLB和MADBLB 的值
    """
    GG = mkt_data_gg['volume']/mkt_data_gg['volume'].shift(1).rolling(N).sum()
    ZS = mkt_data_zs['volume']/mkt_data_zs['volume'].shift(1).rolling(N).sum()
    DBLB = GG / ZS

    mkt_data_gg['DBLB'] = DBLB
    mkt_data_gg['MADBLB'] = mkt_data_gg['DBLB'].rolling(M).mean()

    return mkt_data_gg

#可视化
def visualize_performance(mkt_data, mkt_data_zs):
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
    close_zs = mkt_data_zs['close']
    f1.line(dt, close / close.tolist()[0], line_width=1)
    f1.line(dt, close_zs / close_zs.tolist()[0], line_width=1, color='yellow')

    # 绘制指标
    indi.line(dt, mkt_data['DBLB'], line_width=1, color='green')
    indi.line(dt, mkt_data['MADBLB'], line_width=1, color='yellow')

    # p = column(f1,f2,f3,f4)
    p = gridplot([[f1],
                  [indi]
                  ])
    show(p)

#运行部分
data_zs = pd.read_csv('data/000001.csv')
data_gg = pd.read_csv('data/000016.csv')

data = calc_DBLB(data_gg, data_zs)
visualize_performance(data_gg, data_zs)

