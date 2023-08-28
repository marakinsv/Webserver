import aiopg
import json
import urllib
from ..general import getSql
from ..constants import c_name_cols_mpsa, c_name_cols_ltm

# Класс обработчик события (обновление элемента grid)
class UpdateItemGrid_:
    # Конструктор   
    def __init__(self, app, web):       
        app.add_routes([web.get('/updateitemgrid_', self.updateitemgrid_)])  # Добавление маршрута

    # Обработчик обновления элемента grid
    async def updateitemgrid_(self, request):
        global getSql, c_name_cols_mpsa, c_name_cols_ltm
        params = request.rel_url.query
        dataItem = json.loads(params['dataitem'])
        # Раскодируем название
        for key in dataItem.keys():
            dataItem[key] = urllib.parse.unquote(dataItem[key])

        changedPrKey = []
        if self.sysId == 1:   # ЛТМ
            if dataItem['NUMCP'] != self.previousItem.get('NUMCP', dataItem['NUMCP']): # Изменили номер КП
                changedPrKey = ['NUMCP', self.previousItem['NUMCP'], dataItem['NUMCP']]
        
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(getSql([c_name_cols_mpsa, c_name_cols_ltm][self.sysId], dataItem, self.sysId, True, changedPrKey))
                    
        return self.web.json_response([1])
