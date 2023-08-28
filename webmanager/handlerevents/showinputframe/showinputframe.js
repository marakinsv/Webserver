// Обработчик события (показать фрейм ввода данных о загружаемом файле)
function showinputframe(evt, data) {
	$('.btnshowframe').hide();          // Скрываем кнопку добавить
	$('.btndownload').show();           // Показываем кнопку загрузить
	g_sendfile = null;
	$("input#date").datepicker("setDate", new Date());       // Устанавливаем текущую дату
	$('#sendfile').prop('value', null);
	$('#combo_users').empty();                      // Очищаем список пользователей
	$('#reasons').prop('value', '');                // Очищаем список причин
	$('#descr').prop('value', '');                  // Очищаем описание
	$("div#progressbar").progressbar ("value", 0);  // Устанавливаем на 0 прогресс бар
	$("#enunzip").prop('checked', false);           // Сбрасываем checkbox
	if (g_sysid == 0)                               // МПСА
		if (g_numtab != 1 && g_numtab != 9)
	       $("#enunzip").prop('checked', true);     // Устанавливаем checkbox
	if (g_sysid == 1)                               // ЛТМ
		if (g_numtab == 4)
			$("#enunzip").prop('checked', true);    // Устанавливаем checkbox
	$('#list' + g_numtab).hide();                   // Скрываем список файлов (папок)
	$('#inputframe').show();                        // Показываем фрейм добавления данных
    $.getJSON('http://' + g_rhost + '/getdatainputframe',
        function(data) {
			if (!(data instanceof Object)) {
				console.log(data);
				alert('Сервер вернул неизвестное значение!');
				return;		
			}
			var users = data['users'];
			var reasons = data['reasons'];
			// Добавляем пользователей и причины в списки
			for (idx in users) $('#combo_users').append('<option value=' + idx + '>' + users[idx] + '</option>');
			$('#combo_users option:contains("' + readCookie('user') + '")').prop('selected', true);  // Устанавливаем пользователя из cookie
            $('#reasons').autocomplete({
                source: data['reasons']
            })
		}
    )
}