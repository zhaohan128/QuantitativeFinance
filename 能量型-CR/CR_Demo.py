# -*- coding: utf-8 -*-
#通达信CR-带状能量线
#CR能够测量价格动量的潜能，又能测量人气的热度，同时还能显示压力带和支撑带。CR指标的计算公式和BR相同， 只是把公式中昨天的收盘价改成昨天的中间价。
#CR能够测量人气的热度， 能够测量价格动量的潜能； CR能够显示压力带和支撑带， 功能作用上， 可以补充BRAR的不足。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#cr-%E5%B8%A6%E7%8A%B6%E8%83%BD%E9%87%8F%E7%BA%BF
#本文件：主要对CR进行回测，需要数据包含最高价['high']、最低价['low']、波动率['pct_chg']
#测试时间：20220316
"""
指标源代码
CR:SUM(MAX(0,HIGH-REF(MID,1)),M1)/SUM(MAX(0,REF(MID,1)-LOW),M1)*100;
MA1 = MA(CR,M1);
MA2 = MA(CR,M2);
MA3 = MA(CR,M3);
MA4 = MA(CR,M4);

用法注释：
1.CR>400时，其10日平均线向下滑落，视为卖出信号；CR<40买进；
2.CR 由高点下滑至其四条平均线下方时，股价容易形成短期底部；
3.CR 由下往上连续突破其四条平均线时，为强势买进点；
4.CR 除了预测价格的外，最大的作用在于预测时间；
5.BR、AR、CR、VR 四者合为一组指标群，须综合搭配使用。
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

#计算CR和MA1，MA2，MA3，MA4 的值
def calc_CR(mkt_data, N=26, M1=10, M2=20, M3=40, M4=62):
    """
    计算CR和MA1，MA2，MA3，MA4 的值
    CR:SUM(MAX(0,HIGH-REF(MID,1)),M1)/SUM(MAX(0,REF(MID,1)-LOW),M1)*100;
    MA1 = MA(CR,M1);
    MA2 = MA(CR,M2);
    MA3 = MA(CR,M3);
    MA4 = MA(CR,M4);

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含最高价['high']、最低价['low']
    :param n int VPT参数n
    :param m int MAVPT参数M

    :return mkt_data DataFrame 新增6列，中间价格['mid']，CR和MA1，MA2，MA3，MA4 的值
    """

    def quzheng(x):
        z = x if x > 0 else 0
        return z

    mkt_data['mid'] = (mkt_data['high'] + mkt_data['low']) / 2
    mkt_data['CR'] = 100 * (mkt_data['high'] - mkt_data['mid'].shift(1)).apply(quzheng).rolling(N).sum() / (mkt_data['mid'].shift(1) - mkt_data['low']).apply(quzheng).rolling(N).sum()

    mkt_data['MA1'] = mkt_data['CR'].rolling(M1).mean()
    mkt_data['MA2'] = mkt_data['CR'].rolling(M2).mean()
    mkt_data['MA3'] = mkt_data['CR'].rolling(M3).mean()
    mkt_data['MA4'] = mkt_data['CR'].rolling(M4).mean()

    return mkt_data

#计算信号
def calc_signal(mkt_data):
    """
    计算信号，1为买进，-1为卖出;
    1.CR>400时，其10日平均线向下滑落，视为卖出信号；CR<40买进；
    2.CR 由高点下滑至其四条平均线下方时，股价容易形成短期底部；
    3.CR 由下往上连续突破其四条平均线时，为强势买进点；
    4.CR 除了预测价格的外，最大的作用在于预测时间；
    5.BR、AR、CR、VR 四者合为一组指标群，须综合搭配使用。

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含DIF, DEA和OSC的值

    :return mkt_data DataFrame 新增1列['signal']
    """
    CR = mkt_data['CR']
    MA1 = mkt_data['MA1']
    MAmax = mkt_data[['MA1','MA2','MA3','MA4']].max(axis=1)
    MAmin = mkt_data[['MA1','MA2','MA3','MA4']].min(axis=1)

    """ 计算信号 """
    signals = [None]
    for i in range(1,len(mkt_data)):
        signal = None
        if CR.loc[i] < 40:
            signal = 1
        elif (CR.loc[i] > 400) & (CR.loc[i] < CR.loc[i-1]):
            signal = -1
        elif (CR.loc[i] < MAmin.loc[i]) & (CR.loc[i-1] > MAmax.loc[i-1]):
            signal = -1
        elif (CR.loc[i] > MAmax.loc[i]) & (CR.loc[i-1] < MAmin.loc[i-1]):
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
    CR = mkt_data['CR']
    MA1 = mkt_data['MA1']
    indi.line(dt, CR, line_width=1, color='yellow')
    indi.line(dt, MA1, line_width=1, color='blue')

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
data = calc_CR(data)
data = calc_signal(data)
data = calc_position(data)
result_daily, performance_df = statistic_performance(data)
visualize_performance(result_daily)
print(performance_df)

