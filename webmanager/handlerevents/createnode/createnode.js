// Обработчик события (создание узла (папки))
function createnode() {
	var ls = decodeURIComponent(g_fullpath).split(',');
    if (ls.length > 4) {
		alert('На этом уровне невозможно создать папку!');
	    return;
	}
	var pr = false;
    if (g_sysid == 1)  // ЛТМ
		if (ls.length >= 4) {foldername = prompt('Введите номер КП', 'КП№xx'); pr = true;}
	if (!pr) foldername = prompt('Введите название создаваемой папки', 'NewFolder');
	
	if (foldername == null) return;
	if (foldername.trim() == '') return;    // Если пробелы, выходим
    $.getJSON('http://' + g_rhost + '/createnode' + '?path=' + g_fullpath + '&foldername=' + encodeURIComponent(foldername),
        function(data) {
			if (data == 'notfound') {       // Директория не найдена, кто-то удалил эту папку пока браузер был открыт
			    alert('Директория, в которой создается папка не найдена. Попробуйте обновить дерево!');
				return;
			}
			if (data == 'exists') {         // Папка уже существует (может другой клиент создал папку)
			    alert('Папка с таким именем уже существует!');
				return;    
			}
			if (data == 'notcreated') {      // Ошибка при создании папки
			    alert('Не удалось создать папку. Возможно нет прав на создание папки!');
				return;    
			}
			if (data == 'success') {         // Папка успешно создана на сервере
				$('#treeview').jstree('refresh');  // Обновляем дерево
				return;
			}
			console.log(data);
			alert('Сервер вернул неизвестное значение. Операция не выполнена');
		}
    )
}