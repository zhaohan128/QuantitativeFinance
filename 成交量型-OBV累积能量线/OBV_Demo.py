# -*- coding: utf-8 -*-
#通达信OBV-累积能量线
#累积能量线（英文on-balance volume, OBV）是一个广为运用的股票技术指标，它反映了股票价格变动与成交量的关系。OBV是由著名的股市技术分析大师Joe Granville最早推广使用的。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#obv-%E7%B4%AF%E7%A7%AF%E8%83%BD%E9%87%8F%E7%BA%BF
#http://www.danglanglang.com/gupiao/1297
#本文件：主要对OBV进行回测，需要数据包含收盘价['close']、成交量['volume']
#测试时间：20220321
"""
指标公式：
如果今天的收盘价高于昨天的收盘价，那么OBV＝昨天的OBV＋今天的成交量
如果今天的收盘价低于昨天的收盘价，那么OBV＝昨天的OBV－今天的成交量
如果今天的收盘价等于昨天的收盘价，那么OBV＝昨天的OBV

用法注释：
1.股价一顶比一顶高，而OBV 一顶比一顶低，暗示头部即将形成；
2.股价一底比一底低，而OBV 一底比一底高，暗示底部即将形成；
3.OBV 突破其Ｎ字形波动的高点次数达5 次时，为短线卖点；
4.OBV 跌破其Ｎ字形波动的低点次数达5 次时，为短线买点；
5.OBV 与ADVOL、PVT、WAD、ADL同属一组指标群，使用时应综合研判。
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

#计算OBV 的值
def calc_OBV(mkt_data, M=5):
    """
    计算OBV 的值
    如果今天的收盘价高于昨天的收盘价，那么OBV＝昨天的OBV＋今天的成交量
    如果今天的收盘价低于昨天的收盘价，那么OBV＝昨天的OBV－今天的成交量
    如果今天的收盘价等于昨天的收盘价，那么OBV＝昨天的OBV

    :param mkt_data DataFrame 个股历史行情数据，日维度，需要包含收盘价['close']、成交量['volume']
    :param M int MAHSL参数M

    :return mkt_data DataFrame 新增1列，OBV 的值
    """

    def obv(close, volume):
        obv=pd.Series(index=close.index)
        obv[0] = volume[0]
        for i in range(1,len(close)):
            if close[i] > close[i-1]:
                obv[i] = obv[i-1] + volume[i]
            elif close[i] < close[i-1]:
                obv[i] = obv[i-1] - volume[i]
            else:
                obv[i] = obv[i - 1]
        return obv

    mkt_data['OBV'] = obv(mkt_data['close'], mkt_data['volume'])

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
    indi.line(dt, mkt_data['OBV'], line_width=1, color='green')

    # p = column(f1,f2,f3,f4)
    p = gridplot([[f1],
                  [indi]
                  ])
    show(p)

#运行部分
data = pd.read_csv('data/000001.csv')
data = calc_OBV(data)
visualize_performance(data)

