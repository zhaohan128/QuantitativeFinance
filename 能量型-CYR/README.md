#CYR-市场强弱
#CYR市场强弱指标是成本均线派生出的一个指标，就是13日成本均线的升降速度。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#cyr-%E5%B8%82%E5%9C%BA%E5%BC%BA%E5%BC%B1
#https://www.zcaijing.com/jdjszb/263724.html

#本文件：主要对CYR进行回测，需要包含成交额['amount']、成交量['volume']
#测试时间：20220316

DIVE=0.01X成交额（元）的N日加权移动平均＋成交量（手）的N日加权移动平均

CYR市场强弱=(DIVE÷昨日DIVE-1)X100

用法注释：

1.CYR是成本均线派生出的指标,是13日成本均线的升降幅度;

2.使用CYR可以对股票的强弱进行排序,找出其中的强势和弱势股票。


#20220316
上传version1.0
