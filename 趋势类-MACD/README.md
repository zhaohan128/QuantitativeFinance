#通达信MACD-平滑异同平均

#MACD即指数平滑异同移动平均线（Moving Average Convergence Divergence，macd）是股票交易中一种常见的技术分析工具，是从双移动平均线发展而来的，由Gerald Appel于1970年代提出，用于研判价格或指数变化的强度、方向、能量以及趋势周期，以便把握买进和卖出的时机。
#MACD指标由一组曲线与图形组成，通过收盘时股价或指数的快变及慢变的移动平均值（EMA）之间的差计算出来。“快”指更短时段的EMA，而“慢”则指较长时段的EMA，最常用的是12及26日EMA。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#macd-%E5%B9%B3%E6%BB%91%E5%BC%82%E5%90%8C%E5%B9%B3%E5%9D%87
#https://zhuanlan.zhihu.com/p/134077409

#本文件：主要对MACD进行回测，需要数据包含收盘价['close']、波动率['pct_chg']
#测试时间：20220311


DIFF线　收盘价短期、长期指数平滑移动平均线间的差

DEA线　 DIFF线的M日指数平滑移动平均线

MACD线　DIFF线与DEA线的差，彩色柱状线

用法：

1.DIFF、DEA均为正，DIFF向上突破DEA，买入信号。

2.DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号。

3.DEA线与K线发生背离，行情反转信号。

4.分析MACD柱状线，由红变绿(正变负)，卖出信号；由绿变红，买入信号


#20220311
上传version1.0