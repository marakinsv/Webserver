import os

# Класс обработчик событий (выбор узла)
class SelectNode:
    # Конструктор   
    def __init__(self, app, web):
        app.add_routes([web.get('/selectnode', self.selectnode)])     # Добавление маршрута

    # Обработчик выделения узла дерева
    async def selectnode(self, request):
        params = request.rel_url.query
        if params['path'] == '': return self.web.json_response('')
        fullpath = self.get_fullpath(params['path'], request.remote)  # Полный путь к выделенной папке
        self.paths[self.sysId][request.remote] = fullpath             # Сохраняем путь
        if not os.path.exists(fullpath):                              # Нет выделенной папки
            return self.web.json_response('notfound')
        folders = os.listdir(fullpath)                                # Получаем список всех папок в указанной директории
        if self.is_struct_folder(folders):                            # Папка принадлежит структуре данных
            listFolders = self.get_struct_folders(fullpath, folders)
            return self.web.json_response(listFolders)
        return self.web.json_response('unknown')

# Дополнительные методы ==========================================    
    # Возвращает папки структуры данных с идентификатором заполненности
    def get_struct_folders(self, path, folders):
        dataList = []
        num = 1
        for folder in folders:
            if self.sysId == 0:                             # 0 - МПСА, 1 - ЛТМ
                if '.' in folder:
                    if folder.index('.') != 2: continue     # Пропускаем файлы
                sNum = folder[:2]
                if not sNum.isdigit(): continue             # Папка не принадлежит структуре данных
                num = int(sNum)            
            else:
                if self.isfile(folder): continue            # Пропускаем файлы
                num += 1
            status = False
            if len(os.listdir(path + '/' + folder)) != 0: status = True  # Папка содержит файлы или папки
            dataList.append((num, folder, status))
        dataList.sort()
        return [[folder, status] for num, folder, status in dataList]
