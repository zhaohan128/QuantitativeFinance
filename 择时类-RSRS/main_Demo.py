# -*- coding: utf-8 -*-
#光大证券--金融工程--20170501--基于阻力支撑相对强度（择时类-RSRS）的市场择时——技术择时系列报告之一
#代码出处：https://blog.csdn.net/weixin_43915798/article/details/116097715?spm=1001.2014.3001.5502
#相关研报：见文件夹
#本文件：主要对基于阻力支撑相对强度（择时类-RSRS）择时进行回测，需要数据包含，最低价'low'，最高价'high'，收盘价'close'
#测试时间：20220308

import datetime
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
import warnings
from bokeh.plotting import figure, show, output_notebook
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import Span
warnings.filterwarnings("ignore")
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

#策略策略结果
def calculate_statistics(df):
    '''
    计算策略结果
    :param df DataFrame 包含价格数据和仓位、开平仓标志
                        position列：仓位标志位，0表示空仓，1表示持有标的
                        flag列：买入卖出标志位，1表示在该时刻买入，-1表示在该时刻卖出
                        close列：日收盘价

    :return statistics_result dict 包含夏普比率、最大回撤等策略结果的统计数据
    '''
    # 净值序列
    df['net_asset_pct_chg'] = df.net_asset_value.pct_change(1).fillna(0)

    # 总收益率与年化收益率
    total_return = (df['net_asset_value'][df.shape[0] - 1] - 1)
    annual_return = (total_return) ** (1 / (df.shape[0] / 252)) - 1
    total_return = total_return * 100
    annual_return = annual_return * 100
    # 夏普比率
    df['ex_pct_chg'] = df['net_asset_pct_chg']
    sharp_ratio = df['ex_pct_chg'].mean() * math.sqrt(252) / df['ex_pct_chg'].std()

    # 回撤
    df['high_level'] = (
        df['net_asset_value'].rolling(
            min_periods=1, window=len(df), center=False).max()
    )
    df['draw_down'] = df['net_asset_value'] - df['high_level']
    df['draw_down_percent'] = df["draw_down"] / df["high_level"] * 100
    max_draw_down = df["draw_down"].min()
    max_draw_percent = df["draw_down_percent"].min()

    # 持仓总天数
    hold_days = df['position'].sum()

    # 交易次数
    trade_count = df[df['flag'] != 0].shape[0] / 2

    # 平均持仓天数
    avg_hold_days = int(hold_days / trade_count)

    # 获利天数
    profit_days = df[df['net_asset_pct_chg'] > 0].shape[0]
    # 亏损天数
    loss_days = df[df['net_asset_pct_chg'] < 0].shape[0]

    # 胜率(按天)
    winrate_by_day = profit_days / (profit_days + loss_days) * 100
    # 平均盈利率(按天)
    avg_profit_rate_day = df[df['net_asset_pct_chg'] > 0]['net_asset_pct_chg'].mean() * 100
    # 平均亏损率(按天)
    avg_loss_rate_day = df[df['net_asset_pct_chg'] < 0]['net_asset_pct_chg'].mean() * 100
    # 平均盈亏比(按天)
    avg_profit_loss_ratio_day = avg_profit_rate_day / abs(avg_loss_rate_day)

    # 每一次交易情况
    buy_trades = df[df['flag'] == 1].reset_index()
    sell_trades = df[df['flag'] == -1].reset_index()
    result_by_trade = {
        'buy': buy_trades['close'],
        'sell': sell_trades['close'],
        'pct_chg': (sell_trades['close'] - buy_trades['close']) / buy_trades['close']
    }
    result_by_trade = pd.DataFrame(result_by_trade)
    # 盈利次数
    profit_trades = result_by_trade[result_by_trade['pct_chg'] > 0].shape[0]
    # 亏损次数
    loss_trades = result_by_trade[result_by_trade['pct_chg'] < 0].shape[0]
    # 单次最大盈利
    max_profit_trade = result_by_trade['pct_chg'].max() * 100
    # 单次最大亏损
    max_loss_trade = result_by_trade['pct_chg'].min() * 100
    # 胜率(按次)
    winrate_by_trade = profit_trades / (profit_trades + loss_trades) * 100
    # 平均盈利率(按次)
    avg_profit_rate_trade = result_by_trade[result_by_trade['pct_chg'] > 0]['pct_chg'].mean() * 100
    # 平均亏损率(按次)
    avg_loss_rate_trade = result_by_trade[result_by_trade['pct_chg'] < 0]['pct_chg'].mean() * 100
    # 平均盈亏比(按次)
    avg_profit_loss_ratio_trade = avg_profit_rate_trade / abs(avg_loss_rate_trade)

    statistics_result = {
        'net_asset_value': df['net_asset_value'][df.shape[0] - 1],  # 最终净值
        'total_return': total_return,  # 收益率
        'annual_return': annual_return,  # 年化收益率
        'sharp_ratio': sharp_ratio,  # 夏普比率
        'max_draw_percent': max_draw_percent,  # 最大回撤
        'hold_days': hold_days,  # 持仓天数
        'trade_count': trade_count,  # 交易次数
        'avg_hold_days': avg_hold_days,  # 平均持仓天数
        'profit_days': profit_days,  # 盈利天数
        'loss_days': loss_days,  # 亏损天数
        'winrate_by_day': winrate_by_day,  # 胜率（按天）
        'avg_profit_rate_day': avg_profit_rate_day,  # 平均盈利率（按天）
        'avg_loss_rate_day': avg_loss_rate_day,  # 平均亏损率（按天）
        'avg_profit_loss_ratio_day': avg_profit_loss_ratio_day,  # 平均盈亏比（按天）
        'profit_trades': profit_trades,  # 盈利次数
        'loss_trades': loss_trades,  # 亏损次数
        'max_profit_trade': max_profit_trade,  # 单次最大盈利
        'max_loss_trade': max_loss_trade,  # 单次最大亏损
        'winrate_by_trade': winrate_by_trade,  # 胜率（按次）
        'avg_profit_rate_trade': avg_profit_rate_trade,  # 平均盈利率（按次）
        'avg_loss_rate_trade': avg_loss_rate_trade,  # 平均亏损率（按次）
        'avg_profit_loss_ratio_trade': avg_profit_loss_ratio_trade  # 平均盈亏比（按次）
    }
    return statistics_result

