#通达信TRIX-终极指标
#TRIX指标又叫三重指数平滑移动平均指标，其英文全名为“Triple Exponentially Smoothed Average”，是一种研究股价趋势的长期技术分析工具。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#trix-%E7%BB%88%E6%9E%81%E6%8C%87%E6%A0%87
#https://zhuanlan.zhihu.com/p/134077409

#本文件：主要对TRIX进行回测，需要数据包含收盘价['close']、波动率['pct_chg']
#测试时间：20220311


TR:= EMA(EMA(EMA(CLOSE,N),N),N);

TRIX : (TR-REF(TR,1))/REF(TR,1)*100;

TRMA : MA(TRIX,M)。

用法注释：

1.TRIX由下往上交叉其平均线时，为长期买进信号；

2.TRIX由上往下交叉其平均线时，为长期卖出信号；

3.DMA、MACD、TRIX 三者构成一组指标群，互相验证。


#20220314
上传version1.0
