// Обработчик событий (сохранение лога действия плюс необходимые проверки перед загрузкой)
function befdownloadfile(reload = false, rdata= null) {
	if (g_downloading) return;                    // Идет загрузка файла
    function padStr(i) {
        return (i < 10) ? "0" + i : "" + i;
    }
	if (!reload) {
	    // Проверка корректности введенных данных ========
	    if (g_sendfile == null) {
		   alert('Необходимо выбрать файл');
		   return;
	    };
	    var date = $("input#date").datepicker('getDate')   // Выбранная дата в календаре
	        if (date == null) {
		    alert('Необходимо выбрать дату');
		    return;
	    }	
        var str_date = padStr(date.getFullYear()) + '_' + padStr(1 + date.getMonth()) + '_' + padStr(date.getDate());
        var reason = $('#reasons').val();
	    if (reason == '') {
		    alert('Необходимо ввести причину');
		    return;
	    }
        var user = $("#combo_users option:selected" ).text();
		document.cookie = "user=" + user;                  // Сохраняем пользователя в cookie
		var descr = $('#descr').prop('value');
	    var unzip = $("#enunzip").is(':checked');
	    if (unzip) {
		    if (g_sendfile.name.slice(-3) != 'zip') {
		        alert('В хранилище можно распаковать только ".zip" файл');
		        return;			
		    }
			var res = confirm('Действительно распаковать файлы в хранилище?');
			if (!res) return;
	    }
	    var replace = false;
	}
	// ===============================================
	if (!reload)
	    var querydata = {'folder': g_selfolder, 'filename': g_sendfile.name, 'sdate': str_date, 'reason': reason, 
	                     'user': user, 'descr': descr, 'unzip': unzip, 'replace': replace};
    else var querydata = rdata;
	// Передаем серверу имя файла и имя папки для него
    $.getJSON('http://' + g_rhost + '/befdownloadfile' + '?path=' + g_fullpath + '&data=' + JSON.stringify(querydata),
        function(data) {
			if (data == 'notfound') {   // Директория не найдена, кто-то удалил ее пока браузер был открыт
			    alert('Выделенная в дереве папка не найдена. Попробуйте обновить дерево!');
				return;
			}
			if (data == 'notexists') {      // Папка не найдена, кто-то удалил эту папку пока браузер был открыт
			    alert('Папка для загрузки файла не найдена. Попробуйте обновить дерево!')
				return;
			}
			if (data == 'collision') {      // Попытка записать уже записываемый файл
			    alert('Данный файл уже загружается с другого хоста.\nПопробуйте загрузить файл через некоторое время!')
				return;
			}
			if (data == 'existsfolder') {   // Папка куда будут распакованы файлы существует
                var res = confirm('Папка, куда распаковываются файлы уже существует. Перезаписать?');
	            if (res == true) {
					querydata['replace'] = true;
				    befdownloadfile(true, querydata);    // Вызываем себя же
				}
				return;
			}
			if (data == 'existsfile') {     // Файл с таким именем уже существует
                var res = confirm('Файл с таким именем уже существует. Перезаписать?');
	            if (res == true) {
					querydata['replace'] = true;
				    befdownloadfile(true, querydata);    // Вызываем себя же
				}
				return;
			}
			if (data == 'success') {         // Имя файла передано серверу
			    downloadfile();              // Загрузка файла на сервер (обработчик в handlerevents/downloadfile)
			}
		}
    )			
}