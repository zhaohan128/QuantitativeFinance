# -*- coding: utf-8 -*-
# https://gitee.com/xuezhihuan/my-over-sea-cloud/tree/master/quantitative_research_report
# 2022/02/15 01:00

# 导入库
import numpy as np
import pandas as pd
import pandas_ta as ta
import datetime

from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span
# output_notebook()

data = pd.read_csv("000300.SH.csv")
print(data)
daily_300 = data.copy()
print(daily_300)
pd.DataFrame().ta.indicators()

def calc_ADX(mkt_data, n=14):
    high = mkt_data['high']
    low = mkt_data['low']
    close = mkt_data['close']
    """ 计算指标 """
    # 1. 自行计算，DIp, DIn是用的SMA
    DMIp = high.rolling(2).max() - high.shift(1)
    DMIn = low.shift(1) - low.rolling(2).min()
    # DMIp和DMIn中只能有一个>0，选大的
    DMIp = DMIp*(DMIp>=DMIn)
    DMIn = DMIn*(DMIp<DMIn)
    TR = pd.concat([high, close.shift(1)], axis=1).max(axis=1) - pd.concat([low, close.shift(1)], axis=1).min(axis=1)
    # TR = abs(close - close.shift(1))
    DIp = DMIp.rolling(n).sum() / TR.rolling(n).sum()
    DIn = DMIn.rolling(n).sum() / TR.rolling(n).sum()
    # DIp = DMIp.rolling(n).sum() / abs(close - close.shift(n))
    # DIn = DMIn.rolling(n).sum() / abs(close - close.shift(n))
    DX = abs(DIp-DIn)/(DIp+DIn) * 100
    # 2. PandasTA直接计算，是用的EMA
    ADX_df = ta.adx(high, low, close, n)
    DIp = ADX_df['DMP_{}'.format(n)]
    DIn = ADX_df['DMN_{}'.format(n)]
    DX = abs(DIp-DIn)/(DIp+DIn) * 100
    """ 指标赋值 """
    mkt_data['DMIp'] = DMIp
    mkt_data['DMIn'] = DMIn
    #mkt_data['TR'] = TR
    mkt_data['DIp'] = DIp
    mkt_data['DIn'] = DIn
    mkt_data['DX'] = DX
    return mkt_data

daily_300 = calc_ADX(daily_300,  n=14)
print(daily_300[:20])

# 计算信号
def calc_signal(mkt_data):
    DIp = mkt_data['DIp']
    DIn = mkt_data['DIn']
    signals = []
    for dip, din, pre_dip, pre_din in zip(DIp, DIn, DIp.shift(1), DIn.shift(1)):
        signal = None
        if pre_dip<pre_din and dip>=din:
            signal = 1
        elif pre_dip>=pre_din and dip<din:
            signal = -1
        signals.append(signal)
    mkt_data['signal'] = signals
    return mkt_data

daily_300 = calc_signal(daily_300)
print(daily_300)

# 计算持仓
def calc_position(mkt_data):
    mkt_data['position'] = mkt_data['signal'].fillna(method='ffill').shift(1).fillna(0)
    return mkt_data
daily_300 = calc_position(daily_300)
print(daily_300)

# 计算结果
def statistic_performance(mkt_data, r0=0.03, data_period=1440):
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


def visualize_performance(mkt_data):
    mkt_data['trade_datetime'] = mkt_data['trade_date'].apply(lambda x: datetime.datetime.strptime(str(x), '%Y%m%d'))
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

    # 绘制行情
    close = mkt_data['close']
    cumu_hold_close = (mkt_data['hold_cumu_r'] + 1)
    f1.line(dt, close / close.tolist()[0], line_width=1)
    f1.line(dt, cumu_hold_close, line_width=1, color='red')

    # 绘制指标
    indi = figure(height=200, sizing_mode='stretch_width',
                  title='ADX',
                  x_axis_type='datetime',
                  x_range=f1.x_range
                  )
    DIp = mkt_data['DIp']
    DIn = mkt_data['DIn']
    indi.line(dt, DIp, line_width=1, color='red')
    indi.line(dt, DIn, line_width=1, color='blue')

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

