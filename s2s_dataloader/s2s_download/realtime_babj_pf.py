from ecmwfapi import ECMWFDataServer
from .main import RealTimeGribDownload


server = ECMWFDataServer()


class Download_BABJ_PF_Realtime(RealTimeGribDownload):
    """
    下载babj的近实时预报数据，扰动模式
    """

    parameter_num = {'mn2t6': 122,
                     'mx2t6': 121,
                     '2t': 167,
                     'tp': 228228,
                     '10u': 165,
                     '10v': 166,
                     'msl': 151,
                     'sp': 134,
                     'wtmp': 34,
                     'u': 131,
                     'v': 132,
                     'q': 133,
                     'gh': 156,
                     't': 130,
                     'w': 135}

    pressure_level = {'u': (1000, 925, 850, 700, 500, 300, 200, 100, 50, 10),
                      'v': (1000, 925, 850, 700, 500, 300, 200, 100, 50, 10),
                      'w': (1000, 925, 850, 700, 500, 300, 200, 100, 50, 10),
                      't': (1000, 925, 850, 700, 500, 300, 200, 100, 50, 10),
                      'gh': (1000, 925, 850, 700, 500, 300, 200, 100, 50, 10),
                      'q': (1000, 925, 850, 700, 500, 300, 200)}

    def __init__(self, number):
        RealTimeGribDownload.__init__(self, number=number, data_center='babj')

    def retrieve_2t_wtmp(self, parameter, init_date: str, save_path: str):
        assert parameter in ['2t', 'wtmp']
        server.retrieve({
            "number": str(self.number),
            "class": "s2",
            "dataset": "s2s",
            "date": init_date,
            "expver": "prod",
            "levtype": "sfc",
            "model": "glob",
            "origin": self.data_center,
            "param": self.parameter_num[parameter],
            "step": "0-24/24-48/48-72/72-96/96-120/120-144/144-168/168-192/192-216/216-240/240-264/264-288/288-312"
                    "/312-336/336-360/360-384/384-408/408-432/432-456/456-480/480-504/504-528/528-552/552-576/576-600"
                    "/600-624/624-648/648-672/672-696/696-720/720-744/744-768/768-792/792-816/816-840/840-864/864-888"
                    "/888-912/912-936/936-960/960-984/984-1008/1008-1032/1032-1056/1056-1080/1080-1104/1104-1128/1128"
                    "-1152/1152-1176/1176-1200/1200-1224/1224-1248/1248-1272/1272-1296/1296-1320/1320-1344/1344-1368"
                    "/1368-1392/1392-1416/1416-1440",
            "stream": "enfo",
            "time": "00:00:00",
            "type": self.data_type,
            "target": save_path,
        })

    def retrieve_10u10v(self, parameter: str, init_date: str, save_path: str):
        assert parameter in ['10u', '10v']
        server.retrieve({
            "number": str(self.number),
            "class": "s2",
            "dataset": "s2s",
            "date": init_date,
            "expver": "prod",
            "levtype": "sfc",
            "model": "glob",
            "origin": self.data_center,
            "param": self.parameter_num[parameter],
            "step": "0/24/48/72/96/120/144/168/192/216/240/264/288/312/336/360/384/408/432/456/480/504/528/552/576"
                    "/600/624/648/672/696/720/744/768/792/816/840/864/888/912/936/960/984/1008/1032/1056/1080/1104"
                    "/1128/1152/1176/1200/1224/1248/1272/1296/1320/1344/1368/1392/1416/1440",
            "stream": "enfo",
            "time": "00:00:00",
            "type": self.data_type,
            "target": save_path,
        })

    def retrieve_mx2t6_mn2t6_tp(self, parameter: str, init_date: str, save_path: str):
        assert parameter in ['mn2t6', 'mx2t6', "tp"]
        server.retrieve({
            "number": str(self.number),
            "class": "s2",
            "dataset": "s2s",
            "date": init_date,
            "expver": "prod",
            "levtype": "sfc",
            "model": "glob",
            "origin": self.data_center,
            "param": self.parameter_num[parameter],
            "step": "6/12/18/24/30/36/42/48/54/60/66/72/78/84/90/96/102/108/114/120/126/132/138/144/150/156/162/168"
                    "/174/180/186/192/198/204/210/216/222/228/234/240/246/252/258/264/270/276/282/288/294/300/306/312"
                    "/318/324/330/336/342/348/354/360/366/372/378/384/390/396/402/408/414/420/426/432/438/444/450/456"
                    "/462/468/474/480/486/492/498/504/510/516/522/528/534/540/546/552/558/564/570/576/582/588/594/600"
                    "/606/612/618/624/630/636/642/648/654/660/666/672/678/684/690/696/702/708/714/720/726/732/738/744"
                    "/750/756/762/768/774/780/786/792/798/804/810/816/822/828/834/840/846/852/858/864/870/876/882/888"
                    "/894/900/906/912/918/924/930/936/942/948/954/960/966/972/978/984/990/996/1002/1008/1014/1020"
                    "/1026/1032/1038/1044/1050/1056/1062/1068/1074/1080/1086/1092/1098/1104/1110/1116/1122/1128/1134"
                    "/1140/1146/1152/1158/1164/1170/1176/1182/1188/1194/1200/1206/1212/1218/1224/1230/1236/1242/1248"
                    "/1254/1260/1266/1272/1278/1284/1290/1296/1302/1308/1314/1320/1326/1332/1338/1344/1350/1356/1362"
                    "/1368/1374/1380/1386/1392/1398/1404/1410/1416/1422/1428/1434/1440",
            "stream": "enfo",
            "time": "00:00:00",
            "type": self.data_type,
            "target": save_path,
        })

    def retrieve_sp_msl(self, parameter: str, init_date: str, save_path: str):
        assert parameter in ['sp', 'msl']
        server.retrieve({
            "number": str(self.number),
            "class": "s2",
            "dataset": "s2s",
            "date": init_date,
            "expver": "prod",
            "levtype": "sfc",
            "model": "glob",
            "origin": self.data_center,
            "param": self.parameter_num[parameter],
            "step": "0/24/48/72/96/120/144/168/192/216/240/264/288/312/336/360/384/408/432/456/480/504/528/552/576"
                    "/600/624/648/672/696/720/744/768/792/816/840/864/888/912/936/960/984/1008/1032/1056/1080/1104"
                    "/1128/1152/1176/1200/1224/1248/1272/1296/1320/1344/1368/1392/1416/1440",
            "stream": "enfo",
            "time": "00:00:00",
            "type": self.data_type,
            "target": save_path,
        })

    def retrieve_pressure_level(self, parameter: str, level: int, init_date: str, save_path: str) -> bool:
        assert parameter in self.pressure_level
        assert level in self.pressure_level[parameter]

        server.retrieve({
            "number": str(self.number),
            "class": "s2",
            "dataset": "s2s",
            "date": init_date,
            "expver": "prod",
            "levelist": str(level),
            "levtype": "pl",
            "model": "glob",
            "origin": self.data_center,
            "param": self.parameter_num[parameter],
            "step": "0/24/48/72/96/120/144/168/192/216/240/264/288/312/336/360/384/408/432/456/480/504/528/552/576"
                    "/600/624/648/672/696/720/744/768/792/816/840/864/888/912/936/960/984/1008/1032/1056/1080/1104"
                    "/1128/1152/1176/1200/1224/1248/1272/1296/1320/1344/1368/1392/1416/1440",
            "stream": "enfo",
            "time": "00:00:00",
            "type": self.data_type,
            "target": save_path,
        })
        return True

    def retrieve_single_level(self, parameter: str, init_date: str, save_path: str):
        kwarg = {'parameter': parameter, 'init_date': init_date, 'save_path': save_path}

        if parameter in ('2t', 'wtmp'):
            self.retrieve_2t_wtmp(**kwarg)
        elif parameter in ('10u', '10v'):
            self.retrieve_10u10v(**kwarg)
        elif parameter in ('mx2t6', 'mn2t6', 'tp'):
            self.retrieve_mx2t6_mn2t6_tp(**kwarg)
        elif parameter in ('sp', 'msl'):
            self.retrieve_sp_msl(**kwarg)
        return True


