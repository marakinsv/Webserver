// Обработчик удаления элемента из grid
function deleteItemGrid(dataItem) {
    var timerId = setTimeout(
        () => {
                  alert('При удалении элемента произошла ошибка!');
				  args.cancel = true;
              }, g_timeout * 1000)
    // -------------------------------
    $.getJSON('http://' + g_rhost + '/deleteitemgrid' + '?dataitem=' + JSON.stringify(dataItem),
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