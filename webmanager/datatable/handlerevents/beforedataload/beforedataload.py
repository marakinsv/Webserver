import aiopg

# Класс обработчик события (перед загрузкой данных в grid)
class BeforeDataLoad_:
    # Конструктор   
    def __init__(self, app, web):       
        app.add_routes([web.get('/beforedataload_', self.beforedataload_)])  # Добавление маршрута

    # Обработчик перед загрузкой данных в grid
    async def beforedataload_(self, request):
        params = request.rel_url.query
        flt = params['filter']; refid = int(params['refid'])
        # Значения для фильтров столбцов
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('SELECT * FROM public."{}"'.format(['VALUES_PARAMS_MPSA', 'VALUES_PARAMS_LTM'][self.sysId]))
                    async for row in cur:
                        for data in row[0]:
                            if data['parentid'] == refid:     # Нашли нужный параметр
                                for choice in data['values']:
                                    if list(choice.keys())[0] == flt:
                                        #print(choice[flt])
                                        return self.web.json_response(choice[flt])
        return self.web.json_response([])
