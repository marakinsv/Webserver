import aiopg
import json
from ..general import getSql
from ..constants import c_name_cols

# Класс обработчик события (обновление элемента grid)
class UpdateItemGrid:
    # Конструктор   
    def __init__(self, app, web):       
        app.add_routes([web.get('/updateitemgrid', self.updateitemgrid)])  # Добавление маршрута

    # Обработчик обновления элемента grid
    async def updateitemgrid(self, request):
        global getSql, c_name_cols
        params = request.rel_url.query
        dataItem = json.loads(params['dataitem'])

        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(getSql(c_name_cols, dataItem, True))
                    
        return self.web.json_response([1])
