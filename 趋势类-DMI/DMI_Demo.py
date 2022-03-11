# -*- coding: utf-8 -*-
#国泰君安DMI - 趋向指标
#DMI指标又叫趋向指标，是美国技术分析大师威尔斯.威尔德通过分析股价在涨跌过程中买卖双方的力量变化而去判断趋势所创造出来的一种技术指标。
#DMI指标包含两组指标，分别是多空指标（多方指标PDI和空方指标MDI）和趋向指标（ADX和ADXR）。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#dmi-%E8%B6%8B%E5%90%91%E6%8C%87%E6%A0%87
#https://zhuanlan.zhihu.com/p/407021533
#本文件：主要对DMI进行回测，需要数据包含收盘价['close']、最高价['high']、最低价['low']、波动率['pct_chg']
#测试时间：20220310
"""
用法：市场行情趋向明显时，指标效果理想。
PDI(上升方向线) MDI(下降方向线) ADX(趋向平均值)
1.PDI线从下向上突破MDI线，显示有新多头进场，为买进信号；
2.PDI线从上向下跌破MDI线，显示有新空头进场，为卖出信号；
3.ADX值持续高于前一日时，市场行情将维持原趋势；
4.ADX值递减，降到20以下，且横向行进时，市场气氛为盘整；
5.ADX值从上升倾向转为下降时，表明行情即将反转。
参数：N　统计天数； M 间隔天数，一般为14、6
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span


def calc_DMI(mkt_data, n=14, m=6):
    """
    计算指标，
    TR0:= SUM(MAX(MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1))),ABS(LOW-REF(CLOSE,1))),N);
    HD := HIGH-REF(HIGH,1);
    LD := REF(LOW,1)-LOW;
    DMP:= SUM(IF(HD>0 AND HD>LD,HD,0),N);
    DMM:= SUM(IF(LD>0 AND LD>HD,LD,0),N);
    PDI: DMP*100/TR0;MDI: DMM*100/TR0;    #DIP DIN
    ADX: MA(ABS(MDI-PDI)/(MDI+PDI)*100,M);
    ADXR:(ADX+REF(ADX,M))/2;

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含收盘价['close']、最高价['high']、最低价['low']
    :param n int PDI, MDI参数N
    :param m int ADX参数M

    :return mkt_data DataFrame 新增4列, PDI, MDI, ADX, ADXR的值
    """
    # 计算
    high = mkt_data['high']
    low = mkt_data['low']
    close = mkt_data['close']
    """ 计算指标 """
    DMIp = high.rolling(2).max() - high.shift(1)
    DMIn = low.shift(1) - low.rolling(2).min()
    # DMIp和DMIn中只能有一个>0，选大的
    DMIp = DMIp*(DMIp>=DMIn)
    DMIn = DMIn*(DMIp<DMIn)
    TR = pd.concat([high-low, abs(high-close.shift(1)), abs(low-close.shift(1))], axis=1).max(axis=1)
    #TR = pd.concat([high, close.shift(1)], axis=1).max(axis=1) - pd.concat([low, close.shift(1)], axis=1).min(axis=1)
    PDI = DMIp.rolling(n).sum() * 100 / TR.rolling(n).sum()
    MDI = DMIn.rolling(n).sum() * 100 / TR.rolling(n).sum()
    DX = abs(PDI-MDI)/(PDI+MDI) * 100
    ADX = DX.rolling(m).mean()
    ADXR = (ADX + ADX.shift(m)) / 2
    """ 指标赋值 """
    mkt_data['PDI'] = PDI
    mkt_data['MDI'] = MDI
    mkt_data['ADX'] = ADX
    mkt_data['ADXR'] = ADXR
    return mkt_data

#计算信号
def calc_signal(mkt_data):
    """
    比较DIF和DIFMA，计算信号，1为买进，-1为卖出;
    1.PDI线从下向上突破MDI线，显示有新多头进场，为买进信号；
    2.PDI线从上向下跌破MDI线，显示有新空头进场，为卖出信号；

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含['PDI']['MDI']

    :return mkt_data DataFrame 新增1列['signal']
    """
    PDI = mkt_data['PDI']
    MDI = mkt_data['MDI']
    signals = []
    for dip, din, pre_dip, pre_din in zip(PDI, MDI, PDI.shift(1), MDI.shift(1)):
        signal = None
        if pre_dip < pre_din and dip >= din:
            signal = 1
        elif pre_dip >= pre_din and dip < din:
            signal = -1
        signals.append(signal)
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
    PDI = mkt_data['PDI']
    MDI = mkt_data['MDI']
    indi.line(dt, PDI, line_width=1, color='red')
    indi.line(dt, MDI, line_width=1, color='blue')

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
data = calc_DMI(data, n=14, m=6)
data = calc_signal(data)
data = calc_position(data)
result_daily, performance_df = statistic_performance(data)
visualize_performance(result_daily)
print(performance_df)

