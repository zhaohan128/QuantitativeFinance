# -*- coding: utf-8 -*-
#通达信AMV-成本价均线
#成本价均线不同于一般移动平均线系统，成本价均线系统首次将成交量引入均线系统，充分提高均线系统的可靠性。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#amv-%E6%88%90%E6%9C%AC%E4%BB%B7%E5%9D%87%E7%BA%BF
#http://cftsc.com/quxiangzhibiao/583.html
#本文件：主要对AMV进行回测，需要数据包含收盘价['close']、开盘价['open']、成交量['volume']、波动率['pct_chg']
#测试时间：20220322
"""
指标源代码
AMV0:=VOL*(OPEN+CLOSE)/2;
AMV1:SUM(AMv0,M1)/SUM(VOL,M1);
AMV2:SUM(AMv0,M2)/SUM(VOL,M2);
AMV3:SUM(AMv0,M3)/SUM(VOL,M3);
AMV4:SUM(AMv0,M4)/SUM(VOL,M4);

用法注释：
成本价均线不同于一般移动平均线系统，成本价均线系统首次将成交量引入均线系统，充分提高均线系统的可靠性。
同样对于成本价均线可以使用月均线系统(5,10,20,250)和季均线系统(20,40,60,250),另外成本价均线还可以使用自身特有的均线系统(5,13,34,250),称为市场平均建仓成本均线，简称成本价均线。
在四个均线中参数为250的均线为年度均线,为行情支撑均线。
成本均线不容易造成虚假信号或骗线，比如某日股价无量暴涨，移动均线会大幅拉升，但成本均线却不会大幅上升，因为在无量的情况下市场持仓成本不会有太大的变化。
依据均线理论，当短期均线站在长期均线之上时叫多头排列，反之就叫空头排列。短期均线上穿长期均线叫金叉，短期均线下穿长期均线叫死叉。均线的多头排列是牛市的标志，空头排列是熊市的标志。
均线系统一直是市场广泛认可的简单而可靠的分析指标，其使用要点是尽量做多头排列的股票，回避空头排列的股票。
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

#计算AMV1、AMV2、AMV3、AMV4的值。
def calc_AMV(mkt_data, M1=5, M2=10, M3=20, M4=250):
    """
    计算AMV1、AMV2、AMV3、AMV4的值
    AMV0:=VOL*(OPEN+CLOSE)/2;
    AMV1:SUM(AMv0,M1)/SUM(VOL,M1);
    AMV2:SUM(AMv0,M2)/SUM(VOL,M2);
    AMV3:SUM(AMv0,M3)/SUM(VOL,M3);
    AMV4:SUM(AMv0,M4)/SUM(VOL,M4);

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含收盘价['close']、开盘价['open']、成交量['volume']
    :param M1 int AMV1参数M1
    :param M2 int AMV1参数M2
    :param M3 int AMV1参数M3
    :param M4 int AMV1参数M4

    :return mkt_data DataFrame 新增4列,AMV1、AMV2、AMV3、AMV4的值
    """
    VOL = mkt_data['volume']
    OPEN = mkt_data['open']
    CLOSE = mkt_data['close']
    AMV0 = VOL * (OPEN + CLOSE) / 2
    AMV1 = AMV0.rolling(M1).sum() / VOL.rolling(M1).sum()
    AMV2 = AMV0.rolling(M2).sum() / VOL.rolling(M2).sum()
    AMV3 = AMV0.rolling(M3).sum() / VOL.rolling(M3).sum()
    AMV4 = AMV0.rolling(M4).sum() / VOL.rolling(M4).sum()

    mkt_data['AMV1'] = AMV1
    mkt_data['AMV2'] = AMV2
    mkt_data['AMV3'] = AMV3
    mkt_data['AMV4'] = AMV4

    return mkt_data

#计算信号
def calc_signal(mkt_data):
    """
    计算信号，1为买进，-1为卖出;
    采用均线理论，金叉买入，死叉卖出；

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含AMV1、AMV2、AMV3、AMV4的值

    :return mkt_data DataFrame 新增1列['signal']
    """
    AMV1 = mkt_data['AMV1']
    AMV2 = mkt_data['AMV2']
    AMV3 = mkt_data['AMV3']
    AMV4 = mkt_data['AMV4']

    SHORT = AMV1
    LONG = AMV4

    """ 计算信号 """
    signals = []
    for short, pre_short, long, pre_long in zip(SHORT, SHORT.shift(1), LONG, LONG.shift(1)):
        signal = None
        if (short > long) & (pre_short < pre_long):
            signal = 1
        elif (short < long) & (pre_short > pre_long):
            signal = -1
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

#计算结果
def statistic_performance(mkt_data, r0=0.03, data_period=1440):
    """
    策略表现;

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含持仓['position']、波动率['pct_chg']

    :return mkt_data DataFrame  新增序列型特征，持仓收益，持仓胜负，累计持仓收益，回撤，超额收益
    :return performance_df DataFrame  新增数值型特征，'累计收益','多仓次数', '多仓胜率', '多仓平均持有期','空仓次数', '空仓胜率',
                                    '空仓平均持有期','日胜率', '最大回撤', '年化收益/最大回撤','年化收益', '年化标准差', '年化夏普'
    """
    position = mkt_data['position']

    """      序列型特征
        hold_r :      持仓收益
        hold_win :    持仓胜负
        hold_cumu_r : 累计持仓收益
        drawdown :    回撤
        ex_hold_r :   超额收益
    """
    hold_r = mkt_data['pct_chg'] / 100 * position
    hold_win = hold_r > 0
    hold_cumu_r = (1 + hold_r).cumprod() - 1
    drawdown = (hold_cumu_r.cummax() - hold_cumu_r) / (1 + hold_cumu_r).cummax()
    ex_hold_r = hold_r - r0 / (250 * 1440 / data_period)

    mkt_data['hold_r'] = hold_r
    mkt_data['hold_win'] = hold_win
    mkt_data['hold_cumu_r'] = hold_cumu_r
    mkt_data['drawdown'] = drawdown
    mkt_data['ex_hold_r'] = ex_hold_r

    """       数值型特征
        v_hold_cumu_r：         累计持仓收益
        v_pos_hold_times：      多仓开仓次数
        v_pos_hold_win_times：  多仓开仓盈利次数
        v_pos_hold_period：     多仓持有周期数
        v_pos_hold_win_period： 多仓持有盈利周期数
        v_neg_hold_times：      空仓开仓次数
        v_neg_hold_win_times：  空仓开仓盈利次数
        v_neg_hold_period：     空仓持有盈利周期数
        v_neg_hold_win_period： 空仓开仓次数
        v_hold_period：         持仓周期数（最后一笔未平仓订单也算）
        v_hold_win_period：     持仓盈利周期数（最后一笔未平仓订单也算）
        v_max_dd：              最大回撤
        v_annual_std：          年化标准差
        v_annual_ret：          年化收益
        v_sharpe：              夏普率
    """
    v_hold_cumu_r = hold_cumu_r.tolist()[-1]

    v_pos_hold_times = 0
    v_pos_hold_win_times = 0
    v_pos_hold_period = 0
    v_pos_hold_win_period = 0
    v_neg_hold_times = 0
    v_neg_hold_win_times = 0
    v_neg_hold_period = 0
    v_neg_hold_win_period = 0
    for w, r, pre_pos, pos in zip(hold_win, hold_r, position.shift(1), position):
        # 有换仓（先结算上一次持仓，再初始化本次持仓）
        if pre_pos != pos:
            # 判断pre_pos非空：若为空则是循环的第一次，此时无需结算，直接初始化持仓即可
            if pre_pos == pre_pos:
                # 结算上一次持仓
                if pre_pos > 0:
                    v_pos_hold_times += 1
                    v_pos_hold_period += tmp_hold_period
                    v_pos_hold_win_period += tmp_hold_win_period
                    if tmp_hold_r > 0:
                        v_pos_hold_win_times += 1
                elif pre_pos < 0:
                    v_neg_hold_times += 1
                    v_neg_hold_period += tmp_hold_period
                    v_neg_hold_win_period += tmp_hold_win_period
                    if tmp_hold_r > 0:
                        v_neg_hold_win_times += 1
            # 初始化本次持仓
            tmp_hold_r = r
            tmp_hold_period = 0
            tmp_hold_win_period = 0
        else:  # 未换仓
            if abs(pos) > 0:
                tmp_hold_period += 1
                if r > 0:
                    tmp_hold_win_period += 1
                if abs(r) > 0:
                    tmp_hold_r = (1 + tmp_hold_r) * (1 + r) - 1

    v_hold_period = (abs(position) > 0).sum()
    v_hold_win_period = (hold_r > 0).sum()
    v_max_dd = drawdown.max()
    v_annual_ret = pow(1 + v_hold_cumu_r,
                       1 / (data_period / 1440 * len(mkt_data) / 250)) - 1
    v_annual_std = ex_hold_r.std() * np.sqrt(250 * 1440 / data_period)
    v_sharpe = v_annual_ret / v_annual_std

    """ 生成Performance DataFrame """
    performance_cols = ['累计收益',
                        '多仓次数', '多仓胜率', '多仓平均持有期',
                        '空仓次数', '空仓胜率', '空仓平均持有期',
                        '日胜率', '最大回撤', '年化收益/最大回撤',
                        '年化收益', '年化标准差', '年化夏普'
                        ]
    performance_values = ['{:.2%}'.format(v_hold_cumu_r),
                          v_pos_hold_times, '{:.2%}'.format(v_pos_hold_win_times / v_pos_hold_times),
                          '{:.2f}'.format(v_pos_hold_period / v_pos_hold_times),
                          v_neg_hold_times, '{:.2%}'.format(v_neg_hold_win_times / v_neg_hold_times),
                          '{:.2f}'.format(v_neg_hold_period / v_neg_hold_times),
                          '{:.2%}'.format(v_hold_win_period / v_hold_period),
                          '{:.2%}'.format(v_max_dd),
                          '{:.2f}'.format(v_annual_ret / v_max_dd),
                          '{:.2%}'.format(v_annual_ret),
                          '{:.2%}'.format(v_annual_std),
                          '{:.2f}'.format(v_sharpe)
                          ]
    performance_df = pd.DataFrame(performance_values, index=performance_cols)
    return mkt_data, performance_df

#可视化
def visualize_performance(mkt_data):
    """
    可视化;

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含日期['date']、收盘价['close']、持仓['position']、
                                           持仓收益['hold_r']、累计持仓收益['hold_cumu_r']、回撤['drawdown']

    :return plot html 可交互式图
    """
    mkt_data['trade_datetime'] = mkt_data['date'].apply(lambda x: datetime.datetime.strptime(str(x), '%Y-%m-%d'))
    dt = mkt_data['trade_datetime']

    f1 = figure(height=300, width=700,
                sizing_mode='stretch_width',
                title='Target Trend',
                x_axis_type='datetime',
                x_axis_label="trade_datetime", y_axis_label="close")
    f2 = figure(height=200, sizing_mode='stretch_width',
                title='Position',
                x_axis_label="trade_datetime", y_axis_label="position",
                x_axis_type='datetime',
                x_range=f1.x_range)
    f3 = figure(height=200, sizing_mode='stretch_width',
                title='Return',
                x_axis_type='datetime',
                x_range=f1.x_range)
    f4 = figure(height=200, sizing_mode='stretch_width',
                title='Drawdown',
                x_axis_type='datetime',
                x_range=f1.x_range)

    indi = figure(height=200, sizing_mode='stretch_width',
                  title='Factor',
                  x_axis_type='datetime',
                  x_range=f1.x_range
                  )

    # 绘制行情
    close = mkt_data['close']
    cumu_hold_close = (mkt_data['hold_cumu_r'] + 1)
    f1.line(dt, close / close.tolist()[0], line_width=1)
    f1.line(dt, cumu_hold_close, line_width=1, color='red')

    # 绘制指标
    indi.line(dt, mkt_data['AMV1'], line_width=1, color='yellow')
    indi.line(dt, mkt_data['AMV2'], line_width=1, color='green')
    indi.line(dt, mkt_data['AMV3'], line_width=1, color='purple')
    indi.line(dt, mkt_data['AMV4'], line_width=1, color='blue')

    # 绘制仓位
    position = mkt_data['position']
    f2.step(dt, position)

    # 绘制收益
    hold_r = mkt_data['hold_r']
    f3.vbar(x=dt, top=hold_r)

    # 绘制回撤
    drawdown = mkt_data['drawdown']
    f4.line(dt, -drawdown, line_width=1)

    # p = column(f1,f2,f3,f4)
    p = gridplot([[f1],
                  [indi],
                  [f2],
                  [f3],
                  [f4]
                  ])
    show(p)

#运行部分
data = pd.read_csv('data/000300.csv')
data = calc_AMV(data)
data = calc_signal(data)
data = calc_position(data)
result, performance_df = statistic_performance(data)
visualize_performance(result)
print(performance_df)

