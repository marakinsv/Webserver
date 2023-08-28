// Обработчик обновления таблицы стилей цветов grid
function refreshCSSGridColors(data) {
	return
	if (data.forEach == undefined) return 
    var stylesheet = document.styleSheets[document.styleSheets.length-1]  // Эта таблица д.б. объявлена последней
	var ruleIndex = stylesheet.cssRules.length
	var itemIndex = 0;	
	data.forEach(function(item) {
	    var col = 2  // 1-й столбец - это контролы, если они заданы вначале
		item['ATTRIBUTES'].forEach(function(item) {
			var rule = ''
			if (item['fc'].length == 3) {
				rule = 'color: rgb(' +  item['fc'][0] + ',' + item['fc'][1] + ',' + item['fc'][2] + ');'
			}
			if (item['bc'].length == 3) {
				rule = rule + 'background-color: rgb(' +  item['bc'][0] + ',' + item['bc'][1] + ',' + item['bc'][2] + ');'
			}
			if (rule != '') rule = rule + '}'
			if (rule != '') {
			    stylesheet.insertRule('.row-custom-class-item' + itemIndex + ' td:nth-child(' + col + ') {' + rule, rule, ruleIndex)
                ruleIndex += 1			
			}
			col += 1
		})
		itemIndex += 1
	})
}