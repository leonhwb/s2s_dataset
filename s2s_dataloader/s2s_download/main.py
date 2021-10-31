import json
import os
import sys
from abc import ABC, abstractmethod
from typing import List
import pandas as pd

file_dir = os.path.dirname(os.path.abspath(__file__))

"""
务必结合以下网址
https://confluence.ecmwf.int/display/S2S/Models
阅读以下代码
"""


def load_config():
    # 读取配置文件获取S2S数据的保存路径
    with open(os.path.join(file_dir, 'config.json'), 'r', encoding='utf8') as fp:
        json_data = json.load(fp)
        return json_data


__config__ = load_config()


class Param:
    data_center = ('babj', 'ecmf', 'kwbc')
    forecast_type = ('realtime', 'reforecast')
    data_type = ('cf', 'pf')
    single_level_parameter = ('mn2t6', 'mx2t6', '2t', 'tp',
                              '10u', '10v', 'msl', 'sp', 'wtmp')
    multi_level_parameter = ('u', 'v', 'w', 'gh', 'q', 't')
    parameter = single_level_parameter + multi_level_parameter

    @classmethod
    def separate_FactorLevel(cls, parameter_level: str):
        """
        除了10u、10v、2t之外，确保要素在前，等压层在后
        使用例子：
        separate_FactorLevel('2t') -> ('2t', None)
        separate_FactorLevel('u1000') -> ('u', 1000)
        separate_FactorLevel('6gh500') -> ('gh', 6500)
        """
        parameter_level = parameter_level.replace(' ', '')  # 去掉空格
        if parameter_level in cls.single_level_parameter:
            level = None
            parameter = parameter_level
        else:
            parameter = ''.join([s for s in parameter_level if str.isalpha(s)])
            if parameter not in cls.parameter:
                print(f'{parameter_level}中的{parameter}不在合法要素缩写{cls.parameter}中')

            level = ''.join([s for s in parameter_level if str.isdigit(s)])
            if level != '':
                level = int(level)
            else:
                raise NameError(f'{parameter_level}中没有关于等压层的数字')

            if parameter not in cls.parameter:
                raise NameError(f'{parameter_level}中的{parameter}不在合法要素缩写{cls.parameter}中')
        return parameter, level

    @classmethod
    def step(cls, data_center: str, parameter: str) -> int:
        """
        参考上级目录的readme说明，返回不同data_center和parameter的预报步长step
        海温要素缩写兼容sst和wtmp
        """
        step = 0
        if data_center == "ecmf":
            if parameter in ("mn2t6", "mx2t6"):
                step = 184  # ecmf的2m最高最低气温缺失第0天0时，缺失47天6、12、18时
            elif parameter == "tp":
                step = 185  # ecmf的累计降水缺少46天6、12、18时
            elif parameter == "wtmp" or parameter == "sst":
                step = 46  # ecmf的海温缺少了第0天
            else:
                step = 47

        elif data_center == "babj":
            if parameter in ("mn2t6", "mx2t6", "tp"):
                step = 240  # babj的mn2t6,mx2t6,tp缺失第0天0时，缺失61天6、12、18时。共61*4-4=240个场
            elif parameter in ("sst", "wtmp", "2t"):
                step = 60  # babj的海温wtmp和2t缺失第0天的数据
            else:
                step = 61

        elif data_center == "kwbc":
            if parameter in ("mn2t6", "mx2t6", "tp"):
                step = 176  # kwbc的mn2t6,mx2t6,tp缺失第0天0时，缺失44天6、12、18时
            elif parameter in ('10u', '10v', 'sp'):
                step = 44  # kwbc的10u,10v,sp缺失第0天的数据
            elif parameter in ("wtmp", "2t"):
                step = 43  # kwbc的海温wtmp和2t缺失第0,1天的数据
            else:
                step = 45

        return step


