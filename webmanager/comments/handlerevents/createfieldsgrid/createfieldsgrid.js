// Обработчик создания полей грида
function createFieldsGrid() {
    var timerId = setTimeout(
        () => {
                  alert('При проверки возможности вставки элемента произошла ошибка!');
				  args.cancel = true;
              }, g_timeout * 1000)
    // -------------------------------
	// Проверка, что строка цифры
	function isNumber(str) {
		return /^-{0,1}\d+$/.test(str)
	}
	// Проверка, что строка дата
	function isDate(str) {
		var ls = str.split('.')
		if (ls.length != 3) return false
		if (!isNumber(ls[0]) || ls[0].length != 2) return false
		if (!isNumber(ls[1]) || ls[1].length != 2) return false
		if (!isNumber(ls[2]) || ls[2].length != 4) return false
		return true
	}
	// Преобразование списка значений в список для grid
	var c_any_txt = '<НЕТ>'
	function conv_list(list) {
		var ret = []
		ret.push({'Name': c_any_txt, 'Id': 0})
		for (var id in list) {
			ret.push({'Name': list[id], 'Id': id + 1})
		}
		return ret
	}
	// Запрашиваем данные для списков значений из БД
	var res = {}
    $.ajax({
        url: 'http://' + g_rhost + '/createfieldsgrid' + '?managobj=' + g_params['managobj'],
        dataType: 'json',
        async: false,
        success: function(data) {
			clearTimeout(timerId)   // Отменяем таймер
			res = data
		}
	})
//console.log(res)
    // Устанавливаем значения по умолчанию согласно данным, переданных в строке запроса
	idx_managobj = -1; idx_obj = -1; idx_system = -1
	if (g_params['managobj'] != '') {
	    idx_managobj = res['MANAGOBJS'].indexOf(g_params['managobj']) + 1
		obj = g_params['obj']
		if (obj.slice(0, 4) == 'НПС ') g_params['obj'] = obj.slice(4, obj.length)
	    idx_obj = res['objs'].indexOf(g_params['obj']) + 1
	    idx_system = res['SYSTEMS'].indexOf(g_params['system']) + 1
	    g_params['managobj'] = ''
	}
	// Имя "name" из таблицы БД "NOTICE"
    fields = [
     	{type: 'control', clearFilterButton: false},
	    {name: 'MANAGOBJ', type: 'select', title: 'РНУ', width: 50, items: conv_list(res['MANAGOBJS']), 
		   valueField: 'Name', textField: 'Name', selectedIndex: idx_managobj, editing: false,
		     validate: function(value, item) {
			     return value != c_any_txt;
		     }
		},
	    {name: 'OBJECT', type: 'select', title: 'Объект', width: 110, items: conv_list(res['objs']), 
		   valueField: 'Name', textField: 'Name', selectedIndex: idx_obj, editing: false,
		     validate: function(value, item) {
			     return value != c_any_txt;
		     }
		},
	    {name: 'SYSTEM', type: 'select', title: 'Система', width: 90, items: conv_list(res['SYSTEMS']), 
		   valueField: 'Name', textField: 'Name', selectedIndex: idx_system, editing: false,
		     validate: function(value, item) {
			     return value != c_any_txt;
		     }
		},
	    {name: 'NUM', type: 'text', title: '№', align: 'center', width: 40, filtering: false, editing: false,
		     validate: function(value, item) {
			     return isNumber(value);
		     }		
		},
	    {name: 'COMMENT', type: 'textarea', title: 'Замечание', width: 400, validate: 'required', filtering: false},
	    {name: 'SDATETIME', type: 'text', title: 'Дата замечания', align: 'center', width: 75, validate: 'required',
		     validate: function(value, item) {
			     return isDate(value);
		     }		
		},
	    {name: 'STEP', type: 'select', title: 'Этап', width: 105, items: conv_list(res['STEPS']), valueField: 'Name', textField: 'Name',
		     validate: function(value, item) {
			     return value != c_any_txt;
		     }
		},
		{name: 'LEVEL', type: 'select', title: 'Уровень', width: 50, items: conv_list(res['LEVELS']), valueField: 'Name', textField: 'Name',
		     validate: function(value, item) {
			     return value != c_any_txt;
		     }
		},
		{name: 'PERSON', type: 'select', title: 'Ответственный', width: 100, items: conv_list(res['LISTPERSON']), 
		    valueField: 'Name', textField: 'Name',
		     validate: function(value, item) {
			     return value != c_any_txt;
		     }
		},
		{name: 'STATUS', type: 'select', title: 'Устранено', width: 60, items: conv_list(res['LISTSTATUS']), valueField: 'Name', textField: 'Name',
		     validate: function(value, item) {
			     return value != c_any_txt;
		     }
		},
		{name: 'LIMITSDATETIME', type: 'text', title: 'Срок устранения', align: 'center', width: 75,
		     validate: function(value, item) {
				 if (value == '') return true;
			     return isDate(value);
		     }
		},
		{name: 'DESCRIPTION', type: 'textarea', title: 'Примечание', width: 300, filtering: false},
		{name: 'ATTRIBUTES', type: 'text', title: 'Атрибуты строки', width: 0, visible: false},
		{name: 'ISDELETED', type: 'select', title: 'Удален ные', width: 40, items: [{'Name': 'НЕТ', 'Id': 0}, {'Name': 'ДА', 'Id': 1}], 
		   valueField: 'Id', textField: 'Name'
		},
    ]
	return fields
}