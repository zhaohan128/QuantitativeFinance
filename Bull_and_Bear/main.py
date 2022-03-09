# -*- coding: utf-8 -*-
#华泰证券--金工研究/深度研究--20190927--波动率与换手率构造牛熊指标
#代码出处：https://blog.csdn.net/weixin_43915798/article/details/117366027
#相关研报：https://www.doc88.com/p-89499801312439.html
#本文件：主要对基于牛熊指标的双均线策略和布林带策略进行回测，需要数据包含，波动率'pct_chg'，换手率'turnover'，收盘价'close'
#测试时间：20220308

#加载库
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

# 构造牛熊指标，牛熊指标 = 250日波动率/250日换手率
def calc_fac(df):
    """
    构造牛熊指标，牛熊指标 = 250日波动率/250日换手率.

    :param df DataFrame 股票历史行情数据，日维度，需要包含波动率'pct_chg'，换手率'turnover'

    :return df DataFrame 新增一列牛熊指标'kernel'
    """
    df['250_vol'] = pd.Series.rolling(df['pct_chg'], window=250).std()
    df['250_turnover'] = pd.Series.rolling(df['turnover'], window=250).mean()
    df['kernel'] = df['250_vol'] / df['250_turnover']
    return df

#双均线策略计算净值
def calc_netv(df):
    """
    双均线策略计算牛熊指标净值.
    :param df DataFrame 股票历史行情数据，需要包含牛熊指标'kernel'

    :return df1 DataFrame 新增一列净值’net_value‘
    """
    df1 = df.copy()
    #为方便使用loc
    df1 = df1.reset_index()

    df1['kernel_20'] = pd.Series.rolling(df1.kernel,window = 20,min_periods = 1).mean()
    df1['kernel_60'] = pd.Series.rolling(df1.kernel,window = 60,min_periods = 1).mean()
    df1['position'] = 0
    df1['flag'] = 0
    position1 = 0

    for i in range(df.shape[0]-1):
        if df1.loc[i,'kernel_20'] < df1.loc[i,'kernel_60'] and position1 == 0:
            df1.loc[i,'flag'] = 1
            df1.loc[i+1,'position'] = 1
            position1 = 1
        elif df1.loc[i,'kernel_20'] > df1.loc[i,'kernel_60'] and position1 == 1:
            df1.loc[i,'flag'] = -1
            df1.loc[i+1,'position'] = 0
            position1 = 0
        else:
            df1.loc[i+1,'position'] = df1.loc[i,'position']
    df1['net_value'] = (1+(df1['pct_chg']/100)*df1.position).cumprod()
    return df1

def clac_itself(df):
    """
    双均线策略计算指数本身净值.
    :param df DataFrame 股票历史行情数据，需要包含收盘价'close'

    :return df_itself DataFrame 新增一列净值’net_value‘
    """

    #指数本身择时所有回测都需要，单独提出
    df_itself = df.copy()
    df_itself = df_itself.reset_index()
    df_itself['ma_20'] = pd.Series.rolling(df_itself['close'],window = 20,min_periods = 1).mean()
    df_itself['ma_60'] = pd.Series.rolling(df_itself['close'],window = 60,min_periods = 1).mean()
    df_itself['position'] = 0
    df_itself['flag'] = 0
    position2 = 0
    for i in range(df_itself.shape[0]-1):
        if df_itself.loc[i,'ma_20'] >  df_itself.loc[i,'ma_60'] and position2 == 0:
            df_itself.loc[i,'flag'] = 1
            df_itself.loc[i+1,'position'] = 1
            position2 = 1
        elif df_itself.loc[i,'ma_20'] <  df_itself.loc[i,'ma_60'] and position2 == 1:
            df_itself.loc[i+1,'position'] = 0
            df_itself.loc[i,'flag'] = -1
            position2 = 0
        else:
            df_itself.loc[i+1,'position'] = df_itself.loc[i,'position']
    df_itself['net_value'] = (1+(df_itself['pct_chg']/100)*df_itself.position).cumprod()
    return df_itself

