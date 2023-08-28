// Обработчик событий (загрузить файл на сервер)
function downloadfile() {
    function ab2str(buf) {
        return String.fromCharCode.apply(null, new Uint8Array(buf));
    }
	g_downloading = true;
	$('#tabs').tabs('disable');                              // Запрещаем переход по вкладкам
	
    let ws = new WebSocket('ws://' + g_rhost + '/ws');        // Создаем web-socket
    ws.binaryType = 'arraybuffer';
    // Открытие сокета
    ws.onopen = function() {
		console.log('Сокет открыт');
		$('#operdescr').show();                               // Показываем подпись выполняемой операции
		$('#operdescr').text('Подготовка файла к отправке');
        var reader = new FileReader();		
        reader.onload = function(evt) {
			$('#operdescr').text('Передача файла на сервер');
            let arrayBuffer = evt.target.result;               // Бинарные данные загружаемого файла
    	    var chunk_size = 2**16;                            // Размер блока передаваемых данных			
    	    // Размер файла позволяет отправить его одним блоком
	   	    if (arrayBuffer.byteLength <= chunk_size)
	    	    ws.send(arrayBuffer);
	        else {
		        $("div#progressbar").progressbar("option", "max", parseInt(arrayBuffer.byteLength / chunk_size));	
		        var start_pos = 0; var end_pos = 0; var cnt = 0;
	            // Отправляем файл поблочно			
	            while (start_pos < arrayBuffer.byteLength) {
		            end_pos = start_pos + chunk_size;
		            if (end_pos > arrayBuffer.byteLength) end_pos = arrayBuffer.byteLength;
    			    if (end_pos == (arrayBuffer.byteLength - 1)) end_pos = arrayBuffer.byteLength; // Исключаем возможность передачи 1-го байта 
	   		        chunk = arrayBuffer.slice(start_pos, end_pos);
	    	        //console.log(start_pos, end_pos)
		            ws.send(chunk);
		            start_pos = end_pos;
	            }
	        }
            var array = new Uint8Array(1);
            array[0] = 0x04;		
	        ws.send(array);                      // Сообщаем серверу, что загрузка завершена							
        }
        reader.readAsArrayBuffer(g_sendfile);
    }	
    // Получены данные от сокета-сервера
    ws.onmessage = function(evt) {
	    msg = ab2str(evt.data);                                // Преобразовываем бинарные данные в строку
		if (msg.indexOf(':') != -1) {
			ls = msg.split(':');
			if (ls[0] == 'startunpack') {
				$('#operdescr').text('Идет распаковка файла');
				$("div#progressbar").progressbar("option", "max", parseInt(ls[1]));
			}
			if (ls[0] == 'procunpack') {
				var value = $("div#progressbar").progressbar("value");
				$("div#progressbar").progressbar ("value", value + parseInt(ls[1]));
			}
			return;
		}
        if (msg == 'prepunpack') {
			$("div#progressbar").progressbar ("value", 0);
			$('#operdescr').text('Удаление существующей папки');
	    }
        if (msg == 'dataunknown') {
		    alert('Данные загружаемого файла не опредлены!');
	    }
        if (msg == 'error') {
		    alert('При загрузке файла произошла ошибка!');
	    }
        if (msg == 'unpackerror') {
		    alert('Произошла ошибка при распаковке загруженного файла!');
        }
        if (msg == 'logerror') {
		    alert('Произошла ошибка записи лога загрузки!');
        }
        if (msg == 'updatedateerror') {
		    alert('Произошла ошибка при обновлении даты загруженного файла!');
        }
        if (msg == 'updatedateerror_') {
		    alert('Произошла ошибка при обновлении даты загруженного файла в Excel файле.\nОбязательно обновите дату вручную!');
        }
        // Блок данных успешно записан
	   	if (msg == 'proc') {
	    	var value = $("div#progressbar").progressbar("value");
		    $("div#progressbar").progressbar ("value", value + 10);
        }
        if (msg == 'success') {
			g_downloading = false;
	        $('.btnshowframe').show();                       // Показываем кнопку добавить
	        $('.btndownload').hide();                        // Скрываем кнопку загрузить
		    $('#tabs').tabs('enable');                       // Разрешаем переход по вкладкам
		    $('#list' + g_numtab).show();                    // Отображаем список файлов (папок)
		    $("#tabref" + g_numtab).removeClass("tabempty"); // Отображаем вкладку как имеющую файлы
		    changetab(g_numtab);                             // Обновляем список файлов
	    }
    }
	// Закрытие сокета
    ws.onclose = function() {
        console.log('Сокет закрыт');
    }
	// Ошибка сокета
    ws.onerror = function(e) {
		g_downloading = false;
	    $('.btnshowframe').show();                       // Показываем кнопку добавить
	    $('.btndownload').hide();                        // Скрываем кнопку загрузить
		$('#tabs').tabs('enable');                       // Разрешаем переход по вкладкам
		$('#operdescr').hide();                          // Скрываем подпись выполняемой операции
        alert('Ошибка канала передачи файла.\nПерезагрузите дерево и попробуйте снова!');
    }	
}
