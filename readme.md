# 说明
> 对于延伸期研究，项目文档和ECMWF的官方文档时能解决大部分问题，但仍需要花时间研究数据       
> 综述《中国气象局S2S数据归档中心设计及关键技术_肖华东》 

需要在s2s_dataloader\s2s_download下创建文件config.json，配置下载的路径
```json
{
  "s2s_root": "..."
}
```

## S2S数据下载
 - 利用欧洲中心的ecmwfapi库进行下载。安装方式：https://pypi.org/project/ecmwf-api-client/  
 - ecmwfapi需要在个人账号下配置密钥文件.ecmwfapirc,相关教程可以网上搜索，十分简单。
 - 欧洲中心的最新数据一般要等3周才能开放下载：This dataset is available with 3 week delay.  
    (参考：https://confluence.ecmwf.int/display/UDOC/MARS+access+restrictions中的Restricted access to S2S)

### 官方文档 
s2s资料官方文档（需要详细参考）：https://confluence.ecmwf.int/display/S2S   
- 下载速度说明： https://confluence.ecmwf.int/display/WEBAPI/S2S+reforecasts+retrieval+efficiency   
- 下载页面：https://apps.ecmwf.int/datasets/data/s2s-realtime-instantaneous-accum-ecmf/levtype=sfc/type=cf/
- 要素编码表格：https://apps.ecmwf.int/codes/grib/param-db 

## 回算数据和预报数据的参数说明
详细参考：   
模型版本：https://confluence.ecmwf.int/display/S2S/Models     
https://confluence.ecmwf.int/display/S2S/A+brief+description+of+reforecasts   

### 近实时预报数据

| 数据中心 | 预报时长 | 成员数 | 起报频率 |
| -------- | -------- | ------ | ---------- |
| ecmf     | day 0-46 | 50+1    | 周一，周四 |
| babj     | day 0-60 | 3+1   | 周一，周四 |
| kwbc     | day 0-44 | 15+1   | 每日     |
 
### 回算资料  

| 数据中心 | 预报时长 | 成员数 | 起报频率 | 回算年数 |
| -------- | -------- | ------ | ---------- | -------- |
| ecmf     | day 0-46 | 3+1    | 周一，周四 | 过去20年 |
| babj     | day 0-60 | 10+1   | 周一，周四 | 过去15年 |

ecmf和babj回算数据是On the Fly模式
以欧洲中心为例（可以在ECMWF的S2S下载也页面找规律）：
> 2021-07-01起报，产生51个近实时预报成员，每个成员预报2021-07-01 ~ 2021-08-16共47天的预报。  
> 同时，还会产生以下历史日期的预报数据（Hindcast date）。
> 2020-07-01、2019-0701、...、2001-07-01
> 共有20个起报日期，都是7月1日。从这20个起报日期，产生11个预报成员，每个预报成员预报共47，与近实时预报相同。


kwbc的回算数据是固定的，这里不累赘，网页上一目了然：   
https://apps.ecmwf.int/datasets/data/s2s-reforecasts-instantaneous-accum-kwbc/levtype=sfc/type=cf/


## 名称说明
多层要素：gh、t、u、v、q、w   
单层要素：10u、10v、msl、wtmp、sp、mx2t6、mn2t6、2t、tp   
要素名称统一使用规范参考：https://confluence.ecmwf.int/display/S2S/Parameters  
> 下载的babj,ecmf的grib文件中，2t的变量名是t2m，10u的变量名是u10，10v的变量名是v10，wtmp的变量名是sst
 
| 英文名 | 含义 | 
| :-----| :---- | 
| parameter | 特指下载的要素，官网定义。例如2t、gh、t等 | 
| factor,factor_level | 使用的要素，范围更广，包含parameter，还包含gh500、t850等 | 
| level | 等压层，仅用于多层要素。例如500hpa、850hpa | 
| data_center | 产生数据的中心。例如babj、kwbc | 
| real time | 近实时预报资料 | 
| reforecast | 回算资料 | 

S2S数据有多个数据来源data_center： 

| 数据中心 | 机构缩写 | 归档缩写 | 
| :-----: | :----: | :----: |
| 中国气象局 | CMA | babj |
| 欧洲中期天气预报中心 | ECMWF | ecmf |
| 美国国家环境预测中心 | NCEP | kwbc |

 
## 下载遵循原则
 1. 要素分开下载
 2. 多层要素不同level分开下载
 3. 控制模式cf和扰动模式pf分开下载
 4. 下载全部step   
 5. 扰动成员的不同成员分开单独下载
 6. 控制成员和扰动成员分开下载
 7. 下载时候，同时下载所有回算日期
 > 1-3 为了保证读取速度（某些层频繁使用，控制模式频繁使用）  
 > 4 为了数据完整性
 > 5,6考虑下载速度，参考： https://confluence.ecmwf.int/display/WEBAPI/S2S+reforecasts+retrieval+efficiency 
 > 5 和周柏荃老师确认过，暂时得到结论：不同起报日期的同一number的扰动成员，扰动方案不变


## 不同中心的之间的S2S资料差异
 1. 起报日期，ecmf和babj每周一和周四起报一次；kwbc每天都有起报
 2. 要素垂直速度w，ecmf和babj有10层；kwbc只有1层（500hpa）
 3. 预报时效的不同
 4. 集合成员数量   
 5. 某些要素的预报场第0天的确实情况   
 - 上述差异特别是第5点，影响数据的后处理，请认真阅读S2SDataset.s2s_download和S2SDataset.s2s_dataloader下的脚本  
 - 对于不同中心的S2S资料的后处理过程在S2SDataset.s2s_dataloader的各个子文件夹下的readme.md有详细说明，务必认真阅读
 
    
## S2S数据存放
### 文件夹结构：
```
📂s2s_source # s2s_source路径在项目目录/s2s_download/config.json下
 ┣📂ecmf
 ┃ ┣📜realTime
 ┃ ┃ ┣📜成员0（控制模式）
 ┃ ┃ ┃ ┣要素1
 ┃ ┃ ┃ ┣...
 ┃ ┃ ┃ ┗要素N
 ┃ ┃ ┣📜扰动成员1（扰动模式）
 ┃ ┃ ┣...
 ┃ ┃ ┗📜扰动成员N（扰动模式）
 ┃ ┃
 ┃ ┣ 📜reforecast
 ┃ ┃
 ┣ 📂babj
 ┣ 📂kwbc
 ┣ 📂 
```
