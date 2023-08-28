// Обработчик события (переименование узла (папки))
function renamenode() {
	// При переименовании нужно переименовать объек или систему в БД замечаний (CHOSE и NOTICE)
	var ls = decodeURIComponent(g_fullpath).split(',');
    if (ls.length <= 2) {
		alert('Папку этого уровня переименовать нельзя!');
	    return;
	}
    var newname = prompt('Введите новое название папки', ls[ls.length-1])
	if (newname == null) return;
	if (newname.trim() == '') return;      // Если пробелы, выходим
    $.getJSON('http://' + g_rhost + '/renamenode' + '?path=' + g_fullpath + '&newname=' + encodeURIComponent(newname),
        function(data) {
			if (data == 'notexists') {      // Директория не найдена, кто-то удалил эту папку пока браузер был открыт
			    alert('Переименуемая папка не найдена. Попробуйте обновить дерево!');
				return;
			}
			if (data == 'exists') {         // Папка с таким именем уже существует
			    alert('Папка с таким именем уже существует!');
				return;   
			}
			if (data == 'notrenamed') {          // Ошибка при переименовании папки
			    alert('Не удалось переименовать папку. Возможно нет прав!');
				return;   
			}
   	        if (data == 'success') {
				$('#treeview').jstree('refresh');    // Обновляем дерево
				return;
			}
			console.log(data);
			alert('Сервер вернул неизвестное значение. Операция не выполнена');
		}
    )
}