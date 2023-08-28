// Обработчик загрузки данных в grid
function loadDataGrid(filter) {
	// Добавляем фильтр скрытых полей
	for (key in g_filter) filter[key] = g_filter[key];
	// Кодируем названия, чтобы можно было такие МНС+ПНС
	for (key in filter) filter[key] = encodeURIComponent(filter[key]);
		
	var ret = [];
    $.ajax({
        url: 'http://' + g_rhost + '/loaddatagrid_?filter=' + JSON.stringify(filter),
        dataType: 'json',
        async: false,
        success: function(data) {
			ret = data
		}
	})
	//refreshCSSGridColors(ret)   // Обновляем таблицу стилей цветов grid. Обработка события в "datatable/handlerevents/"
	// Видимость столбцов, соотв. пути
	return ret;
}