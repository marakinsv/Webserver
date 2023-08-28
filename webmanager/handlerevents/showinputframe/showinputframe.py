import aiopg
import os

# Класс обработчик событий (показать форму ввода данных о загружаемом файле)
class ShowInputFrame:
    # Конструктор   
    def __init__(self, app, web):
        app.add_routes([web.get('/getdatainputframe', self.getdatainputframe)])  # Добавление маршрута

    # Обработчик запроса данных для формы ввода
    async def getdatainputframe(self, request):
        params = request.rel_url.query

        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('SELECT "USERS", "REASONS" FROM public."SETTINGS"')
                    async for row in cur:
                        users = row[0]                  # Список пользователей, работающих с данными
                        reasons = row[1]                # Возможные причины добавления данных
        if reasons == None: reasons = []
        return self.web.json_response({'users': users, 'reasons': reasons})
