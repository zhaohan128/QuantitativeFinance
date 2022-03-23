#通达信BBIBOLL-多空布林线
#多空布林线（BBIBOLL）是以多空线为中心线，多空线的标准差为带宽的轨道线。UPR线为压力线,对股价有压制作用，DWN线为支撑线,对股价具有支撑作用，BBIBOLL线为中轴线。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#bbiboll-%E5%A4%9A%E7%A9%BA%E5%B8%83%E6%9E%97%E7%BA%BF
#https://zhuanlan.zhihu.com/p/208738690

#本文件：主要对BBIBOLL进行回测，需要数据包含收盘价['close']、波动率['pct_chg']
#测试时间：20220322


指标源代码
CV:=CLOSE;

BBIBOLL:(MA(CV,3)+MA(CV,6)+MA(CV,12)+MA(CV,24))/4;

UPR:BBIBOLL+M*STD(BBIBOLL,N);

DWN:BBIBOLL-M*STD(BBIBOLL,N);


用法注释：
1.为BBI与BOLL的迭加；

2.高价区收盘价跌破BBI线，卖出信号；

3.低价区收盘价突破BBI线，买入信号；

4.BBI线向上，股价在BBI线之上，多头势强；

5.BBI线向下，股价在BBI线之下，空头势强。



#20220322
上传version1.0