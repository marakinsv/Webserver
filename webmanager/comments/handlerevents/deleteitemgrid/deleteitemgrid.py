import aiopg
import json

# Класс обработчик события (удаление элемента из grid)
class DeleteItemGrid:
    # Конструктор   
    def __init__(self, app, web):       
        app.add_routes([web.get('/deleteitemgrid', self.deleteitemgrid)])  # Добавление маршрута

    # Обработчик удаления данных из grid
    async def deleteitemgrid(self, request):
        params = request.rel_url.query
        dataItem = json.loads(params['dataitem'])

        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('UPDATE public."NOTICE" SET "ISDELETED" = True \
                                         WHERE "MANAGOBJ" = '"'{}'"' AND "OBJECT" = '"'{}'"' AND "SYSTEM" = '"'{}'"' AND "NUM" = {}'.format(
                                                                dataItem['MANAGOBJ'], dataItem['OBJECT'], dataItem['SYSTEM'], dataItem['NUM']))
        return self.web.json_response([1])
