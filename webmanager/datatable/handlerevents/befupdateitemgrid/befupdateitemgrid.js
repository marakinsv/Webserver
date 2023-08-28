// Обработчик события до изменения элемента grid
function befUpdateItemGrid(args) {
// args.previousItem - предыдущие данные
	// Кодируем названия, чтобы можно было такие МНС+ПНС
	previousItem = {};
	for (key in args.previousItem) previousItem[key] = encodeURIComponent(args.previousItem[key]);
    $.ajax({
        url: 'http://' + g_rhost + '/befupdateitemgrid_' + '?previousitem=' + JSON.stringify(previousItem),
        dataType: 'json',
        async: false,
        success: function(data) {
			msg = data['msg']
		}
	})
	if (msg == 'OK') return       // Можно изменить элемент
    args.cancel = true
    alert(msg)
}