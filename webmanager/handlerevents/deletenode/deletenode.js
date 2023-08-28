// Обработчик события (удаление узла (папки))	
function deletenode() {
	var ls = g_fullpath.split(',');
    res = confirm('Действительно удалить папку "' + decodeURIComponent(ls[ls.length-1]) + '"?');
	if (res == false) return;
    $.getJSON('http://' + g_rhost + '/deletenode' + '?path=' + g_fullpath,
        function(data) {
			if (data == 'notexists') {       // Папка не существует, кто-то удалил эту папку пока браузер был открыт
			    alert('Удаляемая папка не найдена. Попробуйте обновить дерево!');
				return;    
			}
			if (data == 'notempty') {       // Папка не пустая
			    alert('Удаляемая папка содержит файлы или не пустую папку. Не возможно удалить данную папку!');
				return;    
			}
			if (data == 'notdeleted') {     // Ошибка при удалении папки
			    alert('Ошибка при удалении папки');
				return;   
			}
			if (data == 'success') {
				$('#tabs').hide();                   // Скрываем вкладки
                $('#treeview').jstree('refresh');    // Обновляем дерево
				return;
			}
			console.log(data);
			alert('Сервер вернул неизвестное значение. Операция не выполнена');
		}
    )
}