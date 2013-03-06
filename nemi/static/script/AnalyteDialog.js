// Provides methods and types which create and manage the Find Analyte by Name/Code dialog.
// The initialize method must be called before accessing any of the other properties.

AnalyteDialog = {
	dialogEl: {},
	analyteIdKind: '',
	parentTextEl : {},
	initialize : function(divEl /* jquery element */, dataUrl /* String */) {
		// Initialize divEl to use the jquery ui-dialog and to set up the various
		// dialog button click events. The parameter dataUrl should be the ajax url
		// to be used to retrieve the analyte name/code information which will be
		// returned as a json object.
		
		AnalyteDialog.dialogEl = divEl;
		
		// Set up click handlers for the dialog's buttons
		$("#find-analyte-button").click(function() {
			$.ajax({
				url: dataUrl,
				data: {
					kind: AnalyteDialog.analyteIdKind,
					selection: $('#find-analyte-text').val()
				},
				success: function(resp) {
					var valuesEl = $('#analyte-search-list');
					if (resp.values_list.length > 0) {
						var valueOptions = '';

						for (var i=0; i < resp.values_list.length; i++) {
							valueOptions += '<option value="' + resp.values_list[i].toLowerCase() + '">' + resp.values_list[i] + '</option>';
						}
						
						valuesEl.html(valueOptions);
						valuesEl.show();
						$('#no-analyte-values').hide();
					}
					else {
						valuesEl.hide();
						$('#no-analyte-values').show();
					}
				}
			});
			return false;
		});
		
		$('#add-to-select').click(function() {
			var searchList = $('#analyte-search-list');
			var selectList = $('#analyte-select-list');
			searchList.find('option:selected').each(function() {
				var value = $(this).val();
				
				// Check to see if this option is already in select list.
				if (selectList.find('option[value="'+ value + '"]').length == 0){
					if (selectList.find('option').length == 3) {
						// Can't add anymore
						alert("You've reached the maximum number of analytes for searching");
						return false;
					}
					
					selectList.append('<option value="' + value + '">' + $(this).html() + '</option>');
				}
			});
		});
		
		$('#remove-from-select').click(function() {
			$('#analyte-select-list option:selected').remove();
		});
		
		AnalyteDialog.dialogEl.dialog( {
			'autoOpen': false,
			'modal': true,
			'width': 670,
			'height' : 500,
			'buttons' : [{
				text: 'Enter in search',
				click: function() {
					$(this).dialog('close');
					
					var value = '';
					$('#analyte-select-list option').each(function(){
						if (value != '') {
							value += '\n';
						}
						value += $(this).html();
					});
					AnalyteDialog.parentTextEl.val(value);
				}
			}]
		});
		
		return false;
	},
	show: function(idKind /* string for analyte id kind */, parent /*jquery element */) {
		// Show the find analyte dialog using idKind (should be 'code' or 'name') to determine
		// how to do the search. The parameter, parent, specifies the jquery element which has the
		// current search values and where the selected values should go when the dialog's Enter in search
		// button is clicked.
		
		AnalyteDialog.analyteIdKind = idKind;
		AnalyteDialog.parentTextEl = parent;
		
		var title = '';
		if (idKind == 'code') {
			$('#analyte-id-kind').html('analyte code: ');
			title = 'Find an analyte code';
		}
		else {
			$('#analyte-id-kind').html('analyte name: ');
			title = 'Find an analyte name:';
		}
		
		// Clear out all fields and set current selections
		$('#find-analyte-text').val('');
		$('#analyte-search-list').html('');
		var selections = parent.val().split('\n');
		var selectionOptions = '';
		for (var i = 0; i < selections.length; i++) {
			if (selections[i] != '') {
				selectionOptions += '<option value="' + selections[i].toLowerCase() + '">' + selections[i] + '</option>';
			}
		}
		$('#analyte-select-list').html(selectionOptions);
		
		AnalyteDialog.dialogEl.dialog('option', {
			'title': title
		});
		AnalyteDialog.dialogEl.dialog('open');
		
		return false;
	}
		
};