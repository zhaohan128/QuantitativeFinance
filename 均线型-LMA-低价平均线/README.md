#通达信LMA-低价平均线
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#lma-%E4%BD%8E%E4%BB%B7%E5%B9%B3%E5%9D%87%E7%BA%BF

#本文件：主要对LMA进行回测，需要数据包含最低价['low']、波动率['pct_chg']
#测试时间：20220323

LMA:=MA(LOW,N);

用法注释：

一般移动平均线以收盘价为计算基础，低价平均线是以每日最低价为计算基础。

目前市场上许多投资人将其运用在多头市场，认为它的支撑效应比传统平均线更具参考价值。


#20220323
上传version1.0