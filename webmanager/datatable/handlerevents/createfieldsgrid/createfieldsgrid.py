import aiopg
import json
from ..constants import c_name_cols_mpsa, c_name_cols_ltm

# Класс обработчик события (создание полей grid)
class CreateFieldsGrid_:
    # Конструктор   
    def __init__(self, app, web):       
        app.add_routes([web.get('/createfieldsgrid_', self.createfieldsgrid_)])  # Добавление маршрута

    # Обработчик создания полей grid
    async def createfieldsgrid_(self, request):
        global c_name_cols_mpsa, c_name_cols_ltm

        managObjs = []; objs = []; systems = []
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('SELECT * FROM public."SETTINGS"')
                    async for row in cur:
                        managObjs = row[0]
                        data = row[1][['mpsa', 'ltm'][self.sysId]]
                        objs = [val for ls in list(data.values()) for val in ls]
                        systems = row[2]                                      
                            
        #params = request.rel_url.query
        params = []
        titles = [{'MANAGOBJ': 'РНУ', 'OBJECT': 'НПС', 'SYSTEM': 'Система'},                # МПСА
                  {'MANAGOBJ': 'РНУ', 'OBJECT': 'МН', 'DISTANCE': 'км', 'NUMCP': '№ КП'}]   # ЛТМ 
        for colname in [list(c_name_cols_mpsa.keys()), list(c_name_cols_ltm.keys())][self.sysId]:
            if colname == 'PARAM1': break
            param = {}
            param['name'] = colname
            param['pid'] = -1
            param['filtered'] = True
            param['edited'] = False
            if colname == 'NUMCP': param['edited'] = True
            #if colname in ['SYSTEM', 'DISTANCE', 'NUMCP']: param['filtered'] = True
            # Выбор значений из выпадающего списка
            param['choice'] = []
            if colname == 'MANAGOBJ': param['choice'] = managObjs
            if colname == 'OBJECT': param['choice'] = objs
            if colname == 'SYSTEM': param['choice'] = systems
            # ------------------------------------------
            param['title'] = titles[self.sysId][colname]
            # Тип параметра
            param['type'] = 'text'
            if colname in ['MANAGOBJ', 'OBJECT', 'SYSTEM']: param['type'] = 'select'
            # ------------------------------------------
            param['width'] = 30
            param['font-color'] = 'white'
            param['back-color'] = 'black'
            param['blink-font-color'] = 'white'
            param['blink-back-color'] = 'black'
            param['blink'] = False
            params.append(param)
        # Загружаем названия динамических параметров
        idx = [3, 4][self.sysId]           # Индекс столбца для первого динамического параметра
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('SELECT * FROM public."{}"'.format(['HEAD_PARAMS_MPSA', 'HEAD_PARAMS_LTM'][self.sysId]))
                    async for row in cur:
                        for param in row[0]:
                            if not param['visibled']: continue  # Невидимый столбец
                            param['name'] = [list(c_name_cols_mpsa.keys()), list(c_name_cols_ltm.keys())][self.sysId][idx]
                            param['choice'] = []
                            params.append(param)
                            idx += 1
                    # Значения для фильтров столбцов
                    await cur.execute('SELECT * FROM public."{}"'.format(['VALUES_PARAMS_MPSA', 'VALUES_PARAMS_LTM'][self.sysId]))
                    async for row in cur:
                        for data in row[0]:
                            for param in params:
                                if param['pid'] == data['pid']:     # Нашли нужный параметр
                                    param['parentid'] = data['parentid']
                                    param['childid'] = data['childid']  
                                    if data['parentid'] > 0:        # Значения столбца зависят от другого столбца, например, версия драйвера
                                        #param['choice'] = list(data['values'][0].values())[0]
                                        param['choice'] = []
                                        for item in data['values']:
                                            param['choice'] += list(item.values())[0]                                        
                                    else:
                                        if type(data['values'][0]) is dict:
                                            for item in data['values']:
                                                param['choice'].append(list(item.keys())[0])
                                        else: param['choice'] = data['values']
                                    break
        return self.web.json_response(params)