# 当日斜率指标计算方式，线性回归
def cal_nbeta(df, n):
    """
    当日斜率指标计算方式，线性回归.

    :param df DataFrame 股票历史行情数据，日维度，需要包含最低价'low'，最高价'high'
    :param n int 以n天序列构造OLS

    :return df1 DataFrame 新增策略净值'net_asset_value'
    """
    nbeta = []
    trade_days = len(df.index)

    df['position'] = 0
    df['flag'] = 0
    position = 0

    # 计算斜率值
    for i in range(trade_days):
        if i < (n - 1):
            # n-1为配合接下来用iloc索引
            continue
        else:
            x = df['low'].iloc[i - n + 1:i + 1]
            # iloc左闭右开
            x = sm.add_constant(x) #增加常量变量
            y = df['high'].iloc[i - n + 1:i + 1]
            regr = sm.OLS(y, x)
            res = regr.fit()
            beta = round(res.params[1], 2)  # 斜率指标
            nbeta.append(beta)
    df1 = df.iloc[n - 1:]
    df1['beta'] = nbeta

    # 执行交易策略
    for i in range(len(df1.index) - 1):
        # 此处-1是为了避免最后一行
        if df1['beta'].iloc[i] > 1 and position == 0:
            df1['flag'].iloc[i] = 1  # 开仓标志
            df1['position'].iloc[i + 1] = 1  # 仓位不为空
            position = 1
        elif df1['beta'].iloc[i] < 0.8 and position == 1:
            df1['flag'].iloc[i] = -1  # 平仓标志
            df1['position'].iloc[i + 1] = 0  # 仓位为空
            position = 0
        else:
            df1['position'].iloc[i + 1] = df1['position'].iloc[i]
    # 计算净值序列
    df1['net_asset_value'] = (1 + df1.close.pct_change(1).fillna(0) * df1.position).cumprod()

    return df1

