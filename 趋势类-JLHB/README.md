#JLHB-绝路航标

#反趋势类选股指标。综合了动量观念、强弱指标与移动平均线的优点，在计算过程中主要研究高低价位与收市价的关系，反映价格走势的强弱和超买超卖现象。在市场短期超买超卖的预测方面又较敏感。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#jlhb-%E7%BB%9D%E8%B7%AF%E8%88%AA%E6%A0%87
#http://www.360doc.com/content/10/1128/21/235269_73250842.shtml

#本文件：主要对JLHB进行回测，需要包含收盘价['close']、最高价['high']、最低价['low']
#测试时间：20220314



反趋势类选股指标。综合了动量观念、强弱指标与移动平均线的优点，在计算过程中主要研究高低价位与收市价的关系，反映价格走势的强弱和超买超卖现象。
在市场短期超买超卖的预测方面又较敏感。

VAR1 := (CLOSE - LLV(LOW,60))/(HHV(HIGH,60)-LLV(LOW,60))*80

B = SMA(VAR1,N,1)

VAR2 = SMA(B,M,1)

JLHB = IF(CROSS(B,VAR2) AND B<40,50,0)



#20220314
上传version1.0
