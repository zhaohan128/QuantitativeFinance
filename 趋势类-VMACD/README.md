#通达信VMACD-量平滑移动平均
#量指数平滑异同移动平均线(Vol Moving Average Convergence and Divergence)缩写为VMACD。
#因为是从双移动平均线发展而来，由快的移动平均线减去慢的移动平均线， 所以VMACD的意义和MACD基本相同, 但VMACD取用的数据源是成交量，MACD取用的数据源是成交价格，这是它们之间最大的区别。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#vmacd-%E9%87%8F%E5%B9%B3%E6%BB%91%E7%A7%BB%E5%8A%A8%E5%B9%B3%E5%9D%87
#http://cftsc.com/qushizhibiao/600.html

#本文件：主要对MACD进行回测，需要数据包含成交量['volume']、波动率['pct_chg']
#测试时间：20220311

量指数平滑异同平均线

原理：
    以成交量为权数的MACD指标。
算法：
DIFF线　成交量的短期(SHORT)、长期(LONG)指数平滑移动平均线间的差。
DEA线　 DIFF线的M日指数平滑移动平均线。
MACD线　DIFF线与DEA线的差，彩色柱状线。
用法：
1.DIFF、DEA均为正，DIFF向上突破DEA，买入信号。
2.DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号。
3.DEA线与K线发生背离，行情反转信号。
4.分析MACD柱状线，由正变负，卖出信号；由负变正，买入信号。


#20220311
上传version1.0