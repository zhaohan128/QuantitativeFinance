#通达信VRSI-相对强弱量
#相对强弱量指标又名VRSI指标，是通过反映股价变动的四个元素：上涨的天数、下跌的天数、成交量增加幅度、成交量减少幅度来研判量能的趋势，预测市场供求关系和买卖力道，是属于量能反趋向指标之一。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#vrsi-%E7%9B%B8%E5%AF%B9%E5%BC%BA%E5%BC%B1%E9%87%8F
#http://cftsc.com/liangjiazhibiao/650.html#:~:text=%E7%9B%B8%E5%AF%B9%E5%BC%BA%E5%BC%B1%E9%87%8F%E6%8C%87%E6%A0%87%E5%8F%88,%E5%8F%8D%E8%B6%8B%E5%90%91%E6%8C%87%E6%A0%87%E4%B9%8B%E4%B8%80%E3%80%82

#本文件：主要对VRSI进行回测，需要数据包含成交量['volume']
#测试时间：20220321


指标源代码

VRSI(N)=SMA(MAX(VOL-REF(VOL,1),0),N,1)/SMA(ABS(VOL-REF(VOL,1)),N,1)*100

用法注释：

 1)VRSI>20为超买；VRSI<20为超卖

 2)VRSI以50为中轴线,大于50视为多头行情,小于50视为空头行情

 3)VRSI在80以上形成M头或头肩顶形态时,视为向下反转信号

 4)VRSI在20以上形成W头或头肩底形态时,视为向上反转信号

 5)VRSI向上突破其高点连线时,买进；VRSI向下跌破其低点连线时,卖出。


#20220321
上传version1.0
