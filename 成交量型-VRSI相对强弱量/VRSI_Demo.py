# -*- coding: utf-8 -*-
#通达信VRSI-相对强弱量
#相对强弱量指标又名VRSI指标，是通过反映股价变动的四个元素：上涨的天数、下跌的天数、成交量增加幅度、成交量减少幅度来研判量能的趋势，预测市场供求关系和买卖力道，是属于量能反趋向指标之一。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#vrsi-%E7%9B%B8%E5%AF%B9%E5%BC%BA%E5%BC%B1%E9%87%8F
#http://cftsc.com/liangjiazhibiao/650.html#:~:text=%E7%9B%B8%E5%AF%B9%E5%BC%BA%E5%BC%B1%E9%87%8F%E6%8C%87%E6%A0%87%E5%8F%88,%E5%8F%8D%E8%B6%8B%E5%90%91%E6%8C%87%E6%A0%87%E4%B9%8B%E4%B8%80%E3%80%82
#本文件：主要对VRSI进行回测，需要数据包含成交量['volume']
#测试时间：20220321
"""
指标源代码
VRSI(N)=SMA(MAX(VOL-REF(VOL,1),0),N,1)/SMA(ABS(VOL-REF(VOL,1)),N,1)*100

用法注释：
 1)VRSI>20为超买；VRSI<20为超卖
 2)VRSI以50为中轴线,大于50视为多头行情,小于50视为空头行情
 3)VRSI在80以上形成M头或头肩顶形态时,视为向下反转信号
 4)VRSI在20以上形成W头或头肩底形态时,视为向上反转信号
 5)VRSI向上突破其高点连线时,买进；VRSI向下跌破其低点连线时,卖出。
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

#计算VRSI1，VRSI2和VRSI3 的值
def calc_VRSI(mkt_data, N1=6, N2=12, N3=24):
    """
    计算RSI1，VRSI2和VRSI3 的值
    VRSI(N)=SMA(MAX(VOL-REF(VOL,1),0),N,1)/SMA(ABS(VOL-REF(VOL,1)),N,1)*100

    :param mkt_data DataFrame 个股历史行情数据，日维度，需要包含成交量['volume']
    :param N1 int VRSI1参数N1
    :param N2 int VRSI2参数N2
    :param N3 int VRSI3参数N3

    :return mkt_data DataFrame 新增3列，VRSI1，VRSI2和VRSI3 的值
    """
    def VRSI(volume,N):
        def quzheng(x):
            z = x if x > 0 else 0
            return z

        vol_chg = volume - volume.shift(1)
        vrsi = 100 * vol_chg.apply(quzheng).rolling(N).mean()/vol_chg.apply(abs).rolling(N).mean()

        return vrsi

    mkt_data['VRSI1'] = VRSI(mkt_data['volume'],N1)
    mkt_data['VRSI2'] = VRSI(mkt_data['volume'],N2)
    mkt_data['VRSI3'] = VRSI(mkt_data['volume'],N3)

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
    indi.line(dt, mkt_data['VRSI1'], line_width=1, color='green')
    indi.line(dt, mkt_data['VRSI2'], line_width=1, color='yellow')
    indi.line(dt, mkt_data['VRSI3'], line_width=1, color='purple')

    # p = column(f1,f2,f3,f4)
    p = gridplot([[f1],
                  [indi]
                  ])
    show(p)

#运行部分
data = pd.read_csv('data/000001.csv')
data = calc_VRSI(data)
visualize_performance(data)

