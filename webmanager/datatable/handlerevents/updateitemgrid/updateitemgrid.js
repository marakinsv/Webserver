// Обработчик обновления элемента grid
function updateItemGrid(dataItem) {
	// Кодируем названия, чтобы можно было такие МНС+ПНС
	for (key in dataItem) dataItem[key] = encodeURIComponent(dataItem[key]);
	
	dataItem['ATTRIBUTES'] = JSON.stringify(dataItem['ATTRIBUTES'])
	// Изменяем список атрибутов
	//dataItem['ATTRIBUTES'] = JSON.stringify([[{'fc': 0, 'bc': 0}]])
    // -------------------------------
    $.getJSON('http://' + g_rhost + '/updateitemgrid_' + '?dataitem=' + JSON.stringify(dataItem),
        function(data) {
			//console.log(data)	
		    if (data == null) return 0
			if (typeof(data) != 'object') {
				console.log(data)
				alert('Сервер вернул неизвестное значение. Операция не выполнена')
				return 1			
			}
		}
	)
}