from .template import S2SRealtimeBase
import xarray as xr
import pandas as pd


class ECMF_Realtime(S2SRealtimeBase):

    def __init__(self):
        S2SRealtimeBase.__init__(self, data_center='ecmf')

    def post_process(self, dataarray: xr.DataArray, parameter: str):
        """
        返回数据的是时间主轴是step，并保留轴valid_time，即和输入的dataarray保持一致
        """
        if parameter in ('mx2t6', 'mn2t6'):
            dataarray['step'] = (pd.to_datetime(dataarray['valid_time'].data)
                                 - pd.to_timedelta(6, unit='h')).strftime("%Y-%m-%d")
            if parameter == 'mx2t6':
                dataarray = dataarray.groupby('step').max()
            elif parameter == 'mn2t6':
                dataarray = dataarray.groupby('step').min()
            # 还原时间轴
            dataarray['valid_time'] = ('step', pd.to_datetime(dataarray['step'].data))
            dataarray['step'] = dataarray['valid_time'] - dataarray['time']

        elif parameter == 'tp':
            dataarray = dataarray[::4, :, :].diff(dim='step')
            dataarray['step'] = pd.to_timedelta(dataarray['step'].data) - pd.to_timedelta(1, unit='d')
            dataarray['valid_time'] = dataarray['time'] + dataarray['step']
            dataarray = dataarray.where(dataarray > 0, 0)

        return dataarray


if __name__ == "__main__":
    obj = ECMF_Realtime()
    print(obj.init_date_range('2t', 'tp', 't500'))
    for param_ll in ('mn2t6', 'mx2t6', '2t', 'tp', '10u', '10v', 'msl', 'sp', 'wtmp',
                     'u500', 'v500', 'w500', 'gh500', 'q500', 't500'):
        print(param_ll, obj.load(parameter_level=param_ll, init_date='20210104').shape)
    data = obj.load(parameter_level='10v', init_date='20210104')
    obj.post_process(data, parameter='10v')
