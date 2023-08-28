// Обработчик событий (создать структуру папок в выделенной папке)
function createstruct() {
	var ls = decodeURIComponent(g_fullpath).split(',');
    if (ls.length < 4) {
		alert('На этом уровне невозможно создать структуру!');
	    return;
	}
    $.getJSON('http://' + g_rhost + '/createstruct' + '?path=' + g_fullpath,
        function(data) {
			if (data == 'notfound') {           // Директория не найдена, кто-то удалил эту папку пока браузер был открыт
			    alert('Папка-контейнер для структуры не найдена. Попробуйте обновить дерево!');
				return;
			}
			if (data == 'notempty') {           // Папка не пустая
			    alert('Папка-контейнер для структуры не пустая. Структура не будет создана!');
				return;   
			}
			if (data == 'notdbread') {           // Папка не пустая
			    alert('Не удалось получить информацию из БД. Проверьте поле "FOLDERS" в таблице "CHOSE"!');
				return;   
			}
			if (data == 'notcreated') {          // Структура не была создана
			    alert('Не удалось создать структуру. Возможно нет прав на создание папки!');
				return;  
			}
   	        if (!(data instanceof Array)) {
			    console.log(data);
			    alert('Сервер вернул неизвестное значение. Операция не выполнена!');
				return;
            }
			delete_tabs();                                // Удаляем предыдущие вкладки	
			var idx = 1;
			data.forEach(function(item) {
				add_tab(idx, item);                        // Создаем вкладки
				g_folders.push(item);
                idx += 1;				
			})
			//$('div#tabs').tabs('refresh');
	        $('#inputframe').hide();                      // Скрываем фрейм загрузки данных
			fill_tabs_empty();                            // Отображаем вкладки как пустые
			clear_filelist();                             // Очищаем списки файлов (папок)
			$('#tabs' ).tabs('option', 'active', 0);      // Переходим на 1-ю вкладку
			$('#tabs').show();                            // Отображаем вкладки		
            $('div#tabs').tabs('refresh');			
		}
    )
}