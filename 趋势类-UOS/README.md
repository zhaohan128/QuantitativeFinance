#通达信UOS-终极指标

#终极波动（UOS）指标，亦称终极指标，由拉里·威廉姆斯（Larry Williams）所创。他认为现行使用的各种振荡指标，对于周期参数的选择相当敏感。
#不同市况、不同参数设定的振荡指标，产生的结果截然不同。因此，选择最佳的参数组合，成为使用振荡指标之前最重要的一道手续。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#uos-%E7%BB%88%E6%9E%81%E6%8C%87%E6%A0%87
#http://cftsc.com/quxiangzhibiao/590.html

#本文件：主要对UOS进行回测，需要数据包含收盘价['close']、最高价['high']、最低价['low']、波动率['pct_chg']
#测试时间：20220315


TH:=MAX(HIGH,REF(CLOSE,1));

TL:=MIN(LOW,REF(CLOSE,1));

ACC1:=SUM(CLOSE-TL,N1)/SUM(TH-TL,N1);

ACC2:=SUM(CLOSE-TL,N2)/SUM(TH-TL,N2);

ACC3:=SUM(CLOSE-TL,N3)/SUM(TH-TL,N3);

UOS:(ACC1*N2*N3+ACC2*N1*N3+ACC3*N1*N2)*100/(N1*N2+N1*N3+N2*N3);

MAUOS:EMA(UOS,M);

用法注释：

1.UOS 上升至50～70的间，而后向下跌破其Ｎ字曲线低点时，为短线卖点；

2.UOS 上升超过70以上，而后向下跌破70时，为中线卖点；

3.UOS 下跌至45以下，而后向上突破其Ｎ字曲线高点时，为短线买点；

4.UOS 下跌至35以下，产生一底比一底高的背离现象时，为底部特征；

5.以上各项数据会因个股不同而略有不同，请利用参考线自行修正。



#20220315
上传version1.0