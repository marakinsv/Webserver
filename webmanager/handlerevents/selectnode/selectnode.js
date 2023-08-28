// Обработчик события (выделение узла (папки))
function selectnode(evt, data) {
	if (g_downloading) return;                    // Идет загрузка файла
	g_instance = data.instance;
	g_selnode = data.node;
	$('.btnshowframe').show();                    // Показываем конпку добавить
	$('.btndownload').hide();                     // Скрываем кнопку загрузить
	$('div#tabs').hide();                         // Скрываем вкладки
	delete_tabs();                                // Удаляем предыдущие вкладки
	$('#frameupload').hide();                     // Скрываем фрейм загрузки данных
	
	var path = String(data.instance.get_path(g_selnode));
	g_fullpath = encodeURIComponent(path);        // Полный путь из корневой папки к выделенной
    $.getJSON('http://' + g_rhost + '/selectnode' + '?path=' + g_fullpath,
        function(data) {
			//console.log(data)
			if (data == 'notfound') {             // Директория не найдена, кто-то удалил эту папку пока браузер был открыт
			    alert('Выделяемая папка не найдена. Попробуйте обновить дерево!');
				return;
			}
			if (data == 'unknown') {
			    //alert('Произошла ошибка получения содержимого папки. Попробуйте обновить дерево!');
				// В папке не структура папок
				return;				
			}
			if (data == '') return;
			if (!(data instanceof Array)) {
				console.log(data);
				alert('Сервер вернул неизвестное значение. Попробуйте обновить дерево!');
				return;		
			}			
			numtab = 1;
			data.forEach(function(item) {
				var folder = item[0];
				g_folders.push(folder);                                    // Добавляем имя папки в список для использования в ф-и "change_tab"	
				var folder_name = folder;
				var pos = folder.indexOf(".");
				if (pos != -1)
				    folder_name = folder.substring(pos+1, folder.length);  // Выделяем из папки имя 01.Backup
				add_tab(numtab, folder_name);                              // Создаем вкладки
				var empty = item[1] == false;                              // Признак пустой папки
				if (empty && folder_name.toUpperCase() != 'ЗАМЕЧАНИЯ') 
			        $("#tabref" + numtab).addClass("tabempty");            // Выделяем вкладку, соответствующую пустой папке
				else $("#tabref" + numtab).removeClass("tabempty");	
				numtab += 1;                				
			})
			$('div#tabs').tabs('refresh');
			$('#tabs').show();                       // Отображаем вкладки
			set_first_tab();                         // Устанавливаем 1-ю вкладку и загружам файлы в список
			
		}
    )
}