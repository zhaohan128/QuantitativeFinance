#通达信DBQRV-对比强弱量
#相关资料：https://quant.gtja.com/data/dict/technicalanalysis#dbqrv-%E5%AF%B9%E6%AF%94%E5%BC%BA%E5%BC%B1%E9%87%8F
#http://rumen.southmoney.com/zhibiao/DBQRV/111896.html

#本文件：主要对DBQRV进行回测，需要数据包含成交量['volume']
#测试时间：20220321


指标公式：

ZS：（INDEXV-REF（INDEXV，N））/REF（INDEXV，N）;

GG：（VOL-REF（VOL，N））/REF（VOL，N）;

公式翻译为：

输出ZS：（大盘的成交量-N日前的大盘的成交量）/N日前的大盘的成交量

输出GG：（成交量（手）-N日前的成交量（手））/N日前的成交量（手）

用法注释：

对比强弱量指标包含有两条指标线,一条是对应指数量的强弱线。另外一条是个股成交量的强弱线。

当个股强弱线与指数强弱线发生金叉时，表明个股成交活跃过大盘。当个股强弱线与指数强弱线发生死叉时，表明个股活跃度开始弱于大盘。

对比强弱量指标也是一个短线指标。

注意：此指标使用到了大盘的数据，所以需要下载完整的日线数据,否则显示可能不正确


#20220321
上传version1.0
