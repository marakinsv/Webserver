import os
from logging import getLogger, StreamHandler, DEBUG
import json
from time import sleep
from datetime import datetime
#from threading import Thread
import urllib

import aiohttp
from aiohttp import web
import aiopg
#import aiofiles
import zipfile
import asyncio

# Импорт обработчиков событий =================================
from handlerevents.selectnode.selectnode import SelectNode
from handlerevents.createnode.createnode import CreateNode
from handlerevents.deletenode.deletenode import DeleteNode
from handlerevents.renamenode.renamenode import RenameNode
from handlerevents.createstruct.createstruct import CreateStruct
from handlerevents.changetab.changetab import ChangeTab
from handlerevents.gotoinside.gotoinside import GotoInside
from handlerevents.showinputframe.showinputframe import ShowInputFrame
from handlerevents.befdownloadfile.befdownloadfile import BefDownloadFile
from handlerevents.downloadfile.downloadfile import DownloadFile
from handlerevents.uploadfile.uploadfile import UploadFile
# Классы обработчики событий
cls_handlers = (SelectNode, CreateNode, DeleteNode, RenameNode, CreateStruct, ChangeTab, GotoInside, ShowInputFrame,
                  BefDownloadFile, DownloadFile, UploadFile)

# Импорт обработчиков событий (таблица замечаний) =================================
from comments.handlerevents.createfieldsgrid.createfieldsgrid import CreateFieldsGrid
from comments.handlerevents.loaddatagrid.loaddatagrid import LoadDataGrid
from comments.handlerevents.befinsertitemgrid.befinsertitemgrid import BefInsertItemGrid
from comments.handlerevents.insertitemgrid.insertitemgrid import InsertItemGrid
from comments.handlerevents.befupdateitemgrid.befupdateitemgrid import BefUpdateItemGrid
from comments.handlerevents.deleteitemgrid.deleteitemgrid import DeleteItemGrid
from comments.handlerevents.updateitemgrid.updateitemgrid import UpdateItemGrid
# Классы обработчики событий
cls_handlers_ = (CreateFieldsGrid, LoadDataGrid, BefInsertItemGrid, InsertItemGrid, BefUpdateItemGrid, UpdateItemGrid, DeleteItemGrid)

# Импорт обработчиков событий (информационная таблица) =================================
from datatable.handlerevents.createfieldsgrid.createfieldsgrid import CreateFieldsGrid_
from datatable.handlerevents.loaddatagrid.loaddatagrid import LoadDataGrid_
from datatable.handlerevents.beforedataload.beforedataload import BeforeDataLoad_
from datatable.handlerevents.updateitemgrid.updateitemgrid import UpdateItemGrid_
from datatable.handlerevents.befupdateitemgrid.befupdateitemgrid import BefUpdateItemGrid_
# Классы обработчики событий
cls_handlers__ = (CreateFieldsGrid_, LoadDataGrid_, BeforeDataLoad_, UpdateItemGrid_, BefUpdateItemGrid_)

# Класс обработчик запросов
class HandlerRequest(*cls_handlers, *cls_handlers_, *cls_handlers__):
    def __init__(self, app, web_, dsn, dirs, rootFolders, rootNodeText, fileSettings):
        self.web = web_
        self.dsn = dsn
        # Создаем классы обработчики событий
        for cls in cls_handlers: cls.__init__(self, app, web_)
        for cls in cls_handlers_: cls.__init__(self, app, web_)
        for cls in cls_handlers__: cls.__init__(self, app, web_)
        # ----------------------------------------------
        self.sysId = None                 # Идентификатор системы (0 - МПСА, 1 - ЛТМ)
        #self.dir = None
        #self.rootFolder = None
        self.maxLevel = None
        #self.offsetLevel = 0
        for idx in range(len(dirs)):
            if dirs[idx][-1] != '/': dirs[idx] += '/'
        self.dirs = dirs                  # Директории расположения корневой папки
        self.rootFolders = rootFolders    # Корневые папки
        self.rootNodeText = rootNodeText  # Название корневого узла
        self.fileSettings = fileSettings  # Файл с настройками        
        self.paths = [{}, {}]             # Пути к директориям, с которыми работаем в данный момент, для каждого клиента свой
        self.downdata = {}                # Данные загружаемых на сервер файлов
        self.downfiles = []               # Загружаемые в данный момент файлы (исключение записи одного файла с разных клиентов)
        self.downhosts = {}               # Все хосты, с к-х загружаются файлы
        self.archfiles = []               # Список временных архивных файлов
        self.previousItem = {}            # Значения предыдущих элементов для информ. таблицы
        self.sysIds = {}                  # Идентификаторы системы (МПСА, ЛТМ) для каждого клиента
        
