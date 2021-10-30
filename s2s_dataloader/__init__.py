from .realtime_ecmf import ECMF_Realtime
from .realtime_babj import BABJ_Realtime
from .realtime_kwbc import KWBC_Realtime
from .template import S2SRealtimeBase
from .reforecast_ecmf import ECMF_Reforecast
from .s2s_download import DownloadChecker, S2SRealtimeDownloader, S2SReforeacstDownloader

__all__ = ['S2SRealtime',
           'S2SRealtimeBase',
           'S2SReforecast',
           "DownloadChecker",
           "S2SRealtimeDownloader",
           "S2SReforeacstDownloader"
           ]

"""
单子模式（在多进程下可能不是，主要是为了减少内存开销），工厂模式
"""

__babj_realtime = BABJ_Realtime()
__kwbc_realtime = KWBC_Realtime()
__ecmf_realtime = ECMF_Realtime()
__ecmf_reforecst = ECMF_Reforecast()


def S2SRealtime(data_center):
    if data_center == 'babj':
        return __babj_realtime
    elif data_center == 'ecmf':
        return __ecmf_realtime
    elif data_center == 'kwbc':
        return __kwbc_realtime
    else:
        raise ValueError(f'{data_center}数据读取器不存在')


def S2SReforecast(data_center):
    if data_center == 'ecmf':
        return __ecmf_reforecst
    else:
        raise ValueError(f'{data_center}数据读取器不存在')
