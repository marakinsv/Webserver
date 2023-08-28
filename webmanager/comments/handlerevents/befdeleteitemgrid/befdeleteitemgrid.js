// Обработчик события до удаления элемента из grid
function befDeleteItemGrid(args) {
	if (confirm('Удалить замечание для "' + 
	    args.item['MANAGOBJ'] + '. ' + args.item['OBJECT'] + '. ' + args.item['SYSTEM'] + '" под номером <' + args.item['NUM'] + '>?')) return
	args.cancel = true
}