#布林带策略计算净值
def bollinger_netv(df):
    """
    布林带策略计算牛熊指标净值.
    :param df DataFrame 股票历史行情数据，需要包含牛熊指标'kernel'

    :return df1 DataFrame 新增一列净值’net_value‘
    """
    df1 = df.copy()
    df1 = df1.reset_index()

    df1['ma_20'] = pd.Series.rolling(df1.kernel,window = 20,min_periods = 1).mean()
    df1['vol_20'] = pd.Series.rolling(df1.kernel,window = 20, min_periods = 1).std()
    df1['bullin_up'] = df1['ma_20'] + df1['vol_20']*2
    df1['bullin_down'] = df1['ma_20'] - df1['vol_20']*2

    df1['position'] = 0
    df1['flag'] = 0
    position = 0

    for i in range(df1.shape[0]-1):
        if df1.loc[i,'kernel'] < df1.loc[i,'bullin_down'] and position == 0:
            df1.loc[i,'flag'] = 1
            df1.loc[i+1,'position'] = 1
            position = 1
        elif df1.loc[i,'kernel'] > df1.loc[i,'bullin_up'] and position == 1:
            df1.loc[i+1,'position'] = 0
            df1.loc[i,'flag'] = -1
            position = 0
        else:
            df1.loc[i+1,'position'] = df1.loc[i,'position']
    df1['net_value'] = (1+(df1['pct_chg']/100)*df1.position).cumprod()

    return df1

def bollinger_itself(df):
    """
    布林带策略计算指标本身净值.
    :param df DataFrame 股票历史行情数据，需要包含收盘价'close'

    :return df1 DataFrame 新增一列净值’net_value‘
    """
    df1 = df.copy()
    df1 = df1.reset_index()

    df1['ma_20'] = pd.Series.rolling(df1.close,window = 20,min_periods = 1).mean()
    df1['vol_20'] = pd.Series.rolling(df1.close,window = 20, min_periods = 1).std()
    df1['bullin_up'] = df1['ma_20'] + df1['vol_20']*2
    df1['bullin_down'] = df1['ma_20'] - df1['vol_20']*2

    df1['position'] = 0
    df1['flag'] = 0
    position = 0

    for i in range(df1.shape[0]-1):
        if df1.loc[i,'close'] > df1.loc[i,'bullin_up'] and position == 0:
            df1.loc[i,'flag'] = 1
            df1.loc[i+1,'position'] = 1
            position = 1
        elif df1.loc[i,'close'] < df1.loc[i,'bullin_down'] and position == 1:
            df1.loc[i+1,'position'] = 0
            df1.loc[i,'flag'] = -1
            position = 0
        else:
            df1.loc[i+1,'position'] = df1.loc[i,'position']
    df1['net_value'] = (1+(df1['pct_chg']/100)*df1.position).cumprod()
    return df1