# 标准分策略--应该是动态的
def cal_stdbeta(df, n, m):
    """
    改进1，标准分策略。

    :param df DataFrame 股票历史行情数据，日维度，需要包含最低价'low'，最高价'high'
    :param n int 以n天序列构造OLS
    :param m int 计算标准分所用周期天数m

    :return df1 DataFrame 新增策略净值'net_asset_value'
    """
    df['position'] = 0
    df['flag'] = 0
    position = 0

    df1 = cal_nbeta(df, n)
    pre_stdbeta = df1['beta']
    #pre_stdbeta = np.array(pre_stdbeta)
    # 转化为数组，可以对整个数组进行操作
    #sigma = np.std(pre_stdbeta)
    #mu = np.mean(pre_stdbeta)
    # 标准化
    sigma = pd.Series.rolling(pre_stdbeta,window = m,min_periods = 1).std()
    mu = pd.Series.rolling(pre_stdbeta,window = m,min_periods = 1).mean()
    stdbeta = (pre_stdbeta - mu) / sigma

    df1['stdbeta'] = stdbeta

    for i in range(len(df1.index) - 1):
        # 此处-1是为了避免最后一行
        if df1['stdbeta'].iloc[i] > 0.7 and position == 0:
            df1['flag'].iloc[i] = 1
            df1['position'].iloc[i + 1] = 1
            position = 1
        elif df1['stdbeta'].iloc[i] < -0.7 and position == 1:
            df1['flag'].iloc[i] = -1
            df1['position'].iloc[i + 1] = 0
            position = 0
        else:
            df1['position'].iloc[i + 1] = df1['position'].iloc[i]

    df1['net_asset_value'] = (1 + df1.close.pct_change(1).fillna(0) * df1.position).cumprod()
    return df1
# stdbeta是数组 beta是列表

# 优化策略
# 择时类-RSRS 标准分指标优化,修正标准分
def cal_better_stdbeta(df, n):
    """
    改进策略，择时类-RSRS 标准分指标优化,修正标准分。

    :param df DataFrame 股票历史行情数据，日维度，需要包含最低价'low'，最高价'high'
    :param n int 以n天序列构造OLS

    :return df1 DataFrame 新增策略净值'net_asset_value'
    """
    nbeta = []
    R2 = []
    trade_days = len(df.index)
    for i in range(trade_days):
        if i < (n - 1):
            # n-1为配合接下来用iloc索引
            continue
        else:

            x = df['low'].iloc[i - n + 1:i + 1]
            # iloc左闭右开
            x = sm.add_constant(x)
            y = df['high'].iloc[i - n + 1:i + 1]
            regr = sm.OLS(y, x)
            res = regr.fit()
            beta = round(res.params[1], 2)

            R2.append(res.rsquared)
            nbeta.append(beta)

    prebeta = np.array(nbeta)
    sigma = np.std(prebeta)
    mu = np.mean(prebeta)
    stdbeta = (prebeta - mu) / sigma

    r2 = np.array(R2)
    better_stdbeta = r2 * stdbeta  # 修正标准分

    df1 = df.iloc[n - 1:]
    df1['beta'] = nbeta
    df1['flag'] = 0
    df1['position'] = 0
    position = 0
    df1['better_stdbeta'] = better_stdbeta

    for i in range(len(df1.index) - 1):
        # 此处-1是为了避免最后一行
        if df1['better_stdbeta'].iloc[i] > 0.7 and position == 0:
            df1['flag'].iloc[i] = 1
            df1['position'].iloc[i + 1] = 1
            position = 1
        elif df1['better_stdbeta'].iloc[i] < -0.7 and position == 1:
            df1['flag'].iloc[i] = -1
            df1['position'].iloc[i + 1] = 0
            position = 0
        else:
            df1['position'].iloc[i + 1] = df1['position'].iloc[i]
    df1['net_asset_value'] = (1 + df1.close.pct_change(1).fillna(0) * df1.position).cumprod()
    return df1