class HiddenPrints:
    """屏蔽内层函数的命令行输出"""

    def __init__(self, state):
        self.state = state

    def __enter__(self):
        if self.state:
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.state:
            sys.stdout.close()
            sys.stdout = self._original_stdout


class RealTimeGribFileConfig:
    __root__ = __config__['s2s_root']

    """
    S2S近实时预报数据下载的路径管理
    本类不做任何参数约束
    """
    forecast_type = 'realtime'

    pfEnsNums = {'ecmf': 50, 'kwbc': 15, 'babj': 3}  # 扰动模式的数量

    @classmethod
    def factor_dir(cls,
                   data_center: Param.data_center,
                   parameter: Param.parameter,
                   level=None,
                   number: int = None,
                   **kwargs) -> str:
        level = level if level is not None else ''
        return os.path.join(cls.__root__, data_center, cls.forecast_type, str(number), f'{parameter}{str(level)}')

    @classmethod
    def init_date_range(cls, **kwargs) -> List[str]:
        dir = cls.factor_dir(**kwargs)
        if os.path.exists(dir):
            return [f.split('_')[3] for f in os.listdir(dir) if f.endswith('.grib')]
        else:
            return []

    @classmethod
    def factor_save_filename(cls,
                             data_center: Param.data_center,
                             init_date: str,
                             parameter: Param.parameter,
                             number: int = None,
                             level=None) -> str:
        """
        s2s数据保存的格式时grib文件名
        init_date是YYYYMMDD形式
        """
        init_date = pd.to_datetime(init_date).strftime("%Y%m%d")
        level = level if level is not None else ''
        return f's2s_{data_center}_{number}_{init_date}_{parameter}{str(level)}.grib'

    @classmethod
    def factor_filepath(cls, **kwargs) -> str:
        """s2s数据保存的格式时grib文件名"""
        filepath = os.path.join(cls.factor_dir(**kwargs),
                                cls.factor_save_filename(**kwargs))
        return filepath


class RealTimeGribDownload(ABC):
    """
    控制成员和扰动成员分开下载
    扰动成员的不同成员分开单独下载
    """

    def __init__(self, data_center: Param.data_center, number: int = 0):
        assert data_center in Param.data_center

        self.number = number
        self.data_center = data_center

        if number == 0:
            self.data_type = 'cf'
        elif 1 <= number <= RealTimeGribFileConfig.pfEnsNums[data_center]:
            self.data_type = 'pf'
        else:
            raise ValueError(f'{data_center}没有成员{number}')

    def make_factor_dir(self, parameter: Param.parameter, level=None) -> str:
        """创建要素的保存目录，并返回目录"""
        assert parameter in Param.parameter, f'{parameter}不在合法的{Param.parameter}中'
        dir = RealTimeGribFileConfig.factor_dir(data_center=self.data_center,
                                                number=self.number,
                                                parameter=parameter,
                                                level=level)
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def factor_path(self, *, init_date: str, parameter: str, level=None):
        """这里没有参数检查，因为没有经过的create_factor_dir的参数检查就创建不了文件夹，返回grib文件路径将无效"""
        return RealTimeGribFileConfig.factor_filepath(data_center=self.data_center,
                                                      parameter=parameter,
                                                      level=level,
                                                      init_date=init_date,
                                                      number=self.number)

    @abstractmethod
    def retrieve_pressure_level(self, parameter: str, level: int, init_date: str, save_path: str) -> bool:
        """
        多层要素下载，但每次只下载一个等压层
        :param save_path: grib文件保存路径
        :param init_date: 起报日期，字符串，YYYYMMDD
        :param parameter: 要素，参考Param.parameter
        :param level: 等压层, 需要开发人员研究指定data_center和data_type的多层要素的等压层取值
        """
        pass

    @abstractmethod
    def retrieve_single_level(self, parameter: str, init_date: str, save_path: str) -> bool:
        """
        单层要素下载
        :param save_path: grib文件保存路径
        :param init_date: 起报日期，字符串，YYYYMMDD
        :param parameter: 要素，参考Param.parameter
        """
        pass

    def download(self, *, init_date: str, parameter: Param.parameter, level=None, no_cover=True,
                 is_print=False):
        """
        :param init_date: 起报日期，字符串，YYYYMMDD
        :param parameter: 要素，参考Param.parameter
        :param is_print: 是否输出ecmwfapi下载器的命令行输出信息
        :param level: 等压层
        :param no_cover: 默认不覆盖已经下载的文件
        :return: 下载成功返回True，否则返回False
        """
        save_path = self.factor_path(init_date=init_date, parameter=parameter, level=level)
        if os.path.exists(save_path) and no_cover:  # 文件已经被下载且指定不覆盖
            return True
        # 文件不存在或者覆盖下载，则执行下载
        self.make_factor_dir(parameter=parameter, level=level)

        with HiddenPrints(not is_print):
            try:
                if level:
                    state = self.retrieve_pressure_level(parameter=parameter,
                                                         level=level,
                                                         init_date=init_date,
                                                         save_path=save_path)
                else:
                    state = self.retrieve_single_level(init_date=init_date,
                                                       parameter=parameter,
                                                       save_path=save_path)
                message = "success"
            except Exception as e:
                message = e
                state = False

        return state, message


