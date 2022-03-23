# -*- coding: utf-8 -*-
#通达信DBQRV-对比强弱量
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#dbqrv-%E5%AF%B9%E6%AF%94%E5%BC%BA%E5%BC%B1%E9%87%8F
#http://rumen.southmoney.com/zhibiao/DBQRV/111896.html
#本文件：主要对DBQRV进行回测，需要数据包含成交量['volume']
#测试时间：20220321
"""
指标公式：
ZS：（INDEXV-REF（INDEXV，N））/REF（INDEXV，N）;
GG：（VOL-REF（VOL，N））/REF（VOL，N）;
公式翻译为：
输出ZS：（大盘的成交量-N日前的大盘的成交量）/N日前的大盘的成交量
输出GG：（成交量（手）-N日前的成交量（手））/N日前的成交量（手）

用法注释：
对比强弱量指标包含有两条指标线,一条是对应指数量的强弱线。另外一条是个股成交量的强弱线。
当个股强弱线与指数强弱线发生金叉时，表明个股成交活跃过大盘。当个股强弱线与指数强弱线发生死叉时，表明个股活跃度开始弱于大盘。
对比强弱量指标也是一个短线指标。

注意：此指标使用到了大盘的数据，所以需要下载完整的日线数据,否则显示可能不正确
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

#计算ZS和GG 的值
def calc_DBQRV(mkt_data_gg, mkt_data_zs, N=5):
    """
    计算ZS和GG 的值
    ZS：（INDEXV-REF（INDEXV，N））/REF（INDEXV，N）;
    GG：（VOL-REF（VOL，N））/REF（VOL，N）;

    :param mkt_data_gg DataFrame 个股历史行情数据，日维度，需要包含成交量['volume']
    :param mkt_data_zs DataFrame 指数历史行情数据，日维度，需要包含成交量['volume']
    :param N int 参数N

    :return mkt_data_gg DataFrame 新增2列，ZS和GG 的值
    """
    GG = (mkt_data_gg['volume']-mkt_data_gg['volume'].shift(N))/mkt_data_gg['volume'].shift(N)
    ZS = (mkt_data_zs['volume']-mkt_data_zs['volume'].shift(N))/mkt_data_zs['volume'].shift(N)

    mkt_data_gg['ZS'] = ZS
    mkt_data_gg['GG'] = GG

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
    indi.line(dt, mkt_data['GG'], line_width=1, color='green')
    indi.line(dt, mkt_data['ZS'], line_width=1, color='yellow')

    # p = column(f1,f2,f3,f4)
    p = gridplot([[f1],
                  [indi]
                  ])
    show(p)

#运行部分
data_zs = pd.read_csv('data/000001.csv')
data_gg = pd.read_csv('data/000016.csv')

data = calc_DBQRV(data_gg, data_zs)
visualize_performance(data_gg, data_zs)

