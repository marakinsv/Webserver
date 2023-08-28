// Обработчик события до изменения элемента grid
function befUpdateItemGrid(args) {
// args.previousItem - предыдущие данные	
return;
	var msg = ''
	if (args.item['NUM'] == g_selected_num) return  // Номер замечания не меняли
    $.ajax({
        url: 'http://' + g_rhost + '/befupdateitemgrid' + '?dataitem=' + JSON.stringify(args.item),
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