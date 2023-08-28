// Обработчик создания полей грида
function createFieldsGrid(path) {
	var c_any_txt = '<НЕ ЗАДАН>';
	// Запрашиваем данные для списков значений из БД
	var fields = [];
	if (path.split(',').length > 3)
		fields.push({type: 'control', clearFilterButton: false, deleteButton: false, 'width': 7});
    $.ajax({
        url: 'http://' + g_rhost + '/createfieldsgrid_',
        dataType: 'json',
        async: false,
        success: function(data) {
	        data.forEach(function(param) {
		        item = {};
		        item['name'] = param['name'];
                item['filtering'] = param['filtered'];	
                item['editing'] = param['edited'];				
		        item['type'] = param['type'];
		        item['title'] = param['title'];
		        item['align'] = 'center';
		        item['width'] = param['width'];
				// Чисто мои свойства
				item['pid'] = param['pid'];
				item['parentid'] = param['parentid'];
				item['childid'] = param['childid'];
				// Видимость начальных столбцов в зависимости от пути в дереве
				ls = path.split(',')
				if (param['name'] == "MANAGOBJ")
				    if (ls.length > 1) {    // Такой путь ОСПАС/ПРНУ
				        item['visible'] = false;
						g_filter["MANAGOBJ"] = ls[1];
						if (param['choice'].length > 0) item['selectedIndex'] = param['choice'].indexOf(ls[1]) + 1;
					}
				if (param['name'] == "OBJECT") 
				    if (ls.length > 2) {    // Такой путь ОСПАС/ПРНУ/Пермь-1
						item['visible'] = false;
						g_filter["OBJECT"] = ls[2];
						if (param['choice'].length > 0) item['selectedIndex'] = param['choice'].indexOf(ls[2]) + 1;
					}
				if (param['name'] == "SYSTEM" || param['name'] == "DISTANCE") 
				    if (ls.length > 3) {   // Такой путь ОСПАС/ПРНУ/Пермь-1/АСУ ТП МНС
						item['visible'] = false;
						if (g_sysid == 0) g_filter["SYSTEM"] = ls[3];
						if (g_sysid == 1) g_filter["DISTANCE"] = ls[3];
						if (param['choice'].length > 0) item['selectedIndex'] = param['choice'].indexOf(ls[3]) + 1;
					}
				
				// Значения для select
				if (param['type'] == 'select') {
					item['valueField'] = 'Name';
					item['textField'] = 'Name';				
					item['validate'] = function(value, item) {
						                   return value != c_any_txt; 
									   }					
					if (param['choice'].length > 0)
					    item['items'] = [{'Name': c_any_txt, 'Id': 0}]
					else
						item['items'] = [{'Name': c_any_txt, 'Id': 0}, {'Name': 'НЕТ', 'Id': 1}, {'Name': 'ДА', 'Id': 2}];	
				}
				if (param['choice'].length > 0) {
					var id = 1;
					param['choice'].forEach(function(value) {
						item['items'].push({'Name': value, 'Id': id});
						id += 1;
					});
					// Реализуем замену значений фильтра, зависящего от значений другого, например, версия драйвера зависит от производителя
				    if (param['childid'] > 0) {                // Если задан идентификатор зависимого параметра
                        //item['curfilter'] = c_any_txt;
						g_filters[param['name']] = c_any_txt;
				    }					
				}
		
		        fields.push(item);
	        });
		}
	});
	return fields;
}