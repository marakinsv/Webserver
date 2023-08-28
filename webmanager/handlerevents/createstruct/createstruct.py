import aiopg
import json
import os
import urllib
from datatable.handlerevents.general import getSql
from datatable.handlerevents.constants import c_name_cols_mpsa, c_name_cols_ltm

# Класс обработчик событий (создание набора папок)
class CreateStruct:
    # Конструктор   
    def __init__(self, app, web):
        app.add_routes([web.get('/createstruct', self.createstruct)])     # Добавление маршрута

    # Обработчик создание набора папок
    async def createstruct(self, request):
        global c_name_cols_mpsa, c_name_cols_ltm
        params = request.rel_url.query 
        fullpath = self.get_fullpath(params['path'], request.remote)      # Полный путь к выделенной папке
        if not os.path.exists(fullpath):                                  # Нет выделенной папки
            return self.web.json_response('notfound')
        if len(os.listdir(fullpath)) != 0:
            return self.web.json_response('notempty')                     # Сообщаем, что папка не пустая
        # Считываем структуру из БД
        fstructs = []
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('SELECT "STRUCTFOLDERS" FROM public."SETTINGS"')
                    async for row in cur: fstructs = row[0]
        if len(fstructs) == 0: return self.web.json_response('notdbread')
        if self.sysId == 0:
            fstruct = fstructs['mpsa']
        else: fstruct = fstructs['ltm']
                    
        for folder in fstruct:
            os.mkdir(fullpath + '/' + folder)                             # Создаем папки структуры данных
        if not self.is_struct_folder(os.listdir(fullpath)):
            return self.web.json_response('notcreated')                   # Не удалось создать структуру
        
        # Создаем новую запись в информационной таблице ======================
        name_cols = [c_name_cols_mpsa, c_name_cols_ltm][self.sysId]
        dataItem = {}
        for colname in list(name_cols.keys()):
            dataItem[colname] = ''
            if name_cols[colname] == 'JSONB': dataItem[colname] = []
            
        path = urllib.parse.unquote(params['path'])
        ls = path.split(',')[1:]
        numcp = 0
        if self.sysId == 1:  # ЛТМ
            if 'КП№' in ls[-1]:
                numcp = int(ls[-1][3:])
                ls = ls[:-1]
        idx = 0
        for folder in ls:
            dataItem[list(name_cols.keys())[idx]] = folder
            idx += 1
        if self.sysId == 1: dataItem[list(name_cols.keys())[idx]] = numcp   # Для ЛТМ устанавливаем номер КП
            
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(getSql(name_cols, dataItem, self.sysId, False))        
        # =====================================================================
        return self.web.json_response(os.listdir(fullpath))               # Возвращаем созданную структуру
