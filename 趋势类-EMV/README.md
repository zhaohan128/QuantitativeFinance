#国泰君安EMV-简易波动指标
#将价格与成交量的变化，结合成一个指标，观察市场在缺乏动力情况下的移动情形。较少的成交量可以向上推动股价时，则EMV值会升高；
#同样的，较少的成交量可以向下推落股价时，EMV的值会降低。
#但是，如果股价向上或向下推动股价，需要大成交量支持时，则EMV会趋向于零；为克服EMV信号频繁，EMVA(平均值) 可将之平滑化，排除短期信号。

#相关资料：http://blog.sina.com.cn/s/blog_4bdeaafc0100g21d.html
#https://quant.gtja.com/data/dict/technicalanalysis#emv-%E7%AE%80%E6%98%93%E6%B3%A2%E5%8A%A8%E6%8C%87%E6%A0%87

#本文件：主要对EMV进行回测，需要数据包含成交量['volume']、收盘价['close']、最高价['high']、最低价['low']、波动率['pct_chg']

#测试时间：20220310

###应用

1. 当EMV/EMVA向上穿越零轴时，买进时机。

2. 当EMV/EMVA向下穿越零轴时，卖出时机。

3. 当EMV指标由下往上穿越EMVA指标时，是买入信号。

4. 当EMV指标由上往下穿越EMVA指标时，是卖出信号。