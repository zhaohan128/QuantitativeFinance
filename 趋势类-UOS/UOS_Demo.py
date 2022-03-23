# -*- coding: utf-8 -*-
#通达信UOS-终极指标
#终极波动（UOS）指标，亦称终极指标，由拉里·威廉姆斯（Larry Williams）所创。他认为现行使用的各种振荡指标，对于周期参数的选择相当敏感。
#不同市况、不同参数设定的振荡指标，产生的结果截然不同。因此，选择最佳的参数组合，成为使用振荡指标之前最重要的一道手续。
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#uos-%E7%BB%88%E6%9E%81%E6%8C%87%E6%A0%87
#http://cftsc.com/quxiangzhibiao/590.html
#本文件：主要对UOS进行回测，需要数据包含收盘价['close']、最高价['high']、最低价['low']、波动率['pct_chg']
#测试时间：20220315
"""
TH:=MAX(HIGH,REF(CLOSE,1));
TL:=MIN(LOW,REF(CLOSE,1));
ACC1:=SUM(CLOSE-TL,N1)/SUM(TH-TL,N1);
ACC2:=SUM(CLOSE-TL,N2)/SUM(TH-TL,N2);
ACC3:=SUM(CLOSE-TL,N3)/SUM(TH-TL,N3);
UOS:(ACC1*N2*N3+ACC2*N1*N3+ACC3*N1*N2)*100/(N1*N2+N1*N3+N2*N3);
MAUOS:EMA(UOS,M);

用法注释：
1.UOS 上升至50～70的间，而后向下跌破其Ｎ字曲线低点时，为短线卖点；
2.UOS 上升超过70以上，而后向下跌破70时，为中线卖点；
3.UOS 下跌至45以下，而后向上突破其Ｎ字曲线高点时，为短线买点；
4.UOS 下跌至35以下，产生一底比一底高的背离现象时，为底部特征；
5.以上各项数据会因个股不同而略有不同，请利用参考线自行修正。
"""

#加载库
import numpy as np
import pandas as pd
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span

def calc_EMA(X,N):
    """
    计算指数平均数指标(EMA)
    Y = EMA(X，N)，则Y =［2 * X + (N - 1) * Y’］ / (N + 1)，其中Y’表示上一周期的Y值。

    :param X Series EMA(X，N)的X
    :param N int EMA(X，N)参数N

    :return Y list EMA(X，N)的值
    """
    Y = []
    Y.append(X[0])
    for i in range(1, len(X)):
        Y.append((2 * X[i] + (N - 1) * Y[i-1]) / (N + 1))

    return Y

#计算终极指标和MAUOS的值
def calc_UOS(mkt_data, n1=7, n2=14, n3=28, m=6):
    """
    计算终极指标UOS和MAUOS的值
    TH:=MAX(HIGH,REF(CLOSE,1));
    TL:=MIN(LOW,REF(CLOSE,1));
    ACC1:=SUM(CLOSE-TL,N1)/SUM(TH-TL,N1);
    ACC2:=SUM(CLOSE-TL,N2)/SUM(TH-TL,N2);
    ACC3:=SUM(CLOSE-TL,N3)/SUM(TH-TL,N3);
    UOS:(ACC1*N2*N3+ACC2*N1*N3+ACC3*N1*N2)*100/(N1*N2+N1*N3+N2*N3);
    MAUOS:EMA(UOS,M);

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含收盘价['close']、最高价['high']、最低价['low']
    :param n1 int DIF参数n1
    :param n2 int DIF参数n2
    :param m int DEM参数M

    :return mkt_data DataFrame 新增2列,终极指标和MAUOS的值
    """
    TH = pd.concat([mkt_data['high'],mkt_data['close'].shift(1)], axis=1).max(axis=1)
    TL = pd.concat([mkt_data['low'], mkt_data['close'].shift(1)], axis=1).max(axis=1)
    CLOSE = mkt_data['close']
    ACC1 = (CLOSE-TL).rolling(n1).sum() / (TH-TL).rolling(n1).sum()
    ACC2 = (CLOSE-TL).rolling(n2).sum() / (TH-TL).rolling(n2).sum()
    ACC3 = (CLOSE-TL).rolling(n3).sum() / (TH-TL).rolling(n3).sum()
    """计算指标"""
    UOS = (ACC1 * n2 * n3 + ACC2 * n1 * n3 + ACC3 * n1 * n2) * 100 / (n1 * n2 + n1 * n3 + n2 * n3)
    MAUOS = calc_EMA(UOS,m)
    """指标赋值"""
    mkt_data['UOS'] = UOS
    mkt_data['MAUOS'] = MAUOS

    return mkt_data

#计算信号
def calc_signal(mkt_data):
    """
    计算信号，1为买进，-1为卖出;
    1.UOS 上升至50～70的间，而后向下跌破其Ｎ字曲线低点时，为短线卖点；
    2.UOS 上升超过70以上，而后向下跌破70时，为中线卖点；
    3.UOS 下跌至45以下，而后向上突破其Ｎ字曲线高点时，为短线买点；
    4.UOS 下跌至35以下，产生一底比一底高的背离现象时，为底部特征；
    5.以上各项数据会因个股不同而略有不同，请利用参考线自行修正。

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含DIF, DEA和OSC的值

    :return mkt_data DataFrame 新增1列['signal']
    """
    UOS = mkt_data['UOS']
    MAUOS = mkt_data['MAUOS']

    """ 计算信号 """
    signals = []
    for uos, pre_uos in zip(UOS, UOS.shift(1)):
        signal = None
        if (uos > 45) & (pre_uos < 45):
            signal = 1
        elif (uos < 65) & (pre_uos > 65):
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
    UOS = mkt_data['UOS']
    MAUOS = mkt_data['MAUOS']
    indi.line(dt, UOS, line_width=1, color='yellow')
    indi.line(dt, MAUOS, line_width=1, color='blue')

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
data = pd.read_csv('data/000001.csv')
data = calc_UOS(data)
data = calc_signal(data)
data = calc_position(data)
result_daily, performance_df = statistic_performance(data)
visualize_performance(result_daily)
print(performance_df)

