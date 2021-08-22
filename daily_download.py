import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta

from s2s_dataloader.s2s_download import S2SRealtimeDownloader, Param

"""
定时逐日下载
"""

back_day = 30

end_date = datetime.now() - timedelta(days=22)
periods = pd.date_range(end=end_date, period=back_day, freq='q')

single_pl_parameter = ('mn2t6', 'mx2t6', '2t', 'tp', '10u', '10v', 'msl', 'sp', 'wtmp')
multi_pl_parameter = (('w', 500),
                      ('t', 1000), ('t', 850),
                      ('q', 850),
                      ('gh', 500),
                      ('u', 200), ('u', 850),
                      ('v', 850))

for da in ('ecmf', 'babj', 'kwbc'):
    for ens in range(0, 3):  # 只下载0，1，2，3个模式

        download_tool = S2SRealtimeDownloader(da, number=ens)

        # 生成时间
        if da == 'kwbc':
            itr = tqdm(periods.strftime("%Y%m%d"))
        else:
            # babj ecmf 的 只有在周一周四才有下载
            itr = tqdm([d.strftime("%Y%m%d") for d in periods if d.dayofweek in [0, 3]])

        for dt in itr:
            for idx, param in enumerate(single_pl_parameter):
                download_tool.download(init_date=dt,
                                       no_cover=True,
                                       parameter=param,
                                       level=None)

            for idx, (param, level) in enumerate(multi_pl_parameter):
                download_tool.download(init_date=dt,
                                       no_cover=True,
                                       parameter=param,
                                       level=level)
