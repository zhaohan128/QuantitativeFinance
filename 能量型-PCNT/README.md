#通达信PCNT-幅度比
#PCNT幅度比指标是考察股票的涨跌幅度代替涨跌值的大小，有利于判断股票的活跃程度。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#pcnt-%E5%B9%85%E5%BA%A6%E6%AF%94
#https://www.zcaijing.com/jdjszb/263725.html

#本文件：主要对MASS进行回测，需要数据包含收盘价['close']、波动率['pct_chg']
#测试时间：20220318

指标源代码

幅度比＝（收盘价－昨收价）＋收盘价X100

并计算PCNT的M日加权平滑平均

用法注释：

1.PCNT 重视价格的涨跌幅度，排除观察涨跌跳动值；

2.较高的PCNT 值，表示该股波动幅度大；

3.较低的PCNT 值，表示该股波动幅度小。



#20220318
上传version1.0
