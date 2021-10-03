# ECMF数据
## European Centre for Medium-Range Weather Forecasts
### 要素的起报时间、预报时效，预报间隔
 
0~46天，共47天，每个模式（cf或pf）共预报未来46个场。  
参考：https://confluence.ecmwf.int/display/S2S/Models  
海温wtmp缺失第0天的数据。      
mn2t6、mx2t6、tp的预报间隔是6小时。      
* mn2t6,mx2t6缺失第0天0时，缺失47天6、12、18时。故预报未来47*4-4=184个场。
* tp缺失46天6、12、18时。故预报未来47*4-3=185个场。

# 注意
10u 和 10v的20200102之后，改为逐6小时预报，但只需要下载每日0时


### 要素后处理
- ecmf的近实时预报数据，逐6小时的要素后处理：
     * 累积降水tp：    
        Validity：accumulated from the beginning of the forecast   
        从第0个时次起，逐6小时累积的降水量，取出所有的00:00场做差值，1day00:00和0day00:00相减得到第0天总降雨量
        (参考网址：https://confluence.ecmwf.int/display/S2S/S2S+Total+Precipitation)
        > 欧洲中心的累积降水，做差分后有负数，不知道是什么原因
     * 最高气温mx2t6,最低气温mn2t6：  
     官网下载页面描述为：数据中每个valid_time的过去6小时的最高最低气温
        + Maximum temperature at 2 metres in the last 6 hours    
        Validity:Maximum determined over the last 6 hours  
        (参考网址：https://confluence.ecmwf.int/display/S2S/S2S+Surface+Air+Maximum+temperature)
        + Minimum temperature at 2 metres in the last 6 hours    
        Validity:Minimum determined over the last 6 hours  
        (参考网址：https://confluence.ecmwf.int/display/S2S/S2S+Surface+air+minimum+temperature)   
     如果要求出第0天24小时最高气温，只需要取出第6，12，18，24这4个场求最大值即可。最低气温同理。  
  
- 处理后
    + tp由185个场变为46个场,表示第0~45天的逐日降水
    + mx2t6,mn2t6由184个场变为46,表示第0~45天的逐日最高最低温度