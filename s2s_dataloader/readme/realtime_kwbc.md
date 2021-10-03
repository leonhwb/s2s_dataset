# KWBC数据
## National Centers for Environmental Prediction
### 要素的起报时间、预报时效，预报间隔

0~44天，共45天，每个模式（cf或pf）共预报未来44个场（第0天不算预报）。   
参考：https://confluence.ecmwf.int/display/S2S/NCEP+model+description       
 - 海温wtmp和2t缺失第0,1天的数据,共43个场。  
 - 10u,10v,sp缺失第0天的数据,共44个场。          
 - mn2t6,mx2t6,tp的预报间隔是6小时。      
    * mn2t6,mx2t6,tp缺失第0天0时，缺失44天6、12、18时。共45*4-4=176个场。
    

### 注意：kwbc的起报日期不是周一和周四，是每天都有！！
### 注意：kwbc的要素w(垂直速度)只有500hpa，这与ecmf和babj不同!!!!


### 要素后处理
- kwbc的近实时预报数据，逐6小时的要素后处理：
     * 累积降水tp：    
        Validity：accumulated from the beginning of the forecast   
         从第0个时次起，逐6小时累积的降水量，取出所有的00:00场做差值，1day00:00和0day00:00相减得到第0天总降雨量
        (参考网址：https://confluence.ecmwf.int/display/S2S/S2S+Total+Precipitation)
     * 最高气温mx2t6,最低气温mn2t6：  
     官网下载页面描述为：数据中每个valid_time的过去6小时的最高最低气温
        + Maximum temperature at 2 metres in the last 6 hours    
        Validity:Maximum determined over the last 6 hours  
        (参考网址：https://confluence.ecmwf.int/display/S2S/S2S+Surface+Air+Maximum+temperature)
        + Minimum temperature at 2 metres in the last 6 hours    
        Validity:Minimum determined over the last 6 hours  
        (参考网址：https://confluence.ecmwf.int/display/S2S/S2S+Surface+air+minimum+temperature)   
     如果要求出第0天24小时最高气温，只需要取出第6，12，18，24这4个场求最大值即可。最低气温同理。  

- 处理后：
    + tp由176个场变为44个场，表示第0~43日的场，第0天的降水量是06:00~23:59的累积降水量
    + mx2t6,mn2t6由176个场变为44个场，表示第0~43日的场
