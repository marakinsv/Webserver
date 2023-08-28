import os

# Класс обработчик событий (удаление узла)
class DeleteNode:
    # Конструктор   
    def __init__(self, app, web):
        app.add_routes([web.get('/deletenode', self.deletenode)])     # Добавление маршрута

    # Обработчик удаления узла дерева
    async def deletenode(self, request):
        params = request.rel_url.query
        fullpath = self.get_fullpath(params['path'], request.remote)  # Полный путь к выделенной папке
        
        if not os.path.exists(fullpath):                                    
            return self.web.json_response('notexists')                # Удаляемая папка не существует
        
        folders = os.listdir(fullpath)
        if len(folders) != 0:                                         # Папка не пустая
            if not self.is_empty_struct(fullpath, folders):           # Какая либо папка структуры содержит файлы или папки
                return self.web.json_response('notempty')
        # Удаляем папку
        if len(folders) == 0:                                         # Папка пустая
            os.rmdir(fullpath)
        else:
            for folder in folders:
                os.rmdir(fullpath + '/' + folder)
            os.rmdir(fullpath)
        # Проверяем, что папка удалена    
        if os.path.exists(fullpath):                                  # Не удалось удалить директорию
            return self.web.json_response('notdeleted')
        
        self.paths[self.sysId][request.remote] = '/'.join(fullpath.split('/')[:-1]) # Сохраняем путь до родителя
        
        return self.web.json_response('success')                      # Сообщаем, что все ОК

# Дополнительные методы ==========================================
    # Проверка что структура пустая
    def is_empty_struct(self, path, folders):
        for folder in folders:
            #if self.isfile(folder): return False                      # Это файл
            if len(os.listdir(path + '/' + folder)) != 0:  # Папка содержит файлы или папки
                return False
        return True
