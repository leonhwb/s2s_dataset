import sys
import os
from .main import Param
from .main import ReforecastGrib_OnTheFly_FileConfig as ReforecastConfig
from .main import RealTimeGribFileConfig as RealtimeConfig
import xarray as xr

"""用于检测下载文件的大小"""


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


class DownloadChecker:
    def __init__(self):
        self.__message__ = ""
        self.__data__ = None
        self.__state__ = None

    def clear(self):
        self.__data__ = None
        self.__message__ = ""
        self.__state__ = None

    def check(self, grib_path: str, is_print=False) -> bool:
        """
        show_error展示cfgrib的错误信息，如果有的话
        """
        self.clear()

        if not os.path.exists(grib_path):
            self.__message__ = "文件不存在"
            self.__state__ = False  # 文件不存在，即下载错误
        else:
            data = None  # 打开文件
            try:
                if not is_print:
                    with HiddenPrints():  # 屏蔽cfgrib的错误信息
                        data = xr.open_dataarray(grib_path, engine="cfgrib")
                else:
                    data = xr.open_dataarray(grib_path, engine="cfgrib")
            except:
                pass

            if data is None:
                self.__message__ = "文件读取失败，需要重新下载"
                self.__state__ = False
            else:
                self.__data__ = data  # 暂存数据
                self.__message__ = "文件完整"
                self.__state__ = True

        return self.__state__

    def checkRealtime(self,
                      data_center: str,
                      init_date: str,
                      parameter: str,
                      level: int,
                      number: int = 0,
                      is_print=False):
        # 测试文件打开的情况
        grib_path = RealtimeConfig.factor_filepath(data_center=data_center,
                                                   init_date=init_date,
                                                   parameter=parameter,
                                                   number=number,
                                                   level=level)

        if not self.check(grib_path, is_print=is_print):
            return False

        valid_step = Param.step(data_center=data_center, parameter=parameter)
        if len(self.__data__["step"]) != valid_step:
            self.__message__ = f'{data_center}的要素{parameter}共预报{valid_step}个场，' \
                                 f'下载的文件中只有{len(self.__data__["step"])}个'
            self.__state__ = False
            return False

        return self.__state__, self.__message__

    def checkReforecast(self, data_center: str,
                        run_date: str,
                        parameter: str,
                        level: int,
                        number: int = 0,
                        is_print=False):
        grib_path = ReforecastConfig.factor_filepath(data_center=data_center,
                                                     init_date=run_date,
                                                     parameter=parameter,
                                                     number=number,
                                                     level=level)
        if not self.check(grib_path, is_print=is_print):
            return False

        if data_center in ("babj", "ecmf"):
            history_year_num = len(self.__data__["time"])
            valid_rfc_year_num = ReforecastConfig.rfc_periods[data_center]
            if history_year_num != valid_rfc_year_num:
                self.__message__ = f"{data_center}回算{valid_rfc_year_num}年，下载文件中只有{history_year_num}年"
                self.__state__ = False
                return False

        valid_step = Param.step(data_center=data_center, parameter=parameter)
        if len(self.__data__["step"]) != valid_step:
            self.__message__ = f'{data_center}的要素{parameter}共预报{valid_step}个场，' \
                                 f'下载的文件中只有{len(self.__data__["step"])}个'
            self.__state__ = False
            return False

        return self.__state__, self.__message__
