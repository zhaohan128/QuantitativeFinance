#通达信QR-强弱指标
#指标攀升表明个股走势渐强于大盘，后市看好；指标滑落表明个股走势弱于大盘，可择机换股。同时要结合大盘走势研判，应选择大盘转暖或走牛时出击。

#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#qr-%E5%BC%BA%E5%BC%B1%E6%8C%87%E6%A0%87
#https://www.55188.com/thread-3564868-1-1.html

#本文件：主要对QR进行回测，需要个股和指数数据包含收盘价['close']、波动率['pct_chg']
#测试时间：20220314


个股: (CLOSE-REF(CLOSE,N))/REF(CLOSE,N)*100;

大盘: (INDEXC-REF(INDEXC,N))/REF(INDEXC,N)*100;

强弱值:EMA(个股-大盘,2);


#20220314
上传version1.0