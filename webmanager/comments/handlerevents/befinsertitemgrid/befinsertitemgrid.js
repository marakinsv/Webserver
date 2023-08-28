// Обработчик события до вставки элемента в grid
function befInsertItemGrid(args) { return
    var timerId = setTimeout(
        () => {
                  alert('При проверки возможности вставки элемента произошла ошибка!');
				  args.cancel = true;
              }, g_timeout * 1000)
    // -------------------------------
	var msg = ''
    $.ajax({
        url: 'http://' + g_rhost + '/befinsertitemgrid' + '?dataitem=' + JSON.stringify(args.item),
        dataType: 'json',
        async: false,
        success: function(data) {
			clearTimeout(timerId)   // Отменяем таймер
			msg = data['msg']
		}
	})
	if (msg == 'OK') return  // Можно добавлять
    args.cancel = true
    alert(msg)
}