# 右偏标准分 此时N取16
def cal_right_stdbeta(df, n, m):
    """
    改进策略，右偏标准分

    :param df DataFrame 股票历史行情数据，日维度，需要包含最低价'low'，最高价'high'
    :param n int 以n天序列构造OLS
    :param m int 计算标准分所用周期天数m

    :return df1 DataFrame 新增策略净值'net_asset_value'
    """
    df1 = cal_better_stdbeta(df, n)
    df1['position'] = 0
    df1['flag'] = 0
    df1['net_value'] = 0
    position = 0

    df1['right_stdbeta'] = df1['better_stdbeta'] * df1['beta']
    # 修正标准分与斜率值相乘能够达到使原有分布右偏的效果

    for i in range(len(df1.index) - 1):
        # 此处-1是为了避免最后一行
        if df1['right_stdbeta'].iloc[i] > 0.7 and position == 0:
            df1['flag'].iloc[i] = 1
            df1['position'].iloc[i + 1] = 1
            position = 1
        elif df1['right_stdbeta'].iloc[i] < -0.7 and position == 1:
            df1['flag'].iloc[i] = -1
            df1['position'].iloc[i + 1] = 0
            position = 0
        else:
            df1['position'].iloc[i + 1] = df1['position'].iloc[i]
    df1['net_asset_value'] = (1 + df1.close.pct_change(1).fillna(0) * df1.position).cumprod()
    return df1

#RSRS指标配合价格数据优化策略
def cal_ma_beta(df, n, m):
    """
    改进策略，RSRS指标配合价格数据优化策略

    :param df DataFrame 股票历史行情数据，日维度，需要包含最低价'low'，最高价'high'
    :param n int 以n天序列构造OLS
    :param m int 计算标准分所用周期天数m

    :return df1 DataFrame 新增策略净值'net_asset_value'
    """
    df1 = cal_stdbeta(df, n, m)
    df1['ma20'] = pd.Series.rolling(df1['close'],window = 20,min_periods = 1).mean()
    df1['position'] = 0
    df1['flag'] = 0
    df1['net_asset_value'] = 0
    position = 0

    # beta是前17天没有数据（n=18） ma20是前20天没有数据
    for i in range(5, len(df1.index) - 1):
        if df1['stdbeta'].iloc[i] > 0.7 and df1['ma20'].iloc[i - 1] > df1['ma20'].iloc[i - 3] and position == 0:
            df1['flag'].iloc[i] = 1
            df1['position'].iloc[i + 1] = 1
            position = 1
        elif df1['stdbeta'].iloc[i] < -0.7 and df1['ma20'].iloc[i - 1] < df1['ma20'].iloc[i - 3] and position == 1:
            df1['flag'].iloc[i] = -1
            df1['position'].iloc[i + 1] = 0
            position = 0
        else:
            df1['position'].iloc[i + 1] = df1['position'].iloc[i]
    df1['net_asset_value'] = (1 + df1.close.pct_change(1).fillna(0) * df1.position).cumprod()
    return df1

# 基于 择时类-RSRS 指标与交易量相关性的优化
def cal_vol_beta(df, n, m):
    """
    改进策略，基于 择时类-RSRS 指标与交易量相关性的优化

    :param df DataFrame 股票历史行情数据，日维度，需要包含最低价'low'，最高价'high'
    :param n int 以n天序列构造OLS
    :param m int 计算标准分所用周期天数m

    :return df1 DataFrame 新增策略净值'net_asset_value'
    """
    df1 = cal_stdbeta(df, n, m)

    df1['position'] = 0
    df1['flag'] = 0
    df1['net_asset_value'] = 0
    position = 0

    for i in range(10, len(df1.index) - 1):

        pre_volume = df1['volume'].iloc[i - 10:i]
        series_beta = df1['stdbeta'].iloc[i - 10:i]
        # 计算相关系数需要数据为series格式
        corr = series_beta.corr(pre_volume, method='pearson')
        if df1['stdbeta'].iloc[i] > 0.7 and corr > 0 and position == 0:
            df1['flag'].iloc[i] = 1
            df1['position'].iloc[i + 1] = 1
            position = 1
        elif df1['stdbeta'].iloc[i] < -0.7 and position == 1:
            df1['flag'].iloc[i] = -1
            df1['position'].iloc[i + 1] = 0
            position = 0
        else:
            df1['position'].iloc[i + 1] = df1['position'].iloc[i]

    df1['net_asset_value'] = (1 + df1.close.pct_change(1).fillna(0) * df1.position).cumprod()
    return df1

