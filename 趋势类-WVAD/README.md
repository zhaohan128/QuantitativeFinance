#通达信WVAD-威廉变异离散量
#威廉变异离散量（WVAD）由拉里·威廉姆斯（Larry Williams）所创，是一种将成交量加权的量价指标。用于测量从开盘价至收盘价期间，买卖双方各自爆发力的程度。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#wvad-%E5%A8%81%E5%BB%89%E5%8F%98%E5%BC%82%E7%A6%BB%E6%95%A3%E9%87%8F
#http://cftsc.com/liangjiazhibiao/655.html

#本文件：主要对WVAD进行回测，需要数据包含收盘价['close']、开盘价['open']、最高价['high']、最低价['low']、成交量['volume']、波动率['pct_chg']
#测试时间：20220315


指标源代码

(CLOSE-OPEN)/(HIGH-LOW)*VOL

计算公式

1.A=当天收盘价-当天开盘价

2.B=当天最高价-当天最低价

3.C=A/B*成交量

4.WVAD=N日ΣC

5.MAWVAD=WVAD的M日简单移动平均

用法注释：

1.WVAD由下往上穿越0 轴时，视为长期买进信号；

2.WVAD由上往下穿越0 轴时，视为长期卖出信号；

3.当ADX 低于±DI时，本指标失去效用；

4.长期使用WVAD指标才能获得最佳利润；

5.本指标可与EMV 指标搭配使用。



#20220315
上传version1.0