# -*- coding: utf-8 -*-
#通达信VPT-量价曲线
#量价曲线VPT（英文：volume price trend）是一个重要的股票技术指标，它反映了成交量与价格之间的关系。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#vpt-%E9%87%8F%E4%BB%B7%E6%9B%B2%E7%BA%BF
#https://zhidao.baidu.com/question/461969533005870805.html
#本文件：主要对VPT进行回测，需要数据包含收盘价['close']、成交量['volume']、波动率['pct_chg']
#测试时间：20220315
"""
VPT:SUM(VOL*(CLOSE-REF(CLOSE,1))/REF(CLOSE,1),N);
MAVPT:MA(VPT,M)

用法注释：
1.VPT 由下往上穿越0 轴时，为买进信号；
2.VPT 由上往下穿越0 轴时，为卖出信号；
3.股价一顶比一顶高，VPT 一顶比一顶低时，暗示股价将反转下跌；
4.股价一底比一底低，VPT 一底比一底高时，暗示股价将反转上涨；
5.VPT 可搭配EMV 和WVAD指标使用效果更佳。
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

#计算VPT 和 MAVPT 的值
def calc_VPT(mkt_data, n=51, m=6):
    """
    计算VPT 和 MAVPT 的值
    VPT:SUM(VOL*(CLOSE-REF(CLOSE,1))/REF(CLOSE,1),N);
    MAVPT:MA(VPT,M)

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含收盘价['close']、成交量['volume']
    :param n int VPT参数n
    :param m int MAVPT参数M

    :return mkt_data DataFrame 新增2列,VPT 和 MAVPT 的值
    """
    """计算指标"""
    VPT = (mkt_data['volume'] * (mkt_data['close']-mkt_data['close'].shift(1)) / mkt_data['close'].shift(1)).rolling(n).sum()
    MAVPT = VPT.rolling(m).mean()
    """指标赋值"""
    mkt_data['VPT'] = VPT
    mkt_data['MAVPT'] = MAVPT

    return mkt_data

#计算信号
def calc_signal(mkt_data):
    """
    计算信号，1为买进，-1为卖出;
    1.VPT 由下往上穿越0 轴时，为买进信号；
    2.VPT 由上往下穿越0 轴时，为卖出信号；
    3.股价一顶比一顶高，VPT 一顶比一顶低时，暗示股价将反转下跌；
    4.股价一底比一底低，VPT 一底比一底高时，暗示股价将反转上涨；
    5.VPT 可搭配EMV 和WVAD指标使用效果更佳。

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含DIF, DEA和OSC的值

    :return mkt_data DataFrame 新增1列['signal']
    """
    VPT = mkt_data['VPT']
    MAVPT = mkt_data['MAVPT']

    """ 计算信号 """
    signals = []
    for vpt, pre_vpt in zip(VPT, VPT.shift(1)):
        signal = None
        if (vpt > 0) & (pre_vpt < 0):
            signal = 1
        elif (vpt < 0) & (pre_vpt > 0):
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
    VPT = mkt_data['VPT']
    MAVPT = mkt_data['MAVPT']
    indi.line(dt, VPT, line_width=1, color='yellow')
    indi.line(dt, MAVPT, line_width=1, color='blue')

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
data = calc_VPT(data)
data = calc_signal(data)
data = calc_position(data)
result_daily, performance_df = statistic_performance(data)
visualize_performance(result_daily)
print(performance_df)

