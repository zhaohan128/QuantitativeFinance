# -*- coding: utf-8 -*-
#通达信AMO-成交金额。成交金额AMO是表示每日已成交证券金额的数值。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#amo-%E6%88%90%E4%BA%A4%E9%87%91%E9%A2%9D
#http://www.yingjia360.com/cjl/2015-12-07/24118.html
#本文件：主要对AMO进行回测，需要数据包含收盘价['amount']
#测试时间：20220321
"""
用法注释：
1.成交金额大，代表交投热络，可界定为热门股；
2.底部起涨点出现大成交金额，代表攻击量；
3.头部地区出现大成交金额，代表出货量；
4.观察成交金额的变化，比观察成交手数更具意义，因为成交手数并未反应股价的涨跌的后所应支出的实际金额。
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

#计算AMOW，AMO1和AMO2 的值
def calc_AMO(mkt_data, M1=5, M2=10):
    """
    计算AMOW，AMO1和AMO2 的值

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含成交额['amount']
    :param M1 int AMO1参数M1
    :param M2 int AMO2参数M2

    :return mkt_data DataFrame 新增3列，AMOW，AMO1和AMO2 的值
    """

    mkt_data['AMOW'] = mkt_data['amount']
    mkt_data['AMO1'] = mkt_data['AMOW'].rolling(M1).mean()
    mkt_data['AMO2'] = mkt_data['AMOW'].rolling(M2).mean()

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
    indi.line(dt, mkt_data['AMO1'], line_width=1, color='green')
    indi.line(dt, mkt_data['AMO2'], line_width=1, color='yellow')
    indi.vbar(dt, top=mkt_data['AMOW'], width=0.9)

    # p = column(f1,f2,f3,f4)
    p = gridplot([[f1],
                  [indi]
                  ])
    show(p)

#运行部分
data = pd.read_csv('data/000001.csv')
data = calc_AMO(data)
visualize_performance(data)

