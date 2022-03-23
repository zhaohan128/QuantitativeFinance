#通达信HMA-高价平均线
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#hma-%E9%AB%98%E4%BB%B7%E5%B9%B3%E5%9D%87%E7%BA%BF

#本文件：主要对HMA进行回测，需要数据包含最高价['high']、波动率['pct_chg']
#测试时间：20220323


HMA:=MA(HIGH,N);

用法注释：

一般移动平均线以收盘价为计算基础，高价平均线是以每日最高价为计算基础。

目前市场上许多投资人将其运用在空头市场，认为它的压力效应比传统平均线更具参考价值。


#20220323
上传version1.0