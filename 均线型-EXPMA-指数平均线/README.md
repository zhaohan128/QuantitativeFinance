#通达信EXPMA-指数平均线
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#expma-%E6%8C%87%E6%95%B0%E5%B9%B3%E5%9D%87%E7%BA%BF

#本文件：主要对EMA进行回测，需要数据包含收盘价['close']、波动率['pct_chg']
#测试时间：20220322

指标源代码

Y = EMA(X，N)，则Y =［2 * X + (N - 1) * Y’］ / (N + 1)，其中Y’表示上一周期的Y值。

用法注释：

1.EXPMA 一般以观察12日和50日二条均线为主；

2.12日指数平均线向上交叉50日指数平均线时，买进；

3.12日指数平均线向下交叉50日指数平均线时，卖出；

4.EXPMA 是多种平均线计算方法的一；

5.EXPMA 配合MTM 指标使用，效果更佳。



#20220322
上传version1.0