# Вспомогательные методы -----------------------
    # Проверка, что это файл    
    def isfile(self, fname):
        if fname[-1] == '/' or fname[-1] == '\\': fname = fname[:-1]
        if '/' in fname: fname = fname.split('/')[-1]
        if '\\' in fname: fname = fname.split('\\')[-1]
        if not ('.' in fname): return False
        ext = fname.split('.')[-1]        # Расширение файла
        if ext.isdigit(): return False
        if len(ext) > 8: return False
        return True
    
    # Это временный файл (остался после распаковки, упаковки при ошибке)
    def istempfile(self, fullname):
        if fullname.count('.') == 0: return False
        if fullname.count('/') > 0:
            filename = fullname.split('/')[-1]
        else: filename = fullname.split('\\')[-1]
        if filename.split('.')[-1] != 'zip': return False
        if not ('[temp-' in filename and ']' in filename): return False
        if filename.count('-') < 5: return False
        return True
    
    # Удаление временного файла (если находим временный файл, то удаляем его в отдельном потоке)
    def deleteTempFiles(self, path, listfiles):
        for filename in listfiles:
            if self.istempfile(path + '/' + filename):
                if self.archfiles.count(path + '/' + filename) > 0: continue  # Идет операция с файлом
                thread = Thread(target = os.remove, args = (path + '/' + filename,)) # Создаем отдельный поток
                thread.start()                                          # Запускаем поток
        
    # Возвращает полный путь к папке
    def get_fullpath(self, path, rhost):
        sysId = self.sysIds[rhost]
        return self.dirs[sysId] + urllib.parse.unquote(path).replace(',', '/').replace(self.rootNodeText, self.rootFolders[sysId])

    # Проверка принадлежит ли папка структуре данных
    def is_struct_folder(self, folders):
        for folder in folders:
            if self.sysId == 0:                             # 0 - МПСА, 1 - ЛТМ
                if folder[:3] == '01.': return True
            elif 'BACKUP' in folder.upper(): return True
        return False
        
    # Возвращает описатель директории, в которой находится указанный файл
    def get_dir_descr(self, filename):
        if os.path.exists(filename):                     # Имеется файл - описатель текущей директории
            with open(filename) as fl:
                return eval(fl.read().strip())
        return {}
    
    # Возвращает уровень элемента в дереве
    def get_level_tree(self, listPairId, parentId, level = 0):
        path = ''
        if len(listPairId) == 0: return (0, path)
        while True:
            exists = False
            for itemId, parentId_, itemText in listPairId:   # Перебираем все пары идентификаторов списка
                if parentId == itemId:
                    exists = True
                    level += 1
                    path = itemText + '/' + path
                    parentId = parentId_
                    if itemId == 0: return (level, path)     # Добрались до корневого элемента
            if not exists: return (None, '')                 # Элемент не найден

    # Формирование данных для построения дерева из папок на диске (рекурсия)
    async def build_data_tree(self, data, listPairId, itemId, parentId, dir_, remoteHost):
        folders = os.listdir(dir_)                           # Получаем список всех папапок в указанной директории
        if len(folders) == 0: return
        parentId = itemId[0]                                 # Идентификатор родительского элемента
        level, path = self.get_level_tree(listPairId, parentId)
        if level > self.maxLevel: return
        #if level == 2 and self.sysId == 1: folders.sort()
        for folder in folders:
            self.offsetLevel = 0
            if level == 1 and not (folder in ['КРНУ', 'АРНУ', 'РРНУ', 'УРНУ', 'ПРНУ']): continue
            if self.isfile(folder): continue                 # Пропускаем файлы
            itemId[0] += 1                                   # Идентификатор элемента
            listPairId.append((itemId[0], parentId, folder))
            #print(folder, itemId, parentId, level, path + folder)
            if self.paths[self.sysId].get(remoteHost, '') != '':         # Есть выделенная папка
                op = path + folder in self.paths[self.sysId][remoteHost]
            else: op = level == 0
            data.append({'id': itemId[0], 'text': folder, 'children': [], 'state': {'opened': op}})
            await self.build_data_tree(data[-1]['children'], listPairId, itemId, parentId, dir_ + '/' + folder, remoteHost)
            await asyncio.sleep(0.001)
            
    # Проверка прав на подключение к серверу
    '''async def check_connection_rights(self, request, need_update, need_update_dtime = False):
        finded = False
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('SELECT * FROM public."REMOTEHOSTSINFO" WHERE "REMOTEHOST" = '"'{}'"''.format(request.remote))
                    async for row in cur:
                        _, loginCount, entryDTime, identName = row
                        finded = True
                    if need_update and not finded:
                        await cur.execute('INSERT INTO public."REMOTEHOSTSINFO" VALUES('"'{}'"', {}, '"'{}'"', '"'{}'"')'.
                                          format(request.remote, 0, datetime.now(), ' '))
                    elif need_update:
                        loginCount += 1
                        dt = datetime.now() - entryDTime
                        if dt.days > 21:
                            loginCount = 0; identName = ' '
                        await cur.execute('UPDATE public."REMOTEHOSTSINFO" SET "LOGINCOUNT" = {1}, "ENTRYDTIME" = '"'{2}'"', "IDENTNAME" = '"'{3}'"' \
                                             WHERE "REMOTEHOST" = '"'{0}'"''.format(request.remote, loginCount, datetime.now(), identName))
                    elif need_update_dtime:
                        await cur.execute('UPDATE public."REMOTEHOSTSINFO" SET "ENTRYDTIME" = '"'{1}'"'WHERE "REMOTEHOST" = '"'{0}'"''.
                                          format(request.remote, datetime.now()))
        if not finded: return False
        
        dt = datetime.now() - entryDTime                                
        if loginCount < 5 or dt.days > 21: return False
        
        return True'''

