import os
import urllib

# Класс обработчик событий (переименование узла)
class RenameNode:
    # Конструктор   
    def __init__(self, app, web):
        app.add_routes([web.get('/renamenode', self.renamenode)])     # Добавление маршрута

    # Обработчик переименования узла дерева
    async def renamenode(self, request):
        params = request.rel_url.query     
        fullpath = self.get_fullpath(params['path'], request.remote)   # Полный путь к выделенной папке

        if not os.path.exists(fullpath):                               # Нет выделенной папки
            return self.web.json_response('notexists')

        newpath = '/'.join(fullpath.split('/')[:-1]) + '/' + urllib.parse.unquote(params['newname'])
        if os.path.exists(newpath):                                    # Папка с таким именем уже существует
            return self.web.json_response('exists')
  
        os.rename(fullpath, newpath)
        if not os.path.exists(newpath):
            return self.web.json_response('notrenamed')                # Не удалось переименовать директорию
        
        return self.web.json_response('success')                       # Сообщаем, что все ОК
