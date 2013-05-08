AnalyteSelect = {
	MAX_SELECTIONS : 3,
	// kind holds the two select elements
	kindEl : {
		'name' : {},
		'code' : {}
	},
	kindId : {
		'name' : '',
		'code' : ''
	},

	_changeHandler : function(kind /* String */, ev /* select2 event obect */, setSearchButtonState /* function */) {
		/* Handles the change for the analyte select of kind. This includes setting
		 * the search button state, updating the analyte selects' sensitivity and
		 * updating the sessionStorage for that element
		 */
		var otherSelect = {};
		var selectId = AnalyteSelect.kindId[kind];
		if (kind === 'code') {
			otherSelect = AnalyteSelect.kindEl.name;
		}
		else {
			otherSelect = AnalyteSelect.kindEl.code;
		}
		
		setSearchButtonState();
		Utils.setSelect2Enabled(otherSelect, ev.val.length == 0)
		for (var i = 0; i < ev.val.length; i++) {
			sessionStorage[selectId + i] = ev.val[i];
		}
		for (var j = ev.val.length; j < AnalyteSelect.MAX_SELECTIONS; j++) {
			sessionStorage[selectId + j] = '';
		}
	},
	_initMultiSelect : function (kind /* String */, categoryEl, subcategoryEl, searchUrl, results /* Function (see select2 docs)*/) {
		AnalyteSelect.kindEl[kind].select2({
			width: 'off',
			minimumInputLength: 3,
			maximumSelectionSize: AnalyteSelect.MAX_SELECTIONS,
			multiple: true,
			separator: '|',
			tokenSeparators: ['|'],
			formatSelection : function(object, container) {
				return object.id;
			},
			ajax: {
				url: searchUrl,
				data: function(term, page) {
					return {
						kind: kind,
						category : categoryEl.val(),
						subcategory : subcategoryEl.val(),
						selection: term
					}
				},
				dataType: 'json',
				quietMillis: 500,
				results: results,
			},
			initSelection : function(element, callback) {
				var data = [];
				$(element.val().split('|')).each(function() {
					data.push({id: this, text: this});
				});
				callback(data);
			}
		});		
	},
	_getValueFromSession : function (kind /* String */) {
		/* Return an array of values, retrieved from SessionStorage suitable for setting the 
		 * value of a multi select widget
		 */
		var values = [];
		for (var i = 0; i < AnalyteSelect.MAX_SELECTIONS; i++) {
			if (sessionStorage[AnalyteSelect.kindId[kind] + i]) {
				values.push(sessionStorage[AnalyteSelect.kindId[kind] + i]);
			}
			else {
				break;
			}
		}
		if (values.length === 0) {
			return '';
		}
		else {
			return values;
		}
	},
	
	
	init: function(nameId /* String */, codeId /* String */, categoryEl, subcategoryEl, searchUrl /* String */, setSearchButtonState /* function */) {
		/* Initialize the analyte multi select fields identified by nameId and codeId. searchUrl
		 * is used when dynamically retrieving matching analytes. setSearchButton function is called
		 * whenever the analyte mutli selects issue a change event.
		 */
		AnalyteSelect.kindId.name = nameId;
		AnalyteSelect.kindId.code = codeId;
		
		AnalyteSelect.kindEl.name = $('#' + nameId);
		AnalyteSelect.kindEl.code = $('#' + codeId);
		
		// Create the name select
		AnalyteSelect._initMultiSelect('name', categoryEl, subcategoryEl, searchUrl, function(data, page) {
			var r = {'results' : []}
			for (var i=0; i < data.values_list.length; i++) {
				r.results.push({
					id: data.values_list[i][0].toLowerCase(), 
					text : data.values_list[i][0] + ' (' + data.values_list[i][1] + ')'
				});
			}
			return r;
		});
		AnalyteSelect.kindEl.name.on('change', function(e) {
			AnalyteSelect._changeHandler('name', e, setSearchButtonState);
		});
		
		// Create the code select
		AnalyteSelect._initMultiSelect('code', categoryEl, subcategoryEl, searchUrl, function(data, page) {
			var r = {'results' : []}
			for (var i=0; i < data.values_list.length; i++) {
				r.results.push({
					id: data.values_list[i].toLowerCase(), 
					text : data.values_list[i]
				});
			}
			return r;
		});
		AnalyteSelect.kindEl.code.on('change', function(e) {
			AnalyteSelect._changeHandler('code', e, setSearchButtonState);
		});
		
		// Set the initial values of the selects from sessionStorage
		AnalyteSelect.kindEl.name.select2('val', AnalyteSelect._getValueFromSession('name'));
		AnalyteSelect.kindEl.code.select2('val', AnalyteSelect._getValueFromSession('code'));
		
		// Set the initial enable/disable states
		Utils.setSelect2Enabled(AnalyteSelect.kindEl.name, AnalyteSelect.kindEl.code.select2('val').length == 0);
		Utils.setSelect2Enabled(AnalyteSelect.kindEl.code, AnalyteSelect.kindEl.name.select2('val').length == 0);

	}
}