class _Test:
    def test1(self):
        obj = Download_BABJ_PF_Realtime(number=1)
        obj.retrieve_2t_wtmp('2t', '2021-07-01', '2t.grib')
        obj.retrieve_2t_wtmp('wtmp', '2021-07-01', 'wtmp.grib')
        obj.retrieve_10u10v('10u', '2021-07-01', '10u.grib')
        obj.retrieve_10u10v('10v', '2021-07-01', '10v.grib')
        obj.retrieve_mx2t6_mn2t6_tp('tp', '2021-07-01', 'tp.grib')
        obj.retrieve_mx2t6_mn2t6_tp('mx2t6', '2021-07-01', 'mx2t6.grib')
        obj.retrieve_mx2t6_mn2t6_tp('mn2t6', '2021-07-01', 'mn2t6.grib')
        obj.retrieve_sp_msl('sp', '2021-07-01', 'sp.grib')
        obj.retrieve_sp_msl('msl', '2021-07-01', 'msl.grib')
        for p in obj.pressure_level.keys():
            obj.retrieve_pressure_level(p, 850, '2021-07-01', f'{p}850.grib')

        # 检查要素是否一致
        import os
        import xarray as xr
        dir = os.path.dirname(__file__)
        for f in [f for f in os.listdir(dir) if f.endswith('grib')]:
            data = xr.open_dataarray(os.path.join(dir, f), engine='cfgrib')
            print(f.split('.')[0], data.name, data.shape, data['number'].__data__)


if __name__ == "__main__":
    _Test().test1()