#策略绩效表现
def calc_statistic(df,index = False):
    """
    计算牛熊指标策略绩效表现.
    :param df DataFrame 股票历史行情数据，需要包含净值'net_value',交易信号'flag'

    :return df_statistic DataFrame 包含  '年化收益':annual_return_str,
                                        '年化波动率':annual_vol_str,
                                        '夏普比率':sharp_ratio,
                                        '最大回撤':max_drawdown_str,
                                        '做多胜率':trade_winrate_str,
                                        '交易盈亏比':profit_loss_ratio,
                                        '交易次数':trade_count,
                                        '平均交易频率':trade_frequency
    """
    total_return = df.loc[df.shape[0]-1,'net_value']-df.net_value[0]
    annual_return = (total_return+1)**(1/(df.shape[0]/250))-1
    annual_return_str = format(annual_return*100,'.2f')+'%'

    annual_vol = (df['net_value'].pct_change(1).fillna(0)).std()*250**(0.5)
    annual_vol_str = format(annual_vol*100,'.2f') + '%'

    #原研报中直接采用年化收益率闭上年化波动率，未减去无风险利率
    sharp_ratio = annual_return/annual_vol
    sharp_ratio = format(sharp_ratio,'4f')

    df['high_level'] = pd.Series.rolling(df.net_value,window = df.shape[0],min_periods=1).max()
    max_drawdown = ((df.net_value - df['high_level'] )/df['high_level'] ).min()
    #输出为百分比
    max_drawdown_str = format(max_drawdown*100,'.2f') + '%'

    sell_trade = np.array(df[df['flag'] < 0].net_value)
    buy_trade = np.array(df[df['flag'] > 0].net_value)

    if df[df['flag']!=0]['flag'].iloc[0] < 0:
        buy_trade = np.insert(buy_trade,0,df['net_value'].iloc[0])
    if df[df['flag']!=0]['flag'].iloc[-1] == 1:
        sell_trade = np.append(sell_trade,df['net_value'].iloc[-1])

    trade_pct = (sell_trade - buy_trade)/buy_trade

    #做多胜率
    trade_winrate = len(trade_pct[trade_pct>0])/len(trade_pct)
    trade_winrate_str = format(trade_winrate*100,'.2f') + '%'
    #盈亏比
    if trade_winrate == 1:
        profit_loss_ratio = 'all_win'
    else:
        profit_loss_ratio = trade_winrate/(1-trade_winrate)
        profit_loss_ratio = format(profit_loss_ratio,'.4f')

    #交易次数
    trade_count = len(buy_trade)*2
    #交易频率
    trade_frequency = df.shape[0]/trade_count
    trade_frequency = np.round(trade_frequency)

    statistic_dict = {'年化收益':annual_return_str,'年化波动率':annual_vol_str,'夏普比率':sharp_ratio,'最大回撤':max_drawdown_str,
                     '做多胜率':trade_winrate_str,'交易盈亏比':profit_loss_ratio,'交易次数':trade_count,'平均交易频率':trade_frequency}

    df_statistic = pd.DataFrame([statistic_dict])

    if index:
        df_statistic.index = [index]

    return df_statistic

#指数本身表现
def calc_index(df,index = False):
    """
    计算指数本身指标(非择时).
    :param df DataFrame 股票历史行情数据，需要包含收盘价'close',交易信号'flag'

    :return df_index DataFrame 包含  '年化收益':annual_return_str,
                                    '年化波动率':annual_vol_str,
                                    '夏普比率':sharp_ratio,
                                    '最大回撤':max_drawdown_str,
                                    '做多胜率':trade_winrate_str,
                                    '交易盈亏比':profit_loss_ratio,
                                    '交易次数':trade_count,
                                    '平均交易频率':trade_frequency
    """
    #计算指数本身指标(非择时)
    total_return_index = df['close'].iloc[-1]/df['close'].iloc[0] - 1
    annual_return_index = (total_return_index+1)**(1/(df.shape[0]/250))-1
    annual_return__index_str = format(annual_return_index*100,'.2f')+'%'
    annual_vol_index = (df['close'].pct_change(1).fillna(0)).std()*250**(0.5)
    annual_vol_index_str = format(annual_vol_index*100,'.2f') + '%'
    sharp_ratio_index = annual_return_index/annual_vol_index
    sharp_ratio_index_str = format(sharp_ratio_index,'4f')
    df['high_level'] = pd.Series.rolling(df.close,window = df.shape[0],min_periods=1).max()
    max_drawdown_index = ((df.close - df['high_level'] )/df['high_level'] ).min()
    max_drawdown_index_str = format(max_drawdown_index*100,'.2f') + '%'
    statistic_dict = {'年化收益':annual_return__index_str,'年化波动率':annual_vol_index_str,'夏普比率':sharp_ratio_index_str,
                      '最大回撤':max_drawdown_index_str,'做多胜率':None,'交易盈亏比':None,'交易次数':None,'平均交易频率':None}

    if index:
        df_index = pd.DataFrame([statistic_dict],index = [index])
    else:
        df_index = pd.DataFrame([statistic_dict])

    return df_index

#画图
def plot_net(df_signal,df_itself):
    """
    画图对比两种择时净值.
    :param df_signal DataFrame 通过牛熊指标得到的策略净值，需要包含'net_value'
    :param df_itself DataFrame 通过指标本身得到的策略净值，需要包含'net_value'
    """
    fig = plt.figure(figsize = (10,4),dpi = 100)
    x = range(df_signal.shape[0])

    plt.plot(x,df_signal['net_value'],label = '牛熊指标择时',color = 'r')
    plt.plot(x,df_itself['net_value'],label = '指数本身择时',color = 'm')
    plt.plot(x,df_signal['close']/df_itself.close[0],label = '指数',color = 'c')

    xlab = range(0,df_itself.shape[0],int(df_itself.shape[0]/12))
    plt.xticks(xlab,df_itself.index[xlab],rotation = 30)
    plt.legend(loc = 'best')
    plt.show()

