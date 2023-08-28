import json

# Возвращает строку sql для вставки или изменения элемента
def getSql(name_cols, dataItem, isUpdate):    
    colnames = list(dataItem.keys())                # Имена столбцов БД для записи
    if isUpdate:
        if 'ISDELETED' in colnames:
            del colnames[colnames.index('ISDELETED')]
    else: dataItem['ISDELETED'] = False
        

    # Удаляем пустые значения
    for colname in colnames:
        if dataItem[colname] in ['', ' ', None]: del colnames[colnames.index(colname)]
            
    s = ''    
    if not isUpdate:
        sql = 'INSERT INTO public."NOTICE" ("' + '","'.join(colnames) + '") VALUES('
        for colname in colnames:
            sql = sql + s + getFormatValue(name_cols, dataItem, colname)
            s = ','
        return sql + ')'
    else:
        sql = 'UPDATE public."NOTICE" SET ' 
        for colname in colnames:
            if colname in ['MANAGOBJ', 'OBJECT', 'SYSTEM', 'NUM']: continue  # Не обновляем данные столбцы
            sql = sql + s + '"{}"={}'.format(colname, getFormatValue(name_cols, dataItem, colname))
            s = ','
        return sql + ' WHERE "MANAGOBJ" = '"'{}'"' AND "OBJECT" = '"'{}'"' AND "SYSTEM" = '"'{}'"' AND "NUM" = {}'.format(
                                                    dataItem['MANAGOBJ'], dataItem['OBJECT'], dataItem['SYSTEM'], dataItem['NUM']) 
 
# Возвращает отформатированное в зависимости от типа столбца БД значение в виде строки
def getFormatValue(name_cols, dataItem, colname):
    value = dataItem[colname]               # Значение для записи в БД
    vtype = name_cols[colname].upper()      # Тип значения столбца БД
    if vtype == 'TEXT': return "'{}'".format(value)
    if vtype == 'INTEGER': return '{}'.format(value)
    if vtype in 'JSONB': return "'{}'".format(value)
    if vtype == 'BOOLEAN': return '{}'.format(value)