#可视化
def visualize_performance(mkt_data):
    """
    可视化，策略回测情况

    :param mkt_data DataFrame 股票历史行情数据，日维度，需要包含日期‘date',收盘价'close',累计收益率’hold_cumu_r‘
                                                            收益'hold_r'，最大回测'drawdown'

    :return plt html
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
                  title='KDJ',
                  x_axis_type='datetime',
                  x_range=f1.x_range
                  )

    # 绘制行情
    close = mkt_data['close']
    cumu_hold_close = (mkt_data['hold_cumu_r'] + 1)
    f1.line(dt, close / close.tolist()[0], line_width=1)
    f1.line(dt, cumu_hold_close, line_width=1, color='red')

    # 绘制指标

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
                  # [indi],
                  [f2],
                  [f3],
                  [f4]
                  ])
    show(p)

def visualize_performance_2(mkt_data,mkt_data_std):
    """
    可视化，对比斜率策略、标准分策略、指数本身回测

    :param mkt_data DataFrame 斜率策略结果数据，需要包含日期‘date',收盘价'close',净值’net_asset_value‘
    :param mkt_data_std DataFrame 标准分策略结果数据，需要包含日期‘date',收盘价'close',净值’net_asset_value‘

    :return plt html
    """
    mkt_data_std['trade_datetime'] = mkt_data_std['date'].apply(lambda x: datetime.datetime.strptime(str(x), '%Y-%m-%d'))
    mkt_data['trade_datetime'] = mkt_data['date'].apply(lambda x: datetime.datetime.strptime(str(x), '%Y-%m-%d'))
    dt = mkt_data['trade_datetime']

    f1 = figure(height=300, width=700,
                #legend_location = "top_left",
                sizing_mode='stretch_width',
                title='Target Trend',
                x_axis_type='datetime',
                x_axis_label="trade_datetime", y_axis_label="close")

    # 绘制行情
    close = mkt_data['close']
    cumu_hold_close = (mkt_data['net_asset_value'] + 1)
    cumu_hold_close_std = (mkt_data_std['net_asset_value'] + 1)
    f1.line(dt, close / close.tolist()[0], line_width=1,legend='沪深300指数净值')
    f1.line(dt, cumu_hold_close, line_width=1, color='red',legend='斜率策略净值')
    f1.line(dt, cumu_hold_close_std, line_width=1, color='purple',legend='标准分策略净值')

    p = gridplot([[f1]])
    show(p)


#导入数据
df = pd.read_csv('data/000300.csv', encoding='utf-8')
mkt_data = cal_nbeta(df,18) #斜率策略
mkt_data_std = cal_stdbeta(df,18, 60) #标准分策略

#斜率策略&标准分策略对比
visualize_performance_2(mkt_data,mkt_data_std)
print(calculate_statistics(mkt_data))
print(calculate_statistics(mkt_data_std))

# 优化策略结果输出
# 择时类-RSRS 标准分指标优化,修正标准分
data = cal_better_stdbeta(df, 16)
print(calculate_statistics(data))

# 右偏标准分 此时N取16
data = cal_right_stdbeta(df, 16, 60)
print(calculate_statistics(data))

#RSRS指标配合价格数据优化策略
data = cal_ma_beta(df, 16, 60)
print(calculate_statistics(data))

# 基于 择时类-RSRS 指标与交易量相关性的优化
data = cal_vol_beta(df, 16, 60)
print(calculate_statistics(data))