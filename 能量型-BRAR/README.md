#通达信BRAR-情绪指标
#情绪指标（ARBR）也称为人气意愿指标，其英文缩写亦可表示为BRAR。由人气指标(AR)和意愿指标(BR)两个指标构成。AR指标和BR指标都是以分析历史股价为手段的技术指标。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#brar-%E6%83%85%E7%BB%AA%E6%8C%87%E6%A0%87
#http://cftsc.com/liangjiazhibiao/648.html

#本文件：主要对BRAR进行回测，需要数据包含收盘价['close']、开盘价['open']、最高价['high']、最低价['low']、波动率['pct_chg']
#测试时间：20220316

指标源代码

M1=26

AR:SUM(HIGH-OPEN,M1)/SUM(OPEN-LOW,M1)*100;

BR:SUM(MAX(0,HIGH-REF(CLOSE,1)),M1)/SUM(MAX(0,REF(CLOSE,1)-LOW),M1)*100;

用法注释：

1.BR>400，暗示行情过热，应反向卖出；BR<40 ，行情将起死回生，应买进；

2.AR>180，能量耗尽，应卖出；AR<40 ，能量已累积爆发力，应买进；

3.BR 由300 以上的高点下跌至50以下的水平,低于AR 时,为绝佳买点；

4.BR、AR、CR、VR 四者合为一组指标群，须综合搭配使用。



#20220316
上传version1.0