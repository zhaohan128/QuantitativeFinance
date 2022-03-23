#通达信VPT-量价曲线
#量价曲线VPT（英文：volume price trend）是一个重要的股票技术指标，它反映了成交量与价格之间的关系。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#vpt-%E9%87%8F%E4%BB%B7%E6%9B%B2%E7%BA%BF
#https://zhidao.baidu.com/question/461969533005870805.html

#本文件：主要对VPT进行回测，需要数据包含收盘价['close']、成交量['volume']、波动率['pct_chg']
#测试时间：20220315


VPT:SUM(VOL*(CLOSE-REF(CLOSE,1))/REF(CLOSE,1),N);

MAVPT:MA(VPT,M)

用法注释：

1.VPT 由下往上穿越0 轴时，为买进信号；

2.VPT 由上往下穿越0 轴时，为卖出信号；

3.股价一顶比一顶高，VPT 一顶比一顶低时，暗示股价将反转下跌；

4.股价一底比一底低，VPT 一底比一底高时，暗示股价将反转上涨；

5.VPT 可搭配EMV 和WVAD指标使用效果更佳。



#20220315
上传version1.0