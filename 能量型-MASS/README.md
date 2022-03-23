#通达信MASS-梅斯线
#梅斯线（MASS），是唐纳德·道尔西（Donald Dorsey）累积股价波幅宽度之后，所设计的震荡曲线。本指标最主要的作用，在于寻找快速上涨股票或者极度弱势股票的重要趋势反转点。
#MASS指标是所有区间震荡指标中，风险系数最小的一个。股价高低点之间的价差波带忽而宽忽而窄，并且不断的重复循环。利用这种重复循环的波带，可以准确地预测股价的趋势反转点。一般市场上的技术指标通常不具备这方面的功能。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#mass-%E6%A2%85%E6%96%AF%E7%BA%BF
#http://cftsc.com/liangjiazhibiao/651.html

#本文件：主要对MASS进行回测，需要数据包含最高价['high']、最低价['low']、波动率['pct_chg']
#测试时间：20220318

指标源代码

1.MASS:SUM(MA(HIGH-LOW,N1)/MA(MA(HIGH-LOW,N1),N1),N2);

2.MAMASS:MA(MASS,M);

用法注释：

1.MASS>27 后，随后又跌破26.5，此时股价若呈上涨状态，则卖出；

2.MASS<27 后，随后又跌破26.5，此时股价若呈下跌状态，则买进；

3.MASS<20 的行情，不宜进行投资。


#20220318
上传version1.0
