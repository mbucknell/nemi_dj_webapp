CustomHeaderDialog = {
	dialogEl : {},
	tableEl : {},
	initialize : function(divEl, resultsTableEl) {
		
		CustomHeaderDialog.dialogEl = divEl;
		CustomHeaderDialog.tableEl = resultsTableEl;
		
		// Build the list of checkboxes by iterating over the list of columns.
		// Those that are visible should be checked.
		var checkboxHtml = '';
		
		resultsTableEl.find($('thead th')).not('.col-always-visible').each(function() {
			var colName = $(this).find('.header-label').html();
			var colIndex = $(this).index();
			var colId = 'col-' + colIndex;
			checkboxHtml += '<li><input type="checkbox" id="' + colId + '" value="' + colIndex + '"';
			if ($(this).is(':visible')) {
				checkboxHtml += ' checked="checked"';
			}
			checkboxHtml += ' /><label for="'+ colId + '">' + colName + '</label></li>';
		});
		CustomHeaderDialog.dialogEl.find('ul').append(checkboxHtml);
		
		CustomHeaderDialog.dialogEl.dialog( {autoOpen: false} );
	},
	show : function() {
		CustomHeaderDialog.dialogEl.dialog('option', {
            'modal':  true,
            'title': 'Customize Header',
            'width': 250,
            'height' : 450,
            'buttons' : [{
                text: 'Apply',
                click: function(){
                	$(this).dialog('close');
                	
                	$(this).find('input:checkbox').each(function() {
                		var colIndex = parseInt($(this).val()) + 1;
                		var colEls = CustomHeaderDialog.tableEl.find('tr :nth-child(' + colIndex + ')');
                		if ($(this).is(':checked')) {
                			colEls.show();
                		}
                		else {
                			colEls.hide();
                		}
                	});
                	
                	CustomHeaderDialog.tableEl.trigger("update").trigger("appendCache");
                }
            }]
	    });
	    CustomHeaderDialog.dialogEl.dialog('open');
		
	}
		
};