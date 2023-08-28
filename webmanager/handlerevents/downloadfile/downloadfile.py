import aiopg
import aiohttp
import asyncio
import os
import json
import zipfile
import shutil
import uuid
from datetime import datetime
from datatable.handlerevents.general import getSql
from datatable.handlerevents.constants import c_name_cols_mpsa, c_name_cols_ltm

#import win32com.client

# Класс обработчик событий (загрузка файла с клиента на сервер)
class DownloadFile:
    # Конструктор   
    def __init__(self, app, web):
        app.add_routes([web.get('/ws', self.downloadfile)])     # Добавление маршрута

    # Обработчик загрузки файла
    async def downloadfile(self, request):
        ws = self.web.WebSocketResponse()
        await ws.prepare(request)

        if self.downdata.get(request.remote, None) == None:
            await ws.send_bytes(b'dataunknown')                 # Отправляем сокету, что данные д.б. сформированные в befdownloadfile не определены
            await ws.close()
            return ws

        datalist = self.downdata[request.remote]
        path, filename, sdate, reason, user, descr, unzip = datalist
        downname = path + '/' + filename                        # Имя загружаемого файла
        del self.downdata[request.remote]                       # Удаляем данные текущей загрузки
        if unzip:
            fullname = path + '/' + filename.split('.')[0] + '[temp-' + str(uuid.uuid4()) + ']' + '.' + filename.split('.')[1]
            self.archfiles.append(fullname)
        else:
            fullname = path + '/' + sdate + '_' + filename       
        try:
            return await self._downloadfile(request, ws, datalist, fullname)
        finally:
            if unzip: self.archfiles.pop(self.archfiles.index(fullname))
            self.downfiles.pop(self.downfiles.index(downname))  # Удаляем имя загружаемого файла
            del self.downhosts[downname]                        # Удаляем имя загружаемого файла               
        
    # Загрузка файла
    async def _downloadfile(self, request, ws, datalist, fullname):
        path, filename, sdate, reason, user, descr, unzip = datalist
        error = False; success = False
        try:
            with open(fullname, 'wb') as fw:
                count = 0
                async for msg in ws:                            # Обрабатываем полученные данные (пока сокет открыт мы в этом цикле)
                    #print(msg.data)
                    if msg.type == aiohttp.WSMsgType.ERROR:
                        error = True
                        await ws.send_bytes(b'error')           # Сообщаем клиенту, что произошла ошибка при загрузке файла
                        break
                    if msg.data == b'\x04':                     # Конец передачи
                        success = True
                        break
                    #if msg.type == aiohttp.WSMsgType.BINARY:
                    fw.write(msg.data)
                    count += 1
                    if count >= 10:
                        await ws.send_bytes(b'proc')            # Сообщаем клиенту, что 10 частей блока файла записаны
                        count = 0
            if not success: error = True
            if error: os.remove(fullname)                       # Удаляем загружаемый файл
        except Exception as e:
            os.remove(fullname)                                 # Удаляем загружаемый файл
            error = True
            print('Ошибка "{}" при приеме файла с хоста {}'.format(str(e), request.remote))
            await ws.send_bytes(b'error')
    
        if not error and unzip:
            folder = sdate #folder = sdate.replace('_', '')
            try:
                await self.unarchive_file(fullname, path + '/' + folder, request.app.loop, ws)  # Разархивируем файл
            except OSError as e:
                error = True
                print('Ошибка распаковки файла {}'.format(str(e)))
                await ws.send_bytes(b'unpackerror')             # Сообщаем клиенту, что произошла ошибка распаковки
            os.remove(fullname)                                 # Удаляем исходный файл 
        if not error:
            try:
                await self.saveLogDownload(path, filename, sdate, reason, user, descr)  # Сохраняем лог
            except Exception as e:
                print('Ошибка логирования "{}" при приеме файла с хоста {}'.format(str(e), request.remote))
                await ws.send_bytes(b'logerror')                # Сообщаем клиенту, что произошла ошибка логирования
            try:
                await self.updateDateDownloadFile(path, sdate)  # Обновляем дату загрузки файла
            except Exception as e:
                print('Ошибка обновления даты загрузки "{}" при приеме файла с хоста {}'.format(str(e), request.remote))
                await ws.send_bytes(b'updatedateerror')         # Сообщаем клиенту, что произошла ошибка обновления даты загрузки файла
            try:
                self.updateDateDownloadFile_(path, sdate)       # Обновляем дату загрузки файла в Excel
            except Exception as e:
                print('Ошибка обновления даты загрузки в Excel "{}" при приеме файла с хоста {}'.format(str(e), request.remote))
                await ws.send_bytes(b'updatedateerror_')        # Сообщаем клиенту, что произошла ошибка обновления даты загрузки файла
                
            await ws.send_bytes(b'success')                     # Сообщаем клиенту, что все прошло успешно
            
        await ws.close()
        return ws

