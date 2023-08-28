import os

# Класс обработчик событий (переход на другую вкладку)
class ChangeTab:
    # Конструктор   
    def __init__(self, app, web):
        app.add_routes([web.get('/getfiles', self.getfiles)])     # Добавление маршрута

    # Обработчик чтения файлов выделенного узла
    async def getfiles(self, request):
        params = request.rel_url.query
        path = params['path'] 
        selfolder = params['selfolder']
        fullpath = self.get_fullpath(path, request.remote)        # Полный путь к выделенной папке

        if not os.path.exists(fullpath):                          # Нет выделенной папки
            return self.web.json_response('notfound')
        if not os.path.exists(fullpath + '/' + selfolder):        # Нет папки, соответствующей вкладке
            return self.web.json_response('notexists')
        
        listfiles = os.listdir(fullpath + '/' + selfolder)        # Список файлов и папок в папке, соответствующей вкладке
        flist = []
        for filename in listfiles:
            if not self.istempfile(filename): flist.append(filename)
            
        self.deleteTempFiles(fullpath + '/' + selfolder, listfiles) # Удаляем временные файлы в выделенной папке, если они есть
        
        return self.web.json_response(flist)
