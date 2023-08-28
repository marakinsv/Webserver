import json

# Возвращает строку sql для вставки или изменения элемента
def getSql(name_cols, dataItem, sysId, isUpdate, changedPrKey = []):    
    colnames = list(dataItem.keys())                  # Имена столбцов БД для записи

    if sysId == 1:
        nonumcp = False
        if dataItem.get('NUMCP', None) == None: nonumcp = True  # ЛТМ без номера КП
        
    # Удаляем пустые значения
    for colname in colnames:
        if dataItem[colname] in ['', ' ', None, 'None']: del colnames[colnames.index(colname)]
            
    s = ''    
    if not isUpdate:
        sql = 'INSERT INTO public."{}" ("'.format(['PARAMS_MPSA', 'PARAMS_LTM'][sysId]) + '","'.join(colnames) + '") VALUES('
        for colname in colnames:
            sql = sql + s + getFormatValue(name_cols, dataItem, colname)
            s = ','
        return sql + ')'
    else:
        sql = 'UPDATE public."{}" SET '.format(['PARAMS_MPSA', 'PARAMS_LTM'][sysId]) 
        for colname in colnames:
            #if colname in ['MANAGOBJ', 'OBJECT', 'SYSTEM', 'NUM']: continue  # Не обновляем данные столбцы
            sql = sql + s + '"{}"={}'.format(colname, getFormatValue(name_cols, dataItem, colname))
            s = ','
        if sysId == 0:   # МПСА
            return sql + ' WHERE "MANAGOBJ" = '"'{}'"' AND "OBJECT" = '"'{}'"' AND "SYSTEM" = '"'{}'"''.format(
                                                       dataItem['MANAGOBJ'], dataItem['OBJECT'], dataItem['SYSTEM']) 
        if sysId == 1:   # ЛТМ
            if len(changedPrKey) != 0:   # Изменилось значение первичного ключа
                colname, prevval, value = changedPrKey
                if colname == 'NUMCP':
                    return sql + ' WHERE "MANAGOBJ" = '"'{}'"' AND "OBJECT" = '"'{}'"' AND "DISTANCE" = {} AND "NUMCP" = {}'.format(
                                                           dataItem['MANAGOBJ'], dataItem['OBJECT'], dataItem['DISTANCE'], prevval)
            else:
                if not nonumcp:
                    return sql + ' WHERE "MANAGOBJ" = '"'{}'"' AND "OBJECT" = '"'{}'"' AND "DISTANCE" = {} AND "NUMCP" = {}'.format(
                                                           dataItem['MANAGOBJ'], dataItem['OBJECT'], dataItem['DISTANCE'], dataItem['NUMCP'])
                else:
                    return sql + ' WHERE "MANAGOBJ" = '"'{}'"' AND "OBJECT" = '"'{}'"' AND "DISTANCE" = {}'.format(
                                                           dataItem['MANAGOBJ'], dataItem['OBJECT'], dataItem['DISTANCE'])
            
# Возвращает отформатированное в зависимости от типа столбца БД значение в виде строки
def getFormatValue(name_cols, dataItem, colname):
    value = dataItem[colname]               # Значение для записи в БД
    vtype = name_cols[colname].upper()      # Тип значения столбца БД
    if vtype == 'TEXT': return "'{}'".format(value)
    if vtype == 'INTEGER': return '{}'.format(value)
    if vtype == 'DOUBLE': return '{}'.format(value)
    if vtype in 'JSONB': return "'{}'".format(value)
    if vtype == 'BOOLEAN': return '{}'.format(value)
