import os
import urllib

# Класс обработчик событий (создание узла)
class CreateNode:
    # Конструктор   
    def __init__(self, app, web):
        app.add_routes([web.get('/createnode', self.createnode)])        # Добавление маршрута
    
    async def createnode(self, request):
        params = request.rel_url.query
        fullpath = self.get_fullpath(params['path'], request.remote)     # Полный путь к выделенной папке
        if not os.path.exists(fullpath):                                 # Нет выделенной папки
            return self.web.json_response('notfound')

        dir_ = fullpath + '/' + urllib.parse.unquote(params['foldername'])
        if os.path.exists(dir_):                                         # Папка с таким именем уже существует
            return self.web.json_response('exists') 
        os.mkdir(dir_)
        if not os.path.exists(dir_):                                     # Не удалось создать папку
            return self.web.json_response('notcreated')
        
        return self.web.json_response('success')                         # Сообщаем, что все ОК
