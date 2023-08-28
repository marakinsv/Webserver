# Класс обработчик события (до изменения элемента в grid)
class BefUpdateItemGrid:
    # Конструктор   
    def __init__(self, app, web):       
        app.add_routes([web.get('/befupdateitemgrid', self.befupdateitemgrid)])  # Добавление маршрута

    # Обработчик события до изменения элемента в grid
    async def befupdateitemgrid(self, request):
        params = request.rel_url.query
        dataItem = json.loads(params['dataitem'])
        return await self.befinsertitemgrid(request)  # Перенаправляем на обработчик до вставки
