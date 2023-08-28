// Обработчик обновления элемента grid
function updateItemGrid(dataItem) {
	var timerId = setTimeout(
    () => {
              alert('При обновлении элемента произошла ошибка!');
	    	  args.cancel = true;
          }, g_timeout * 1000)
	dataItem['ATTRIBUTES'] = JSON.stringify(dataItem['ATTRIBUTES'])
	// Изменяем список атрибутов
	//dataItem['ATTRIBUTES'] = JSON.stringify([[{'fc': 0, 'bc': 0}]])
    // -------------------------------
    $.getJSON('http://' + g_rhost + '/updateitemgrid' + '?dataitem=' + JSON.stringify(dataItem),
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