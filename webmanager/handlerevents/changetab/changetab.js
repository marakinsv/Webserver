// Обработчик событий (переход на другую вкладку)
function changetab(numtab) {
	g_numtab = numtab;                // Используется только в showinputform
	g_viewpath = '';                  // Используется только в gotoInside
	$('.btnshowframe').show();        // Показываем конпку добавить
	$('.btndownload').hide();         // Скрываем кнопку загрузить
	$('#inputframe').hide();          // Скрываем фрейм ввода данных о загружаемом файле
	$('#list' + numtab).show();       // Отображаем список файлов (папок)
	$('#list' + numtab).empty();      // Очищаем список
	$('#operdescr').hide();           // Скрываем подпись выполняемой операции
	if (g_folders.length == 0) {
		alert('change_tab: Не найден список папок, соответствующих вкладкам');
	    return;	
	};
	g_selfolder = g_folders[numtab-1];
	if (g_selfolder == '08.Замечания') {
	    window.open('/comments' + '?path=' + g_fullpath);
		return;
	}
    $.getJSON('http://' + g_rhost + '/getfiles' + '?path=' + g_fullpath + '&selfolder=' + g_selfolder,
        function(data) {
			if (data == 'notfound') {       // Директория не найдена, кто-то удалил ее пока браузер был открыт
			    alert('Выделенная в дереве папка не найдена. Попробуйте обновить дерево!');
				$('#tabs').hide();           // Скрываем вкладки
				return;
			}
			if (data == 'notexists') {      // Папка не найдена, кто-то удалил эту папку пока браузер был открыт
			    alert('Папка, соответствующая вкладке, не найдена. Попробуйте снова выделить папку в дереве!');
				$('#tabs').hide();           // Скрываем вкладки
				return;
			}
			if (!(data instanceof Array)) {
				console.log(data);
				alert('Сервер вернул неизвестное значение. Операция не выполнена');
				return;			
			}
			filllist(numtab, data, g_selfolder, g_viewpath);  // Добавляем имена файлов и папок в список
		}
    )
}