# 整体执行
daily_300 = calc_ADX(daily_300, n=16)
daily_300 = calc_signal(daily_300)
daily_300 = calc_position(daily_300)
print(daily_300)

# 评价和展现
result_daily_300,performance_df = statistic_performance(daily_300[daily_300['trade_date'].apply(lambda x: x>=int('20050901') and x<=int('20120315'))])

print(visualize_performance(result_daily_300))
print(performance_df)

# 参数稳定性（滚动参数优化）
def get_rolling_best_N(mkt_data, default_n=14, alternative_ns=[10, 11, 12, 13, 14, 15, 16], choice_period=125):
    """ 生成一个dict，存放所有参数下生成的mkt_data """
    alternative_dict = {}
    for n in alternative_ns:
        mkt_data = calc_ADX(mkt_data, n=n)
        mkt_data = calc_signal(mkt_data)
        mkt_data = calc_position(mkt_data)
        mkt_data['hold_r'] = mkt_data['position'] * mkt_data['pct_chg'] / 100
        mkt_data['cumu_hold_nv'] = (1 + mkt_data['hold_r']).cumprod()
        alternative_dict[n] = mkt_data.copy()

    """ 从choice_period + default_n开始，选择前choice_period期表现最好的策略的signal """
    cumu_hold_nv_df = pd.concat([alternative_dict[n][['cumu_hold_nv']] for n in alternative_ns],
                                axis=1)
    cumu_hold_nv_df.columns = alternative_ns
    position_df = pd.concat([alternative_dict[n][['position']] for n in alternative_ns],
                            axis=1)
    position_df.columns = alternative_ns

    best_Ns = [default_n] * len(mkt_data)
    best_positions = position_df[default_n].tolist()
    for idx in range(len(mkt_data) - choice_period - 1):
        """取 idx - idx+choice_period 共 choice_period条数据"""
        tmp_cumu_hold_nv_df = cumu_hold_nv_df[idx:idx + choice_period]
        """比较不同n下的 hold_cumu_r/max_dd 的值"""
        tmp_comp_res = pd.DataFrame(
            [[tmp_cumu_hold_nv_df[n].values[-1] / tmp_cumu_hold_nv_df[n].values[0] - 1 for n in alternative_ns],
             [(1 - tmp_cumu_hold_nv_df[n] / tmp_cumu_hold_nv_df[n].cummax()).max() for n in alternative_ns]
             ],
            columns=alternative_ns,
            index=['hold_cumu_r', 'max_dd']).T
        tmp_comp_res['value'] = tmp_comp_res['hold_cumu_r'] / tmp_comp_res['max_dd']
        """选取hold_cumu_r/max_dd最大的参数作为当期best_N，并将其下期的position作为下期的best_pos"""
        best_N = tmp_comp_res.sort_values(by='value', ascending=False).index[0]
        best_pos = position_df[best_N][idx + choice_period]
        best_Ns[idx + choice_period - 1] = best_N
        best_positions[idx + choice_period] = best_pos
    best_Ns = pd.Series(best_Ns, index=mkt_data['trade_date'])
    best_positions = pd.Series(best_positions, index=mkt_data['trade_date'])
    return best_Ns, best_positions

best_Ns, best_positions = get_rolling_best_N( daily_300,
                                              default_n=16,
                                              alternative_ns=[10,11,12,13,14,15,16],
                                              choice_period=125)
print(best_Ns.value_counts())
daily_300['position'] = best_positions.values

#result_daily_300, performance_df = statistic_performance(daily_300)
#result_daily_300, performance_df = statistic_performance(daily_300[daily_300['trade_date'].apply(lambda x: x>='20050901' and x<='20120315')])
result_daily_300, performance_df = statistic_performance(daily_300[daily_300['trade_date'].apply(lambda x: x>=int('20120315'))])

print(visualize_performance(result_daily_300))
print(performance_df)

