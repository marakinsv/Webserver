import aiopg
import json

# Класс обработчик события (событие до вставки элемента в grid)
class BefInsertItemGrid:
    # Конструктор   
    def __init__(self, app, web):       
        app.add_routes([web.get('/befinsertitemgrid', self.befinsertitemgrid)])  # Добавление маршрута

    # Обработчик вставки элемента в grid
    async def befinsertitemgrid(self, request):
        params = request.rel_url.query
        dataItem = json.loads(params['dataitem'])

        msg = 'OK'
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('SELECT "NUM" FROM public."NOTICE" \
                                         WHERE "MANAGOBJ" = '"'{}'"' AND "OBJECT" = '"'{}'"' AND "NUM" = {}'.format(
                                            dataItem['MANAGOBJ'], dataItem['OBJECT'], dataItem['NUM']))
                    async for row in cur:
                        msg = 'Номер замечания уже есть в списке!'

        #print(msg)
        return self.web.json_response({'msg': msg})
        
        

