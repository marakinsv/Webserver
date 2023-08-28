// Обработчик загрузки данных в grid
function loadDataGrid(filter) {
    var timerId = setTimeout(
        () => {
                  alert('При загрузке данных произошла ошибка!');
				  args.cancel = true;
              }, g_timeout * 1000)
    // -------------------------------
	var ret = []
    $.ajax({
        url: 'http://' + g_rhost + '/loaddatagrid?filter=' + JSON.stringify(filter),
        dataType: 'json',
        async: false,
        success: function(data) {
			clearTimeout(timerId)   // Отменяем таймер
			ret = data
		}
	})
	refreshCSSGridColors(ret)   // Обновляем таблицу стилей цветов grid. Обработка события в "comments/handlerevents/"
	return ret
}