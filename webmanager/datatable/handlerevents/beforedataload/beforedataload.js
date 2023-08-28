// Обработчик предзагрузки данных в grid
function beforeDataLoad(args) {
return;
	//var grid = $("#jsGrid").data("JSGrid");
	Object.keys(args['filter']).forEach(function(cname) {
		// Реализуем замену значений фильтра, зависящего от значений другого, например, версия драйвера зависит от производителя
		var childid = $('#grid').jsGrid('fieldOption', cname, 'childid');
		if (childid > 0) {   // Если задан идентификатор зависимого параметра
		    if (g_filters[cname] != args['filter'][cname]) {
alert(cname);
		        g_filters[cname] = args['filter'][cname];           // Сохраняем значение фильтра
				var refid = $('#grid').jsGrid('fieldOption', cname, 'pid');
	            $.ajax({
                    url: 'http://' + g_rhost + '/beforedataload_' + '?filter=' + args['filter'][cname] + '&refid=' + refid,
                    dataType: 'json',
                    async: true,
                    success: function(args) {
					    var items = [{'Name': '<НЕ ЗАДАН>', 'Id': 0}];
					    var id = 1;
				        args.forEach(function(value) {
						    items.push({'Name': value, 'Id': id});
						    id += 1;
					    });

			
                        $('#grid').jsGrid('fieldOption', 'PARAM' + childid, 'items', items);  // Устанавливаем значения фильтра
            						 
			    
			        }
				});
			}
		}
	});	
var filter = $("#grid").jsGrid("getFilter");
console.log(filter);
	return true;
}