class ReforecastGrib_OnTheFly_FileConfig:
    __root__ = __config__['s2s_root']

    """
    S2S回算数据下载的路径管理
    本类不做任何参数约束
    
    每次都下载所有历史年份的数据
    init_date是运行模型的年份，假设init_date是2021-07-01
        > 产生以下历史日期的预报数据。
        > 2020-07-01、2019-0701、...、2001-07-01
        > 共有20个起报日期，都是7月1日。从这20个起报日期，产生11个预报成员，每个预报成员预报共47，与近实时预报相同。
    则在下载时，固定某个成员，把2020-07-01、2019-07-01、...、2001-07-01的历史上的预报都一次性下载到一个文件夹
    
    注意：这里的init_date实际上是下载页面中的Model version date
    """

    forecast_type = 'reforecast'
    data_center = ('ecmf', 'babj')
    pfEnsNums = {'ecmf': 10, 'babj': 3}  # 扰动模式的数量
    rfc_periods = {'ecmf': 20, 'babj': 15}  # 回算历史年数

    @classmethod
    def factor_dir(cls,
                   data_center: Param.data_center,
                   parameter: Param.parameter,
                   level=None,
                   number: int = None,
                   **kwargs) -> str:
        level = level if level is not None else ''
        return os.path.join(cls.__root__,
                            data_center,
                            cls.forecast_type,
                            str(number), f'{parameter}{str(level)}')

    @classmethod
    def init_date_range(cls, **kwargs) -> List[str]:
        dir = cls.factor_dir(**kwargs)
        if os.path.exists(dir):
            return [f.split('_')[4] for f in os.listdir(dir) if f.endswith('.grib')]
        else:
            return []

    @classmethod
    def factor_save_filename(cls,
                             data_center: Param.data_center,
                             init_date: str,
                             parameter: Param.parameter,
                             number: int = None,
                             level=None) -> str:
        """
        s2s数据保存的格式时grib文件名
        init_date是YYYYMMDD形式
        """
        init_date = pd.to_datetime(init_date).strftime("%Y%m%d")
        level = level if level is not None else ''
        return f's2s_{data_center}_{cls.forecast_type}_{number}_{init_date}_{parameter}{str(level)}.grib'

    @classmethod
    def factor_filepath(cls, **kwargs) -> str:
        """s2s数据保存的格式时grib文件名"""
        filepath = os.path.join(cls.factor_dir(**kwargs),
                                cls.factor_save_filename(**kwargs))
        return filepath


