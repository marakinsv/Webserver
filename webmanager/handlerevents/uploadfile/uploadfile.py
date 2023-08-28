import aiofiles
import os
import uuid
import zipfile
import asyncio

# Класс обработчик событий (выгрузка файла с сервера)
class UploadFile:
    # Конструктор   
    def __init__(self, app, web):
        app.add_routes([web.get('/uploadfile', self.uploadfile)])     # Добавление маршрута
        
    # Обработчик выгрузки файла
    async def uploadfile(self, request):
        params = request.rel_url.query
        fullpath = self.get_fullpath(params['path'].replace('\xa0', ' '), request.remote) # Полный путь к выделенной папке
        selfolder = params['selfolder'].replace('\xa0', ' ')
        viewpath = params['viewpath'].replace('\xa0', ' ')
        isfile = int(params['isfile'])
        if isfile:                                                      # Это файл
            upfilename = params['upfilename'].replace('\xa0', ' ')
        else: upfoldername = params['upfoldername'].replace('\xa0', ' ')
        
        if not os.path.exists(fullpath):                                # Нет выделенной в дереве папки
            return self.web.json_response('Folder by select node in tree not found. Update tree!')
        path = fullpath + '/' + selfolder
        if not os.path.exists(path):                                    # Нет выделенной во вкладке папки
            return self.web.json_response('Folder by select tab not found. Reselect node tree')
        if viewpath != '':
            path = path + '/' + viewpath
            if not os.path.exists(path):                                # Нет пути, куда перешли при просмотре папок
                return self.web.json_response('Viewed path not found. Reselect current tab!')
        if isfile:
            if not os.path.exists(path + '/' + upfilename):             # Нет файла для выгрузки
                return self.web.json_response('Upload file not found. Reselect current tab!')
        else:
            if not os.path.exists(path + '/' + upfoldername):           # Нет папки для выгрузки
                return self.web.json_response('Upload folder not found. Reselect current tab!')
        
        if isfile: return self.web.FileResponse(path + '/' + upfilename) # Отправляем файл
        # Если это папка ===================================
        zfilename = path + '/' + upfoldername + '[temp-' + str(uuid.uuid4()) + '].zip'  # Имя временного архивного файла
        self.archfiles.append(zfilename)
        try:
           return await self._uploadfile(request, zfilename, path + '/' + upfoldername)
        finally:
            os.remove(zfilename)                                          # Удаляем архив
            self.archfiles.pop(self.archfiles.index(zfilename))
        
    # Выгрузки файла
    async def _uploadfile(self, request, zfilename, target_folder):
        try:
            await self.archive_file(zfilename, target_folder)             # Архивируем файл
        except OSError as e:
            os.remove(zfilename)
            return self.web.json_response('Error {} packing folder!'.format(str(e)))
            
        resp = self.web.StreamResponse(
            status = 200,
            reason = 'OK',
            headers = {'Content-Type': 'application/stream'},
        )
        #resp.enable_chunked_encoding()
        #resp.enable_compression()
        await resp.prepare(request)
        
        async with aiofiles.open(zfilename, 'rb') as fr:
            while True:
                data = await fr.read(2**16)
                if not data:
                    await resp.drain()
                    break
                await resp.write(data)
        return resp

# Дополнительные методы ===============================================================
    # Архивирование файла
    async def archive_file(self, filename, target_folder):
        try:
            file_zip = zipfile.ZipFile(filename, 'w')
            for folder, subfolders, files in os.walk(target_folder):
                for file in files:
                    file_zip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), target_folder),
                                     compress_type = zipfile.ZIP_DEFLATED)
                    await asyncio.sleep(0.001) 
        finally:
            file_zip.close()
       
        
        
