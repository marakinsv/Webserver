// Очистить списки файлов (папок)
function clear_filelist() {
	var count_tabs = $("div#tabs ul li").length;
	for (var num = 1; num <= count_tabs; num++);
		$('#list' + num).empty();                 // Очищаем список файлов
}
// Добавление новой вкладки 
function add_tab(numtab, folder_name) {
	$('div#tabs ul').append(
		"<li onclick=changetab(" + numtab + ")><a id=tabref" + numtab + " href=#tab" + numtab + ">" + folder_name + "</a></li>"
	);
    $("div#tabs").append("<div id=tab" + numtab + "><ul id=list" + numtab + "></ul></div>");	
}
// Удаление всех существующих вкладок
function delete_tabs() {
	for (var numtab = 1; numtab <= $("div#tabs ul li").length; numtab++)
		$("div#tab" + numtab).remove();	
	$('div#tabs ul').empty();
	$("div#tabs").tabs("refresh");
}
// Выделить все вкладки как пустые 
function fill_tabs_empty() {
	var count_tabs = $("div#tabs ul li").length;
	for (var num = 1; num <= count_tabs; num++)
		$("#tabref" + num).addClass("tabempty");  // Отображаем вкладки как пустые
}
// Установить 1-ю вкладку и загрузить файлы в список
function set_first_tab() {
	$('#tabs').tabs('option', 'active', 0);       // Переходим на 1-ю вкладку
	changetab(1);
}
// Заполнить список файлов (папок)
function filllist(numtab, data, folder, viewpath) {
	var itemIndex = 0;
	var req = '?path=' + g_fullpath + '&amp;selfolder=' + g_selfolder.trim() + '&amp;viewpath=' + viewpath;
	data.forEach(function(fname) {
		var displayname = fname.replace(new RegExp(' ','g'), '&nbsp;');  // Заменяем все пробелы
		if (isFile(fname)) {                     // Это файл
		    request = 'uploadfile' + req + '&amp;upfilename=' + fname + '&amp;isfile=1';
			request = request.replace(new RegExp(' ','g'), '&nbsp;');  // Заменяем все пробелы
		    $('#list' + numtab).append("<li><a " + 
			                                    "href=" + request + ' download=' + displayname + ">" + 
												"<img src=/images/upload.png>&nbsp;&nbsp;" +
										   "</a>"+ fname +"</li>");
	    }
		else {                                    // Это папка
            request = 'uploadfile' + req + '&amp;upfoldername=' + fname + '&amp;isfile=0';	
			request = request.replace(new RegExp(' ','g'), '&nbsp;');  // Заменяем все пробелы
		    $('#list' + numtab).append("<li id='item"+ itemIndex +"'onclick='gotoInside("+ numtab + ',' + itemIndex +")'><a " + 
			                                    "href=" + request + ' download=' + displayname + '.zip' + ">" + 
												"<img src=/images/upload.png>&nbsp;&nbsp;" +
										   "</a>"+ fname +"</li>");
		}		
        $('li#item' + itemIndex).mousemove(function (evt) {
			g_engoinside = true;
			if (evt.originalEvent.clientX > 500)            // Чтоб не перехолдить в папку при нажатии на иконку загрузки
				$(this).css('color', 'blue');
			else {
				g_engoinside = false;
				$(this).css('color', 'black');
			}
        })
        $('li#item' + itemIndex).mouseleave(function (evt) {
            $(this).css('color', 'black');
        })
        itemIndex += 1;		
	})
}
// Проверка, что строка цифры
function isNumber(str) {
	return /^-{0,1}\d+$/.test(str)
}
// Это имя файла
function isFile(fname) {
	var flname = fname;
	if (fname.indexOf('/') != -1) flname = fname.split('/').pop();
	if (fname.indexOf('\\') != -1) flname = fname.split('\\').pop();
	if (flname.indexOf('.') == -1) return false;
	var ext = flname.split('.').pop();  // Расширение файла
	if (isNumber(ext)) return false;
	if (ext.length > 8) return false;
	return true;
}
// Получить значение куки
function readCookie(name) {
	var name_cook = name+"=";
	var spl = document.cookie.split(";");
	for(var i=0; i<spl.length; i++) {
		var c = spl[i];		
		while(c.charAt(0) == " ") c = c.substring(1, c.length);
		if(c.indexOf(name_cook) == 0) {	
			return c.substring(name_cook.length, c.length);		
		}
		
	}
	return null;
}