# Обработчики запросов -------------------------
    # Обработчик возвращающий главную страницу
    async def handler_index(self, request):
        return web.FileResponse('./login.html')
    
    async def handler_login(self, request):
        data = await request.post()
        if data['login'] != 'Ospas' or data['pwd'] != 'Ospas_843!':  # Не верный пароль
            return web.FileResponse('./login.html')

        self.sysId = int(data['sysid'])       # Идентификатор системы (0 - МПСА, 1 - ЛТМ)
        
        #self.dir = self.dirs[self.sysId]
        #self.rootFolder = self.rootFolders[self.sysId]
        self.maxLevel = [3, 3][self.sysId]

        self.sysIds[request.remote] = int(data['sysid'])  # Идентификатор системы (0 - МПСА, 1 - ЛТМ)
       
        return web.FileResponse('./index.html')
    
    # Обработчик возвращающий страницу замечаний
    async def handler_comments(self, request):
        return web.FileResponse('./comments/index.html')

    # Обработчик возвращающий страницу таблицы данных
    async def handler_datatable(self, request):
        return web.FileResponse('./datatable/index.html')
    
   # async def handler_tablehtml(self, request):
        return web.FileResponse('./table.html')
   # 
    async def handler_jquery(self, request):
        return web.FileResponse('./jquery-3.3.1.min.js')

    async def handler_jquery_ui(self, request):
        return web.FileResponse('./jquery-ui-1.12.1/jquery-ui.min.js')

    async def handler_jquery_ui_css(self, request):
        return web.FileResponse('./jquery-ui-1.12.1/jquery-ui.css')
    
    async def handler_jstree(self, request):
        return web.FileResponse('./jstree.min.js')
    
    async def handler_main(self, request):
        return web.FileResponse('./main.js')

    async def handler_stylecss(self, request):
        return web.FileResponse('./themes/default/style.min.css')
    
    async def handler_stylecss_(self, request):
        return web.FileResponse('./main.css')
    
    async def handler_image(self, request):
        return web.FileResponse('./themes/default/32px.png')

    async def handler_image_(self, request):
        return web.FileResponse('./images/upload.png')

    async def handler_build_tree(self, request):
        #print('handler_build_tree')
        #sleep(10)
        params = request.rel_url.query
        '''if params.get('clear', None) != None:
            # Очищаем информацию о загрузке с указанного в запросе хоста на сервер
            removenames = []
            if len(self.downhosts) > 0:
                downnames = list(self.downhosts.keys())
                hosts = list(self.downhosts.values())
                for host in list(hosts):
                    if host != request.host: continue
                    idx = hosts.index(host)
                    removenames.append(downnames[idx])
            if len(removenames) > 0:
                for downname in removenames:
                    del self.downhosts[downname]
                    if downname in self.downfiles:
                        self.downfiles.pop(self.downfiles.index(downname))
        # ============================================='''
        sysId = self.sysIds[request.remote]
        itemId = [0]    # Список, чтобы значение передавалось по ссылке
        parentId = itemId[0]
        data = [{'id': 0, 'text': self.rootNodeText, 'children': [], 'state': {'opened': True}}]
        listPairId = [(0, None, self.rootFolders[sysId])] # Список идентификаторов пар (идент. элемента, идент. его родительского элемента, название элемента)
        try:
            await self.build_data_tree(data[0]['children'], listPairId, itemId, parentId,
                                       self.dirs[sysId] + self.rootFolders[sysId], request.remote)
        except Exception:
            print('handler_build_tree: Ошибка при восстановлении дерева папок')
            return web.json_response({'error': True})
        return web.json_response(data)

    # Возвращает идентификатор системы
    async def handler_getsysid(self, request):
        return web.json_response({'sysid': self.sysIds[request.remote]})
        
    
