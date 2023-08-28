import os

# Класс обработчик событий (переход в папку)
class GotoInside:
    # Конструктор   
    def __init__(self, app, web):
        app.add_routes([web.get('/gotoinside', self.gotoinside)])       # Добавление маршрута

    # Обработчик перехода во внутрь папки
    async def gotoinside(self, request):
        params = request.rel_url.query
        fullpath = self.get_fullpath(params['path'], request.remote)    # Полный путь к выделенной папке
        selfolder = params['selfolder']
        viewpath = params['viewpath']
        
        if not os.path.exists(fullpath):                                # Нет выделенной в дереве папки
            return self.web.json_response('notfound')
        if not os.path.exists(fullpath + '/' + selfolder):              # Нет выделенной во вкладке папки
            return self.web.json_response('notexists')
        
        path = fullpath + '/' + selfolder + '/' + viewpath
    
        if not os.path.exists(path):                                    # Нет выделенной папки
            return self.web.json_response('notexists_')

        return self.web.json_response(os.listdir(path))
