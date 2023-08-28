// Обработчик событий (переход во внутрь выбранной папки)
function gotoInside(numtab, itemIndex) {
	if (!g_engoinside) return;
	var viewfolder = $('#list' + numtab + ' li#item' + itemIndex).text()  // Имя выбранной папки или файла
	if (g_viewpath == '') g_viewpath = viewfolder.trim();
	else g_viewpath = g_viewpath + '/' + viewfolder.trim();
    $.getJSON('http://' + g_rhost + '/gotoinside' + '?path=' + g_fullpath + '&selfolder=' + g_selfolder + '&viewpath=' + g_viewpath,
        function(data) {
			if (data == 'notfound') {        // Директория не найдена, кто-то удалил ее пока браузер был открыт
			    alert('Папка, соотв-я выделенному узлу дерева, не найдена. Попробуйте обновить дерево!');
				$('#tabs').hide();           // Скрываем вкладки
				return;
			}
			if (data == 'notexists') {        // Директория не найдена, кто-то удалил ее пока браузер был открыт
			    alert('Папка, соотв-я вкладке, не найдена. Попробуйте снова выделить папку в дереве!');
				$('#tabs').hide();            // Скрываем вкладки
				return;
			}
			if (data == 'notexists_') {        // Директория не найдена, кто-то удалил ее пока браузер был открыт
			    alert('Просматриваемая папка не найдена. Попробуйте снова выделить текущую вкладку!');
				$('#tabs').hide();             // Скрываем вкладки
				return;
			}
			if (!(data instanceof Array)) {
				console.log(data);
				alert('Сервер вернул неизвестное значение. Попробуйте обновить дерево!');
				return;		
			}
	        $('#list' + numtab).empty();        // Очищаем список
			filllist(numtab, data, viewfolder, g_viewpath); // Добавляем имена файлов и папок в список
		}
    )
}