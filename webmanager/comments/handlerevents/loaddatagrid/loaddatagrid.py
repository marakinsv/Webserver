import aiopg
import datetime
import json
from ..constants import *

c_any_txt = '<НЕТ>'
c_any_person = '|ИНКОГНИТО|'

def strToDate(st):
    ls = st.split('.')
    return datetime.date(int(ls[2]), int(ls[1]), int(ls[0]))

def checkStrDate(st):
    if st == '': return False
    try:
        strToDate(st)
    except:
        return False
    else: return True

# Класс обработчик события (загрузка данных в grid)
class LoadDataGrid:
    # Конструктор   
    def __init__(self, app, web):       
        app.add_routes([web.get('/loaddatagrid', self.loaddatagrid)])  # Добавление маршрута

    # Обработчик загрузки данных в grid
    async def loaddatagrid(self, request):
        params = request.rel_url.query
        #print(params['filter'])

        dataFilter = json.loads(params['filter'])               # Параметры фильтра grid
        
        fmanagobj = dataFilter.get('MANAGOBJ', c_any_txt)
        fobj = dataFilter.get('OBJECT', c_any_txt)
        fsystem = dataFilter.get('SYSTEM', c_any_txt)
        fsdtime = dataFilter.get('SDATETIME', '')
        fstep = dataFilter.get('STEP', c_any_txt)
        flevel = dataFilter.get('LEVEL', c_any_txt)
        fperson = dataFilter.get('PERSON', c_any_txt)
        fstatus = dataFilter.get('STATUS', c_any_txt)
        flimitsdtime = dataFilter.get('LIMITSDATETIME', '')
        fisdeleted = bool(dataFilter.get('ISDELETED', 0))

        ret = []
        managobjs = None
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('SELECT "MANAGOBJS" FROM public."CHOSE"')   # Запрашиваем все РНУ
                    async for row in cur: managobjs = row[0]
                    if managobjs == None: return self.web.json_response({})
                    for managobj in managobjs:        # Проходимся по всем РНУ
                        if fmanagobj != c_any_txt:
                            if managobj != fmanagobj: continue
                        sql = 'SELECT * FROM public."NOTICE" \
                                 WHERE "MANAGOBJ" = '"'{}'"' AND "ISDELETED" = {} ORDER BY "OBJECT", "SYSTEM", "NUM"'.format(managobj, fisdeleted)
                        if fobj != c_any_txt:
                            sql = 'SELECT * FROM public."NOTICE" \
                                     WHERE "MANAGOBJ" = '"'{}'"' AND "OBJECT" = '"'{}'"' AND "ISDELETED" = {} ORDER BY "SYSTEM", "NUM"'.format(
                                                                                                                     managobj, fobj, fisdeleted)

                        await cur.execute(sql)
                        async for row in cur:
                            data = dict(zip(list(c_name_cols.keys()), row))
                            # Фильтрация данных ================
                            if fsystem != c_any_txt:
                                if data['SYSTEM'] != fsystem: continue
                            if fsdtime != '' and flimitsdtime == '' and data['SDATETIME'] != '':
                                if data['SDATETIME'] != fsdtime: continue  # ====================== startDTimeBlock.strftime(c_formatDate)
                            if flimitsdtime != '' and fsdtime == '' and data['LIMITSDATETIME'] != '':
                                if data['LIMITSDATETIME'] != flimitsdtime: continue
                            if fsdtime != '' and flimitsdtime != '' and checkStrDate(data['SDATETIME']):
                                d = strToDate(data['SDATETIME'])
                                if d < strToDate(fsdtime): continue
                                if d > strToDate(flimitsdtime): continue                    
                            if fstep != c_any_txt:
                                if data.get('STEP', -1) != fstep: continue
                            if flevel != c_any_txt:
                                if data['LEVEL'] != flevel: continue
                            if fperson != c_any_txt and fperson != c_any_person:
                                if data['PERSON'] != fperson: continue
                            elif fperson == c_any_person:
                                if data['PERSON'] != '': continue
                            if fstatus != c_any_txt:
                                if data['STATUS'] != fstatus: continue
                            # ===================================
                            ret.append(data)
        return self.web.json_response(ret)
