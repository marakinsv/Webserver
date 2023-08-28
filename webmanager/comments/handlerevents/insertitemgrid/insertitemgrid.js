// Обработчик вставки элемента в grid
function insertItemGrid(dataItem) {
    var timerId = setTimeout(
        () => {
                  alert('При вставке элемента произошла ошибка!');
				  args.cancel = true;
              }, g_timeout * 1000)
    // -------------------------------
	// Формируем список атрибутов
	dataItem['ATTRIBUTES'] = JSON.stringify([[{'fc': 0, 'bc': 0}]])
	// --------------------------------
//console.log(dataItem)
    $.getJSON('http://' + g_rhost + '/insertitemgrid' + '?dataitem=' + JSON.stringify(dataItem),
        function(data) {
			clearTimeout(timerId)   // Отменяем таймер
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