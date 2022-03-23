#通达信OBV-累积能量线
#累积能量线（英文on-balance volume, OBV）是一个广为运用的股票技术指标，它反映了股票价格变动与成交量的关系。OBV是由著名的股市技术分析大师Joe Granville最早推广使用的。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#obv-%E7%B4%AF%E7%A7%AF%E8%83%BD%E9%87%8F%E7%BA%BF
#http://www.danglanglang.com/gupiao/1297

#本文件：主要对OBV进行回测，需要数据包含收盘价['close']、成交量['volume']
#测试时间：20220321


指标公式：

如果今天的收盘价高于昨天的收盘价，那么OBV＝昨天的OBV＋今天的成交量

如果今天的收盘价低于昨天的收盘价，那么OBV＝昨天的OBV－今天的成交量

如果今天的收盘价等于昨天的收盘价，那么OBV＝昨天的OBV

用法注释：

1.股价一顶比一顶高，而OBV 一顶比一顶低，暗示头部即将形成；

2.股价一底比一底低，而OBV 一底比一底高，暗示底部即将形成；

3.OBV 突破其Ｎ字形波动的高点次数达5 次时，为短线卖点；

4.OBV 跌破其Ｎ字形波动的低点次数达5 次时，为短线买点；

5.OBV 与ADVOL、PVT、WAD、ADL同属一组指标群，使用时应综合研判。

#20220321
上传version1.0
