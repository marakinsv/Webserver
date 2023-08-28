import aiopg
import os
import json

# Класс обработчик событий (выполнение действий до загрузки файла)
class BefDownloadFile:
    # Конструктор   
    def __init__(self, app, web):
        app.add_routes([web.get('/befdownloadfile', self.befdownloadfile)])     # Добавление маршрута

    # Обработчик события до загрузки файла
    async def befdownloadfile(self, request):
        params = request.rel_url.query
        fullpath = self.get_fullpath(params['path'], request.remote)            # Полный путь к выделенной папке
        if not os.path.exists(fullpath):                                        # Нет выделенной в дереве папки
            return self.web.json_response('notfound')

        data = json.loads(params['data']);
        folder = data['folder']; filename = data['filename']; sdate = data['sdate']
        reason = data['reason']; user = data['user']; descr = data['descr']
        unzip = data['unzip']; replace = data['replace']

        try:
            async with aiopg.create_pool(self.dsn) as pool:
                async with pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute('SELECT "REASONS" FROM public."SETTINGS"')
                        async for row in cur:
                            reasons = row[0]                                       # Возможные причины добавления данных
                        if reasons == None: reasons = []
                        if not (reason in reasons):                                # Если такой причины добавления нет добавляем ее
                            reasons.append(reason)
                            await cur.execute('UPDATE public."SETTINGS" SET "REASONS" = '"'{}{}{}'"''.format('{', ','.join(reasons), '}'))
        except Exception:
            print('Ошибка при обновлении причины загрузки')
                        
        if not os.path.exists(fullpath + '/' + folder):                         # Папка, в которую загружается файл не найдена
            return self.web.json_response('notexists')
        
        self.downdata[request.remote] = (fullpath + '/' + folder, filename, sdate, reason, user, descr, unzip)
        
        downname = fullpath + '/' + folder + '/' + filename                     # Имя загружаемого файла
        if downname in self.downfiles:                                          # Файл уже загружается с другого хоста
            return self.web.json_response('collision')

        if replace:
            self.downfiles.append(downname)                                     # Сохраняем имя загружаемого файла
            self.downhosts[downname] = request.host
            return self.web.json_response('success')
        
        path = fullpath + '/' + folder
        if unzip:                                 # Распаковать файл
            folder = sdate #folder = sdate.replace('_', '')
            if os.path.exists(path + '/' + folder):
                return self.web.json_response('existsfolder')
        else:
            fullname = path + '/' + sdate + '_' + filename
            if os.path.exists(fullname):
                return self.web.json_response('existsfile')
        
        self.downfiles.append(downname)                                        # Сохраняем имя загружаемого файла
        self.downhosts[downname] = request.host
        return self.web.json_response('success')
        