# ====================================================================
app = web.Application()

dirs =        ['c:/OSPAS', 'c:/OSPAS/ЭКСПЛУАТАЦИЯ_МПСА']
rootFolders = ['Backup', 'backupTM']

dsn = 'dbname={0} user={1} password={2} host={3}'.format('new_db', 'postgres', 'msv', 'localhost')   # Параметры подключения к БД

handler = HandlerRequest(app, web, dsn, dirs = dirs, rootFolders = rootFolders, rootNodeText = 'ОСПАС', fileSettings = 'data/settings')
#print(dir(web))
app.add_routes([web.post('/login', handler.handler_login)])
app.add_routes([web.get('/OSPAS', handler.handler_index)])
app.add_routes([web.get('/comments', handler.handler_comments)])
app.add_routes([web.get('/datatable', handler.handler_datatable)])
app.add_routes([web.get('/main.js', handler.handler_main)])
app.add_routes([web.get('/themes/default/style.min.css', handler.handler_stylecss)])
app.add_routes([web.get('/main.css', handler.handler_stylecss_)])
app.add_routes([web.get('/themes/default/32px.png', handler.handler_image)])
app.add_routes([web.get('/images/upload.png', handler.handler_image_)])
app.add_routes([web.get('/treeview', handler.handler_build_tree)])
app.add_routes([web.get('/getsysid', handler.handler_getsysid)])

# =================================================

#app.add_routes([web.get('/comments', handler.static_comments)])                       # Страница администрирования

app.router.add_static('/handlerevents/', path=str('./handlerevents/'))
app.router.add_static('/comments/handlerevents/', path=str('./comments/handlerevents/'))
app.router.add_static('/datatable/handlerevents/', path=str('./datatable/handlerevents/'))
app.router.add_static('/jstree/', path=str('./jstree/'))
app.router.add_static('/jsgrid/', path=str('./jsgrid/'))
app.router.add_static('/jquery/', path=str('./jquery/'))
app.router.add_static('/static/', path=str('./static/'))
'''log = getLogger('aiohttp.access')
log.setLevel(DEBUG)
log.addHandler(StreamHandler())
log_format = '%a %t "%r" %s %b "%{User-Agent}i" %Tfsec'''
#app.on_startup.append(handler.start_background_tasks)
web.run_app(app, port=8080)#, access_log=log, access_log_format=log_format)
