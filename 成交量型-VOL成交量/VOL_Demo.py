# -*- coding: utf-8 -*-
#通达信VOL-成交量
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#vol-%E6%88%90%E4%BA%A4%E9%87%8F
#本文件：主要对VOL进行回测，需要数据包含成交量['volume']
#测试时间：20220321
"""
用法注释：
1.成交量大，代表交投热络，可界定为热门股；
2.底部起涨点出现大成交量(成交手数)，代表攻击量；
3.头部地区出现大成交量(成交手数)，代表出货量；
4.观察成交金额的变化，比观察成交手数更具意义，因为成交手数并未反应股价的涨跌的后所应支出的实际金额。
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

#计算VOL 和 MAVOL 的值
def calc_VOL(mkt_data, M=5):
    """
    计算VOL 和 MAVOL 的值

    :param mkt_data DataFrame 个股历史行情数据，日维度，需要包含成交量['volume']
    :param M int MAHSL参数M

    :return mkt_data DataFrame 新增2列，VOL 和 MAVOL 的值
    """

    mkt_data['VOL'] = mkt_data['volume']
    mkt_data['MAVOL'] = mkt_data['VOL'].rolling(M).mean()

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
    indi.line(dt, mkt_data['VOL'], line_width=1, color='green')
    indi.line(dt, mkt_data['MAVOL'], line_width=1, color='yellow')

    # p = column(f1,f2,f3,f4)
    p = gridplot([[f1],
                  [indi]
                  ])
    show(p)

#运行部分
data = pd.read_csv('data/000001.csv')
data = calc_VOL(data)
visualize_performance(data)

