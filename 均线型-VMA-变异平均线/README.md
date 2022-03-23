#通达信VMA-变异平均线
#变异平均线（VMA）与移动平均线的计算方法是一样的，区别在于移动平均线是以每日收盘价计算的，而变异平均线则是用每日的开盘价、收盘价、最高价和最低价相加后除以4得出的数据计算平均线。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#lma-%E4%BD%8E%E4%BB%B7%E5%B9%B3%E5%9D%87%E7%BA%BF
#http://www.cftsc.com/quxiangzhibiao/588.html

#本文件：主要对VMA进行回测，需要数据包含收盘价['close']、开盘价['open']、最高价['high']、最低价['low']、波动率['pct_chg']
#测试时间：20220323



VV:=(HIGH+OPEN+LOW+CLOSE)/4;

VMA1:MA(VV,M1);

VMA2:MA(VV,M2);

VMA3:MA(VV,M3);

VMA4:MA(VV,M4);

VMA5:MA(VV,M5);


用法注释：

1.股价高于平均线，视为强势；股价低于平均线，视为弱势；

2.平均线向上涨升，具有助涨力道；平均线向下跌降，具有助跌力道；

3.二条以上平均线向上交叉时，买进；

4.二条以上平均线向下交叉时，卖出；

5.VMA 比一般平均线的敏感度更高，消除了部份平均线落后的缺陷。



#20220323
上传version1.0