class ReforecastGrib_OnTheFly_Download(ABC):
    """
    控制成员和扰动成员分开下载
    扰动成员的不同成员分开单独下载
    """

    def __init__(self, data_center: Param.data_center, number: int = 0):
        assert data_center in ReforecastGrib_OnTheFly_FileConfig.data_center

        self.number = number
        self.data_center = data_center
        self.rfc_nums = ReforecastGrib_OnTheFly_FileConfig.rfc_periods[self.data_center]

        if number == 0:
            self.data_type = 'cf'
        elif 1 <= number <= ReforecastGrib_OnTheFly_FileConfig.pfEnsNums[data_center]:
            self.data_type = 'pf'
        else:
            raise ValueError(f'{data_center}没有成员{number}')

    def hindcast_dates(self, init_date: str) -> list:
        dt = pd.to_datetime(init_date).strftime("%Y-%m-%d")
        cal_year = int(init_date[:4])

        s = [init_date.replace(str(cal_year), str(y))
             for y in range(cal_year - self.rfc_nums, cal_year)]
        return s

    def make_factor_dir(self, parameter: Param.parameter, level=None) -> str:
        """创建要素的保存目录，并返回目录"""
        assert parameter in Param.parameter, f'{parameter}不在合法的{Param.parameter}中'
        dir = ReforecastGrib_OnTheFly_FileConfig.factor_dir(data_center=self.data_center,
                                                            number=self.number,
                                                            parameter=parameter,
                                                            level=level)
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def factor_path(self, *, init_date: str, parameter: str, level=None):
        """这里没有参数检查，因为没有经过的create_factor_dir的参数检查就创建不了文件夹，返回grib文件路径将无效"""
        return ReforecastGrib_OnTheFly_FileConfig.factor_filepath(data_center=self.data_center,
                                                                  parameter=parameter,
                                                                  level=level,
                                                                  init_date=init_date,
                                                                  number=self.number)

    @abstractmethod
    def retrieve_pressure_level(self, parameter: str, level: int, init_date: str, save_path: str) -> bool:
        """
        多层要素下载，但每次只下载一个等压层
        :param save_path: grib文件保存路径
        :param init_date: 起报日期，字符串，YYYYMMDD
        :param parameter: 要素，参考Param.parameter
        :param level: 等压层, 需要开发人员研究指定data_center和data_type的多层要素的等压层取值
        """
        pass

    @abstractmethod
    def retrieve_single_level(self, parameter: str, init_date: str, save_path: str) -> bool:
        """
        单层要素下载
        :param save_path: grib文件保存路径
        :param init_date: 起报日期，字符串，YYYYMMDD
        :param parameter: 要素，参考Param.parameter
        """
        pass

    def download(self, *, init_date: str, parameter: Param.parameter, level=None, no_cover=True,
                 is_print=False):
        """
        :param init_date: 起报日期，字符串，YYYYMMDD
        :param parameter: 要素，参考Param.parameter
        :param level: 等压层
        :param is_print: 是否输出ecmwfapi下载器的命令行输出信息
        :param no_cover: 默认不覆盖已经下载的文件
        :return: 下载成功返回True，否则返回False
        """
        save_path = self.factor_path(init_date=init_date, parameter=parameter, level=level)
        if os.path.exists(save_path) and no_cover:  # 文件已经被下载且指定不覆盖
            return True
        # 文件不存在或者覆盖下载，则执行下载
        self.make_factor_dir(parameter=parameter, level=level)

        with HiddenPrints(not is_print):
            try:
                if level:
                    state = self.retrieve_pressure_level(parameter=parameter,
                                                         level=level,
                                                         init_date=init_date,
                                                         save_path=save_path)
                else:
                    state = self.retrieve_single_level(init_date=init_date,
                                                       parameter=parameter,
                                                       save_path=save_path)
                message = "success"
            except Exception as e:
                message = e
                state = False

        return state, message


if __name__ == "__main__":
    pass
