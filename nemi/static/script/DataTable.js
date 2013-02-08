DataTable = {
	initialize : function(tableEls /* jquery elements */) {
		tableEls.each(function() {
			// Column headers with class nosort should be disabled. The code below collects them in 
			// an array which will be used when registering the table.
			var noSort = {};
			$(this).find("th.nosort").each(function(){
				var i = $(this).index();
				noSort[i] = { sorter: false }
			});
			
			// This sets the first sortable column to be the initial sortList.
			var lastItemIndex = $(this).find("thead th:last").index();
			var sortList = [];
			for (var i=0; i <= lastItemIndex; i++){
				if (!noSort[i]) {
					sortList = [[i, 0]]
					break;
				}
			}
		
			// Sets up the tablesorter plugin 
			$(this).tablesorter({
				theme: 'nemi',
				headers: noSort,
				sortList: sortList,
				widgets : ["zebra"],
			});
		});
	}
}