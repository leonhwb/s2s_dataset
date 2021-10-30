from .main import RealTimeGribFileConfig, Param, ReforecastGrib_OnTheFly_FileConfig
from .reforecast_babj import Download_BABJ_Reforecast
from .reforecast_ecmf import Download_ECMF_Reforecast
from .checker import DownloadChecker


def S2SRealtimeDownloader(data_center: Param.data_center, number=0):
    """
    工厂模式生成 相应的S2S实时预报数据的下载器
    number=0表示控制模式下载
    number>=1表示扰动模式下载，并需要指定第几个扰动成员
    """
    if number == 0:
        if data_center == 'ecmf':
            from .realtime_ecmf_cf import Download_ECMF_CF_Realtime
            return Download_ECMF_CF_Realtime()
        elif data_center == 'kwbc':
            from .realtime_kwbc_cf import Download_KWBC_CF_Realtime
            return Download_KWBC_CF_Realtime()
        elif data_center == 'babj':
            from .realtime_babj_cf import Download_BABJ_CF_Realtime
            return Download_BABJ_CF_Realtime()
        else:
            raise Exception(f'{data_center}的近实时预报控制成员cf的数据下载器还没有开发')
    elif 1 <= number <= RealTimeGribFileConfig.pfEnsNums[data_center]:
        if data_center == 'ecmf':
            from .realtime_ecmf_pf import Download_ECMF_PF_Realtime
            return Download_ECMF_PF_Realtime(number)
        elif data_center == 'kwbc':
            from .realtime_kwbc_pf import Download_KWBC_PF_Realtime
            return Download_KWBC_PF_Realtime(number)
        elif data_center == 'babj':
            from .realtime_babj_pf import Download_BABJ_PF_Realtime
            return Download_BABJ_PF_Realtime(number)
        else:
            raise Exception(f'{data_center}的近实时预报扰动成员pf的数据下载器还没有开发')
    else:
        raise ValueError(f'成员号{number}错误')


def S2SReforeacstDownloader(data_center: Param.data_center, number=0):
    """工厂模式"""
    if data_center == "ecmf":
        return Download_ECMF_Reforecast(number=number)
    elif data_center == "babj":
        return Download_BABJ_Reforecast(number=number)
    else:
        raise Exception(f"{data_center}的会算数据下载器还没有开发")