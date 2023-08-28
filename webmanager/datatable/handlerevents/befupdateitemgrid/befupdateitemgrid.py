import json
import urllib

# Класс обработчик события (до изменения элемента в grid)
class BefUpdateItemGrid_:
    # Конструктор   
    def __init__(self, app, web):       
        app.add_routes([web.get('/befupdateitemgrid_', self.befupdateitemgrid_)])  # Добавление маршрута

    # Обработчик события до изменения элемента в grid
    async def befupdateitemgrid_(self, request):
        params = request.rel_url.query
        self.previousItem = json.loads(params['previousitem'])  # Сохраняем значения элементов до обновления
        # Раскодируем название
        for key in self.previousItem.keys():
            self.previousItem[key] = urllib.parse.unquote(self.previousItem[key])
        
        return self.web.json_response({'msg': 'OK'})
