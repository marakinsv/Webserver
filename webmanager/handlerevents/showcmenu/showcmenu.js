// Обработчик всплывания контекстного меню
function viewdatatable() {
	window.open('/datatable' + '?sysid=' + g_sysid + '&path=' + g_fullpath);
}

function showcmenu(node) {
	if (g_downloading) return [];                 // Идет загрузка файла
    var items =
	{
		'item1': {'label': 'Информация', 'action': viewdatatable, 'icon': false, "separator_after"   : true},
	    'item3': {'label': 'Создать папку', 'action': createnode, 'icon': false},
		'item4': {'label': 'Переименовать папку', 'action': renamenode, 'icon': false},
		'item5': {'label': 'Удалить папку', 'action': deletenode, 'icon': false},
		'item6': {'label': 'Создать структуру папок', 'action': createstruct, 'icon': false},
	}
	return items;
}