# 策略改进方法
# 方法1：DIp-DIn金叉后差额在(-10, 2)的时候保持空仓
def calc_signal(mkt_data):
    DIp = mkt_data['DIp']
    DIn = mkt_data['DIn']
    DMIp = mkt_data['DMIp']
    DMIn = mkt_data['DMIn']
    """ 信号计算 """
    signals = []
    for dip, din, pre_dip, pre_din, dmip, dmin in zip(DIp, DIn, DIp.shift(1), DIn.shift(1), DMIp, DMIn):
        signal = None
        # DIp, DIn差值在(-10, 2)之内时候 空仓
        if dip - din>=2:
            signal = 1
        elif dip - din <= -10:
            signal = -1
        else:
            signal = 0
        signals.append(signal)
    """ 赋值 """
    mkt_data['signal'] = signals
    return mkt_data

daily_300 = calc_ADX(daily_300, n=16)
daily_300 = calc_signal(daily_300)
daily_300 = calc_position(daily_300)
daily_300

#result_daily_300, performance_df = statistic_performance(daily_300)
result_daily_300, performance_df = statistic_performance(daily_300[daily_300['trade_date'].apply(lambda x: x>=int('20050901') and x<=int('20120315'))])
#result_daily_300, performance_df = statistic_performance(daily_300[daily_300['trade_date'].apply(lambda x: x>='20120315')])

print(visualize_performance(result_daily_300))
print(performance_df)

# 方法2:DIp，DIn做3天平滑
def calc_ADX(mkt_data, n=14):
    high = mkt_data['high']
    low = mkt_data['low']
    close = mkt_data['close']
    """ 指标计算 """
    DMIp = high.rolling(2).max() - high.shift(1)
    DMIn = low.shift(1) - low.rolling(2).min()
    # DMIp和DMIn中只能有一个有值，选大的
    DMIp = DMIp*(DMIp>=DMIn)
    DMIn = DMIn*(DMIp<DMIn)
    TR = pd.concat([high, close.shift(1)], axis=1).max(axis=1) - pd.concat([low, close.shift(1)], axis=1).min(axis=1)
    #TR = abs(close - close.shift(1))
    DIp = DMIp.rolling(n).sum() / TR.rolling(n).sum()
    DIn = DMIn.rolling(n).sum() / TR.rolling(n).sum()
    DIp = DIp.rolling(3).mean()
    DIn = DIn.rolling(3).mean()
    DX = abs(DIp-DIn)/(DIp+DIn) * 100
    # PandasTA直接计算，是用的EMA
    ADX_df = ta.adx(high, low, close, n)
    DIp = ADX_df['DMP_{}'.format(n)].rolling(3).mean()
    DIn = ADX_df['DMN_{}'.format(n)].rolling(3).mean()
    DX = abs(DIp-DIn)/(DIp+DIn) * 100
    """ 赋值 """
    mkt_data['DMIp'] = DMIp
    mkt_data['DMIn'] = DMIn
    #mkt_data['TR'] = TR
    mkt_data['DIp'] = DIp
    mkt_data['DIn'] = DIn
    mkt_data['DX'] = DX
    return mkt_data

def calc_signal(mkt_data):
    DIp = mkt_data['DIp']
    DIn = mkt_data['DIn']
    """ 信号计算 """
    signals = []
    for dip, din, pre_dip, pre_din in zip(DIp, DIn, DIp.shift(1), DIn.shift(1)):
        signal = None
        if pre_dip<pre_din and dip>=din:
            signal = 1
        elif pre_dip>=pre_din and dip<din:
            signal = -1
        signals.append(signal)
    """ 赋值 """
    mkt_data['signal'] = signals
    return mkt_data

daily_300 = calc_ADX(daily_300, n=16)
daily_300 = calc_signal(daily_300)
daily_300 = calc_position(daily_300)
print(daily_300)

result_daily_300, performance_df = statistic_performance(daily_300[daily_300['trade_date'].apply(lambda x: x>=int('20050901') and x<=int('20120315'))])

print(visualize_performance(result_daily_300))
print(performance_df)
