import aiopg

# Имена столбцов таблицы "CHOSE" в БД
c_name_cols = ('MANAGOBJS', 'OBJECTS', 'SYSTEMS', 'STEPS', 'LEVELS', 'LISTPERSON', 'LISTSTATUS', 'CURMANAGOBJ')

# Класс обработчик события (создание полей grid)
class CreateFieldsGrid:
    # Конструктор   
    def __init__(self, app, web):       
        app.add_routes([web.get('/createfieldsgrid', self.createfieldsgrid)])  # Добавление маршрута

    # Обработчик создания полей grid
    async def createfieldsgrid(self, request):
        params = request.rel_url.query
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('SELECT * FROM public."CHOSE"')
                    async for row in cur:
                        data = dict(zip(c_name_cols, row))
                        data['objs'] = []
                        '''if params['managobj'] == '':   # В строке запроса РНУ не указано
                            for managobj in list(data['OBJECTS'].keys()):
                                data['objs'] = data['objs'] + data['OBJECTS'][managobj]
                        else: data['objs'] = data['OBJECTS'][params['managobj']]'''
                        for managobj in list(data['OBJECTS'].keys()):
                            data['objs'] = data['objs'] + data['OBJECTS'][managobj]
                        del data['OBJECTS']
                        return self.web.json_response(data)
        return self.web.json_response({})