#导入数据
df = pd.read_csv('data/000001.csv', parse_dates=['date'], index_col=['date'], encoding='utf-8')
#计算牛熊指标
df = calc_fac(df)

#双均线策略回测
df_signal = calc_netv(df)
df_itself = clac_itself(df)
plot_net(df_signal,df_itself)
print(calc_statistic(df_signal))
print(calc_statistic(df_itself))
print(calc_index(df))

#布林带策略回测
df_signal = bollinger_netv(df)
df_itself = bollinger_itself(df)
plot_net(df_signal,df_itself)
print(calc_statistic(df_signal))
print(calc_statistic(df_itself))
print(calc_index(df))

#其他一些描述图
#波动率历史特征
df['60_vol'] = pd.Series.rolling(df['pct_chg'],window = 60).std()
df['120_vol'] = pd.Series.rolling(df['pct_chg'],window = 120).std()
df['200_vol'] = pd.Series.rolling(df['pct_chg'],window = 200).std()
df['250_vol'] = pd.Series.rolling(df['pct_chg'],window = 250).std()
plt.figure(figsize = (10,4),dpi = 100)#dpi 是像素设置
xticks = np.arange(0,df.shape[0],int(df.shape[0]/12))
xticklabel = pd.Series(df.index[xticks])
col_list = ['60_vol','120_vol','200_vol','250_vol']
for i in col_list:
    plt.plot(range(df.shape[0]),df[i],label = i)
plt.xlabel('Time')
plt.ylabel('Volitility')
plt.xticks(xticks,xticklabel,rotation = 30)
plt.title('上证综指不同参数下的历史波动率对比')
plt.legend(loc = 'best')
plt.show()

#换手率数据和研报不一样
plt.plot(range(df.shape[0]),df['turnover'])
plt.show()
#换手率历史特征
#60、120、200换手率以后用不到，故单独计算
df['60_turnover'] = pd.Series.rolling(df['turnover'],window = 60).mean()
df['120_turnover'] = pd.Series.rolling(df['turnover'],window = 120).mean()
df['200_turnover'] = pd.Series.rolling(df['turnover'],window = 200).mean()
df#去掉除顶部框和右侧框
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.figure(figsize = (11,4),dpi = 100)
xticks = np.arange(0,df.shape[0],int(df.shape[0]/12))
xticklabel = pd.Series(df.index[xticks])
col_list = ['60_turnover','120_turnover','200_turnover','250_turnover']
for i in col_list:
    plt.plot(range(df.shape[0]),df[i],label = i)
plt.xticks(xticks,xticklabel,rotation = 30)
plt.title('上证综指不同参数下的日均换手率')
plt.legend(loc = 'best')
plt.show()

#指标走势图
#构造牛熊指标，牛熊指标 = 250日波动率/250日换手率
df['250_vol'] = pd.Series.rolling(df['pct_chg'],window = 250).std()
df['250_turnover'] = pd.Series.rolling(df['turnover'],window = 250).mean()
df['kernel'] = df['250_vol']/df['250_turnover']
fig = plt.figure(figsize = (10,4),dpi = 100)
ax1 = fig.add_subplot(111)
ax1.plot(range(df.shape[0]),df.close, label='close',color = 'r',linewidth = 2)
plt.legend(loc='upper left')
plt.ylim(0,7000)
plt.xticks(xticks,xticklabel,rotation = 30)
ax2 = ax1.twinx()
ax2.plot(range(df.shape[0]),df.kernel, label='牛熊指标',color = 'b',linewidth = 2)
plt.ylim(0,70)
plt.legend(loc='best')
ax1.set_title("上证综指收盘价与其对应的牛熊指标")
plt.show()
corr = df.close.corr(df.kernel)#计算相关性