import xarray as xr
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from typing import Tuple
import gc

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签 'DengXian'
plt.rcParams['axes.unicode_minus'] = False


def map_contourf(dataarray: xr.DataArray,
                 save_path,
                 *,
                 title='',
                 figsize: Tuple[int, int] = None,
                 cmap='Oranges',
                 dpi=400,
                 title_fontsize=7,
                 xticks_fontsize=7,
                 yticks_fontsize=7,
                 xticks_rotation=0,
                 dx=10,
                 dy=10,
                 **kwargs):
    """
    根据输入二维矩阵数据画图，底图是大陆海洋信息
    通过封装Xarray.DataArray.plot.contourf实现功能

    Parameters
    ----------
    dataarray :
        二维矩阵数据xr.DataArray，包含轴longitude和latitude
        dataarray的经度范围是0~360（东->西），纬度范围-90~90（南->北）
    save_path :
        图片保存的路径，要注意路径所在的目录必须是存在的
    dpi :
        dpi 确定了图形每英寸包含的像素数，图形尺寸相同的情况下， dpi 越高，则图像的清晰度越高
    figsize :
        图片的大小尺寸（a,b），单位为英寸.则此时图形的像素为：px=a*dpi, py=b*dpi。
        a表示水平方向宽度
        b表示竖直方向高度
    title :
        图片名称
    cmap :
        颜色映射的方式，参考：
        https://matplotlib.org/stable/tutorials/colors/colormaps.html
    title_fontsize :
        图片标题的字体大小
    yticks_fontsize :
        Y轴刻度字体的大小
    xticks_fontsize :
        X轴刻度字体的大小
    xticks_rotation :
        X轴的坐标旋转角度，对于坐标轴刻度比较稠密且相互覆盖时需要设置，取值0~360
    dx :
        X轴经度的刻度步长。图片显示的经度步长是：dx * dataarray的经度分辨率
    dy :
        Y轴纬度的刻度步长。图片显示的纬度步长是：dy * dataarray的维度分辨率
    kwargs :
        参考xarray.plot.contourf的其他参数，要自定义colorbar可以参考，请参考以下官方文档：
        http://xarray.pydata.org/en/stable/generated/xarray.plot.contourf.html?highlight=contourf
    Returns
    -------
    None

    Examples
    -------
    from share.ERA5 import Reanalysis
    path = '/S2SGribDataMount/DataDisk_4/ecmwf_cf_reforecast/source_data/2t/s2s_ecmf_20181231_2t.grib'
    data = xr.open_dataarray(path, engine='cfgrib')
    data = data[0][0] - 273.15
    data = Reanalysis.select_lon_lat(data, lon_range=(100, 140), lat_range=(-10, 60))
    mn, mx = int(data.min().data), int(data.max().data)
    level = np.linspace(mn, mx, (mx - mn) // 5 + 1)
    map_contourf(data, 'test.png', figsize=(10, 4), title='气温', title_fontsize=10,
                 dx=10,
                 dy=20,
                 xticks_rotation=300,
                 # 以下是Xarray.DataArray.plot.contourf的参数：
                 vmin=mn, vmax=mx, center=0,
                 cmap='Reds',
                 levels=level,
                 cbar_kwargs={'ticks': level,
                              'format': '%.0f'}
                 )

    """
    assert 'longitude' in dataarray.coords.keys()
    assert 'latitude' in dataarray.coords.keys()
    assert len(dataarray.dims) == 2

    data = dataarray.copy()  # 画图过程中会修改经度，即使还原也不是线程和进程安全的
    # 修改经度
    data['longitude'] = data['longitude'] - 180
    plt.figure(figsize=figsize, dpi=dpi)

    # 设置投影，绘制海陆信息的底图
    proj = ccrs.PlateCarree(central_longitude=180)
    ax = plt.axes(projection=proj)
    ax.xaxis.set_major_formatter(LongitudeFormatter(zero_direction_label=True))
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.coastlines()

    # 画出填充的等值线
    data.plot.contourf(ax=ax, transform=proj, cmap=cmap, add_labels=False, **kwargs)

    # 设置刻度
    xticks, yticks = list(data['longitude'].data), list(data['latitude'].data)
    xticks, yticks = xticks[::dx] + [xticks[-1], ], yticks[::dy] + [yticks[-1], ]  # 防止丢失边界刻度

    # 添加网格
    gl = ax.gridlines(crs=proj, draw_labels=False, linewidth=0.8, linestyle=':', color='k', alpha=0.8)
    gl.xlocator = mticker.FixedLocator(xticks)
    gl.ylocator = mticker.FixedLocator(yticks)

    # 添加坐标轴刻度
    ax.set_xticks(xticks, crs=proj)
    ax.set_yticks(yticks, crs=proj)

    # 调节字体大小
    plt.xticks(fontsize=xticks_fontsize, rotation=xticks_rotation)
    plt.yticks(fontsize=yticks_fontsize)
    plt.title(title, fontdict={'fontsize': title_fontsize})

    # 保存图片
    plt.savefig(save_path, bbox_inches='tight')

    # 手动回收内存
    del data
    gc.collect()

    plt.close()


if __name__ == "__main__":
    pass