# Дополнительные методы ========================================
    # Разархивирование файла
    async def unarchive_file(self, filename, target_folder, loop, ws):
        if not os.path.exists(target_folder):
            os.mkdir(target_folder)                     # Создаем папку для распакованных файлов
        else:
            await ws.send_bytes(b'prepunpack')          # Сообщаем клиенту, что началось удаление папки
            await loop.run_in_executor(None, shutil.rmtree, target_folder)
            #shutil.rmtree(target_folder)                # Удаляем папку со всем содержимым
            os.mkdir(target_folder)                     # Создаем папку для распакованных файлов

        sz = os.path.getsize(filename)
        await ws.send_bytes(bytes('startunpack:' + str(sz), encoding = 'cp437')) # Сообщаем клиенту, что началась распаковка и размер файла
        b = False; size = 0
        with zipfile.ZipFile(filename, 'r') as zf:
            for fileinfo in zf.infolist():
                fname = fileinfo.filename.replace('\\', '/').encode('cp437').decode('cp866')  # Для возможности распаковка русских имен
                if not b:
                    os.mkdir(target_folder + '/' + fname.split('/')[0])    # Создаем корневую папку
                    b = True
                if not self.isfile(fname):              # Это папка
                    if not os.path.exists(target_folder + '/' + fname):
                        os.makedirs(target_folder + '/' + fname)
                else:
                    filename = target_folder + '/' + fname                 # Имя файла
                    path = '/'.join(filename.split('/')[:-1])
                    if not os.path.exists(path): os.makedirs(path)         # Создаем папку для файла, если ее нет
                    with open(filename, "wb") as fw:
                        shutil.copyfileobj(zf.open(fileinfo.filename), fw)
                    # Сообщаем клиенту кол-во байт разжатого файла
                    size = size + fileinfo.compress_size
                    if size > 10*1000*1000:             # Больше 10 Мб
                        await ws.send_bytes(bytes('procunpack:' + str(size), encoding = 'cp437'))
                        size = 0
                await asyncio.sleep(0.05)
        
    # Сохранение лога загруженного файла
    async def saveLogDownload(self, path, filename, sdate, reason, user, descr):
        ls = path.split('/')
        path = '/'.join(ls[:-1])
        if self.sysId == 0:                 # 0 - МПСА
            partition = ls[-1][3:]; tablename = 'LOG_MPSA'
        else:
            partition = ls[-1]; tablename = 'LOG_LTM'            

        values = (ls[-4], ls[-3], ls[-2], partition, sdate, str(datetime.now()), reason, user, descr)
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('INSERT INTO public."{}" VALUES{}'.format(tablename, values))
                    
        # ============== Потом удалить код ниже ==========================================================           
        with open(path + '/log_txt.txt', 'a') as fl:
            fl.write('Дата: {}\n'.format(sdate))
            fl.write('Раздел: {}\n'.format(partition))
            fl.write('Причина внесения: {}\n'.format(reason))
            fl.write('Автор: {}\n'.format(user))
            fl.write('Описание: {}\n'.format(descr))
            fl.write('-------------\n')

    # Обновление даты загруженного файла в сводной таблице информации
    async def updateDateDownloadFile(self, path, sdate):
        global c_name_cols_mpsa, c_name_cols_ltm
        ls = path.split('/')
        struct_folder = ls[-1]  # Папка структуры куда загружается файл
        if '.' in struct_folder: struct_folder = struct_folder[struct_folder.index('.')+1:]
        dataItem = {}
        if self.sysId == 0:     # МПСА
            dataItem['SYSTEM'] = ls[-2]; dataItem['OBJECT'] = ls[-3]; dataItem['MANAGOBJ'] = ls[-4]
        else:                   # ЛТМ
            dataItem['DISTANCE'] = ls[-2]; dataItem['OBJECT'] = ls[-3]; dataItem['MANAGOBJ'] = ls[-4]

        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    data = []
                    await cur.execute('SELECT * FROM public."{}"'.format(['HEAD_PARAMS_MPSA', 'HEAD_PARAMS_LTM'][self.sysId]))
                    async for row in cur: data = row[0]
                    num = 1
                    for item in data:
                        if item['title'].upper() == struct_folder.upper(): break
                        num += 1
                    if len(data) > 0:
                        dataItem['PARAM{}'.format(num)] = sdate
                        await cur.execute(getSql([c_name_cols_mpsa, c_name_cols_ltm][self.sysId], dataItem, self.sysId, True))
                    
    # ============== Потом удалить процедуру ==========================================================
    def updateDateDownloadFile_(self, path, sdate):
        ls = path.split('/')
        partition = ls[-1]  # Раздел
        if '.' in partition: partition = partition[partition.index('.')+1:]
        
        managObj = ls[-4]; obj = ls[-3]
        if self.sysId == 0:     # МПСА
            system = ls[-2]
        else:                   # ЛТМ
            distance = ls[-2]
        
        filename = [self.dirs[0] + 'mpsa_manager.xlsm', self.dirs[1] + self.rootFolders[1] + '/backup_tm_remote.xlsm'][self.sysId]
        
        excel = win32com.client.Dispatch("Excel.Application")
        try:
            wb = excel.Workbooks.Open(filename)
            try:
                ws = wb.Worksheets(managObj)

                idx_col = None
                for col in range(1, 100):
                    if ws.Cells(1, col).value == None: continue
                    head = ws.Cells(1, col).value
                    if head.upper() == partition.upper():
                        idx_col = col; break        
                if idx_col == None: raise Exception
                finded = False
                for row in range([2, 3][self.sysId], 120):
                    if ws.Cells(row, 1).value == None: break
                    if self.sysId == 0:     # МПСА
                        obj_ = ws.Cells(row, 2).value
                        system_ = ws.Cells(row, 3).value
                        if obj_.upper() == obj.upper() and system_.upper() == system.upper():
                            ws.Cells(row, idx_col).value = sdate
                            finded = True
                            break
                    else:                   # ЛТМ
                        obj_ = ws.Cells(row, 2).value
                        distance_ = ws.Cells(row, 3).value
                        if obj_.upper() == obj.upper() and float(distance_) == float(distance):
                            ls = sdate.split('_')
                            ws.Cells(row, idx_col).value = '{}.{}.{}'.format(ls[-1], ls[1], ls[0])
                            finded = True                        
                if not finded: raise Exception
                wb.Save()
            finally:
                wb.Close()
        finally:
            excel.Quit()
