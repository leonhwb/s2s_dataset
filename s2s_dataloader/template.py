from .s2s_download import RealTimeGribFileConfig, Param
import os
from typing import List
import xarray as xr


class S2SRealtimeBase:
    """
    读取S2S数据的近实时预报数据
    读取原则：
        不同数据中心的数据分开读取
    在该类中，所有关于要素的查询使用以下方式：
        字符串：parameter + level
        例如：
            ①单层要素：'mn2t6', 'mx2t6', '2t', 'tp', '10u', '10v', 'msl', 'sp', 'wtmp'
            ②多层要素：'u1000', 'v850', 'w500', 'gh500', 'q925', 't1000'等
            输入的parameter+level字符串会被解码处parameter和level信息，解码方式参照Param.separate_FactorLevel
    """

    def __init__(self, data_center: Param.data_center, ):
        self.__data_center = data_center  # 在单子模式下安全
        assert data_center in Param.data_center, f'{data_center}不在{Param.data_center}内'

    @property
    def ensNums(self) -> int:
        return RealTimeGribFileConfig.pfEnsNums[self.__data_center] + 1  # 扰动成员数 + 控制成员数

    @property
    def data_center(self) -> str:
        return self.__data_center  # 字符串是不可变类型，安全

    def init_date_range(self, *parameter_levels, number: int = 0) -> List[str]:
        ans = {}
        for par_ll in parameter_levels:
            parameter, level = Param.separate_FactorLevel(par_ll)
            _period = RealTimeGribFileConfig.init_date_range(data_center=self.__data_center,
                                                             parameter=parameter,
                                                             number=number,
                                                             level=level)
            ans = ans.intersection(set(_period)) if ans != {} else set(_period)
        ans = list(ans)
        ans.sort()
        return ans

    def open_source(self, parameter_level: str, init_date: str, number: int = 0) -> xr.DataArray:
        parameter, level = Param.separate_FactorLevel(parameter_level)
        grib_path = RealTimeGribFileConfig.factor_filepath(data_center=self.__data_center,
                                                           init_date=init_date,
                                                           number=number,
                                                           parameter=parameter,
                                                           level=level)
        if os.path.exists(grib_path):
            data = xr.open_dataarray(grib_path, engine='cfgrib')
            data.name = parameter_level  # 统一命名 parameter + level

            for name in ['meanSea', 'heightAboveGround', 'surface', 'entireAtmosphere', 'isobaricInhPa']:
                if name in data.coords.keys():
                    data = data.drop(name)

            return data

    def post_process(self, dataarray: xr.DataArray, parameter: str):
        """这里没有逐6小时预报的数据处理成为逐24小时，每个中心资料脚本中继承该类，重写这个方法，把所有数据处理成逐24小时"""
        return dataarray

    def load(self, parameter_level: str, init_date: str, number: int = 0) -> xr.DataArray:
        data = self.open_source(parameter_level=parameter_level,
                                init_date=init_date,
                                number=number)
        if data is not None:
            parameter = Param.separate_FactorLevel(parameter_level)[0]

            # 后处理，逐6小时预报的数据处理成为逐24小时
            data = self.post_process(dataarray=data, parameter=parameter)

            if parameter in ('t', '2t', 'wtmp', 'mn2t6', 'mx2t6'):
                data = data - 273.15  # 温度转换

        return data

    def pack(self, *parameter_levels, init_date: str, number: int = 0) -> xr.Dataset:
        """
        读取过程中发现某个parameter_levels不存在，则返回None，
        使用此方法前请首先使用init_date_range进行检查
        """
        ens = []
        for param_ll in parameter_levels:
            _da = self.load(init_date=init_date,
                            parameter_level=param_ll,
                            number=number)
            if _da is None:
                break
            ens.append(_da)

        if len(parameter_levels) == len(ens):
            ens = xr.merge(ens, join="inner", combine_attrs="drop_conflicts")
            return ens


class S2SReforecastBase:
    """
    读取S2S数据的回算资料
    在该类中，所有关于要素的查询使用以下方式：
        字符串：parameter + level
        例如：
            ①单层要素：'mn2t6', 'mx2t6', '2t', 'tp', '10u', '10v', 'msl', 'sp', 'wtmp'
            ②多层要素：'u1000', 'v850', 'w500', 'gh500', 'q925', 't1000'等
            输入的parameter+level字符串会被解码处parameter和level信息，解码方式参照Param.separate_FactorLevel
    """

    def __init__(self, data_center: Param.data_center, data_type: Param.data_type):
        self.data_type = data_type
        self.data_center = data_center

    def init_date_range(self, *parameter_levels) -> List[str]:
        pass

    def load(self, parameter_level: str, init_date: str) -> xr.DataArray:
        pass


if __name__ == "__main__":
    pass
