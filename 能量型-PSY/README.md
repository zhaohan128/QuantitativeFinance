#通达信PSY-心理线
#PCNT幅度比指标是考察股票的涨跌幅度代替涨跌值的大小，有利于判断股票的活跃程度。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#pcnt-%E5%B9%85%E5%BA%A6%E6%AF%94
#https://www.zcaijing.com/jdjszb/263725.html

#本文件：主要对PSY进行回测，需要数据包含收盘价['close']
#测试时间：20220318

指标源代码

PSY:COUNT(CLOSE>REF(CLOSE,1),N)/N*100;

PSYMA:MA(PSY,M);

用法注释：

1.PSY>75，形成Ｍ头时，股价容易遭遇压力；

2.PSY<25，形成Ｗ底时，股价容易获得支撑；

3.PSY 与VR 指标属一组指标群，须互相搭配使用。

#20220318
上传version1.0
