import aiopg
import json
from ..general import getSql

# Класс обработчик события (вставка элемента в grid)
class InsertItemGrid:
    # Конструктор   
    def __init__(self, app, web):       
        app.add_routes([web.get('/insertitemgrid', self.insertitemgrid)])  # Добавление маршрута

    # Обработчик вставки элемента в grid
    async def insertitemgrid(self, request):
        global getSql
        params = request.rel_url.query
        dataItem = json.loads(params['dataitem'])
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(getSql(dataItem, False))  # Вставляем значение в таблицу свойств
                                    
        return self.web.json_response([1])
        
        

