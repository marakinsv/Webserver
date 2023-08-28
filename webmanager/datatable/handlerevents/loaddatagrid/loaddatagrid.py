import aiopg
import datetime
import json
import urllib
from ..constants import c_name_cols_mpsa, c_name_cols_ltm

c_any_txt = '<НЕ ЗАДАН>'

# Класс обработчик события (загрузка данных в grid)
class LoadDataGrid_:
    # Конструктор   
    def __init__(self, app, web):       
        app.add_routes([web.get('/loaddatagrid_', self.loaddatagrid_)])  # Добавление маршрута

    # Обработчик загрузки данных в grid
    async def loaddatagrid_(self, request):
        global c_name_cols_mpsa, c_name_cols_ltm
        params = request.rel_url.query
        #print(params['filter'])

        dataFilter = json.loads(params['filter'])                        # Параметры фильтра grid
        # Раскодируем названия фильтров
        for key in dataFilter.keys():
            dataFilter[key] = urllib.parse.unquote(dataFilter[key])
        #print(dataFilter)
        sql = ''

        if dataFilter.get('MANAGOBJ', c_any_txt) != c_any_txt:
            sql = ' WHERE "MANAGOBJ" = '"'{}'"''.format(dataFilter['MANAGOBJ'])
            if dataFilter.get('OBJECT', c_any_txt) != c_any_txt:
                sql = sql + ' AND'
            else:
                if self.sysId == 0:   # МПСА
                    if dataFilter.get('SYSTEM', c_any_txt) != c_any_txt: sql = sql + ' AND'
                if self.sysId == 1:   # ЛТМ
                    if dataFilter.get('DISTANCE', '') != '': sql = sql + ' AND'
                    
        if dataFilter.get('OBJECT', c_any_txt) != c_any_txt:
            sql = sql + ' "OBJECT" = '"'{}'"''.format(dataFilter['OBJECT'])
            if self.sysId == 0:   # МПСА
                if dataFilter.get('SYSTEM', c_any_txt) != c_any_txt: sql = sql + ' AND'
            if self.sysId == 1:   # ЛТМ
                if dataFilter.get('DISTANCE', '') != '': sql = sql + ' AND'
        if self.sysId == 0:   # МПСА
            if dataFilter.get('SYSTEM', c_any_txt) != c_any_txt:
                sql = sql + ' "SYSTEM" = '"'{}'"''.format(dataFilter['SYSTEM'])
        if self.sysId == 1:   # ЛТМ
            if dataFilter.get('DISTANCE', '') != '':
                sql = sql + ' "DISTANCE" = {}'.format(dataFilter['DISTANCE'])
        if sql != '' and not ('WHERE' in sql): sql = ' WHERE' + sql
        
        ret = []
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    if self.sysId == 0:             # 0 - МПСА, 1 - ЛТМ
                        await cur.execute('SELECT * FROM public."PARAMS_MPSA"{} ORDER BY "MANAGOBJ", "OBJECT"'.format(sql))
                    else:
                        await cur.execute('SELECT * FROM public."PARAMS_LTM"\
                                             {} ORDER BY "MANAGOBJ", "OBJECT", "DISTANCE", "NUMCP"'.format(sql))
                    async for row in cur:
                        data = dict(zip([list(c_name_cols_mpsa.keys()), list(c_name_cols_ltm.keys())][self.sysId], row))
                        mismatch = False
                        for colname in list(data.keys()):
                            fval = dataFilter.get(colname, '')  # Значение фильтра для указанного столбца
                            if fval == '' or fval == c_any_txt: continue
                            if type(data[colname]) is int: fval = int(fval)
                            if type(data[colname]) is float: fval = float(fval)
                            if data[colname] != fval:
                                mismatch = True
                                break
                        if mismatch: continue

                        ret.append(data)
                        
        return self.web.json_response(ret)
