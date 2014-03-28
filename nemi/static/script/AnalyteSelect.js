AnalyteSelect = {
	init : function(analyteDivEl, options /* Object */) {
		/* initialize the analyte name and code select widgets using the options.
		 * Defined below are the valid options
		 * dynamic : Boolean, set to true if you want the search/selections for the name to be dynamic.
		 * searchUrl : Used to get the list of selections.
		 * maxSelectionSize : Number of selections allowed.
		 * setSearchButtonState : Function which sets the Search button state based on the contents 
		 *    of the analyte selects as they change. Used in the select's change handler.
		 * 
		 */
		var selectEl = {
			'name' : analyteDivEl.find('input[name="analyte_name"]'),
			'code' : analyteDivEl.find('input[name="analyte_code"]')
		};

		function changeHandler(kind /* String */, ev /* select2 event object */) {
			var otherKind = '';
			if (kind === 'code') {
				otherKind = 'name';
			}
			else {
				otherKind = 'code';
			}
			var thisId = selectEl[kind].attr('id');
			
			options.setSearchButtonState();
			if (options.maxSelectionSize === 1) {
				Utils.setSelect2Enabled(selectEl[otherKind], ev.val === '');
				sessionStorage[thisId] = ev.val;
			}
			else {
				Utils.setSelect2Enabled(selectEl[otherKind], ev.val.length === 0);
				for (var i = 0; i < ev.val.length; i++) {
					sessionStorage[thisId + i] = ev.val[i];
				}
				for (var j = ev.val.length; j < options.maxSelectionSize; j++) {
					sessionStorage[thisId + i] = '';
				}
			}
		};
		
		function getValueFromSession(kind /* String */) {
			/* Return an array of values, retrieved from SessionStorage suitable for setting the 
			 * value of a multi select widget. If it' not multi select just return the value.
			 */
			var thisId = selectEl[kind].attr('id');
			
			if (options.maxSelectionSize === 1) {
				if (sessionStorage[thisId]) {
					return sessionStorage[thisId];
				}
				else {
					return '';
				}
			}
			else {	
				var values = [];
				
				for (var i = 0; i < options.maxSelectionSize; i++) {
					if (sessionStorage[thisId + i]) {
						values.push(sessionStorage[thisId + i]);
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
			}
		};
		
		function setEnabledStateFromSession(kind /* String */) {
			var otherVal = null;
			if (kind === 'code') {
				otherVal = getValueFromSession('name');
			}
			else {
				otherVal = getValueFromSession('code');
			}
			Utils.setSelect2Enabled(selectEl[kind], otherVal === '');

		};
		
		function initDynamicSelect (kind /* String */, results /* Function (see select2 docs) */) {
			selectEl[kind].select2({
				width: 'off',
				minimumInputLength: 2,
				maximumSelectionSize : options.maxSelectionSize,
				multiple: options.maxSelectionSize > 1,
				separator: '|',
				tokenSeparators: ['|'],
				formatSelection: function(object, container) {
					return object.id;
				},
				ajax: {
					url: options.searchUrl,
					data: function(term, page) {
						return {
							kind: kind,
							category: analyteDivEl.find('input[name="category"]').val(),
							subcategory: analyteDivEl.find('input[name="subcategory"]').val(),
							selection: term
						}
					},
					dataType: 'json',
					quietMillis: 500,
					results: results
				},
				initSelection: function(element, callback) {
					if (options.maxSelectionSize === 1) {
						callback({id: element.val(), text: element.val()});
					}
					else {
						var data = [];
						$(element.val().split('|')).each(function() {
							data.push({id: this, text: this});
						});
						callback(data);
					}
				}
			});
			selectEl[kind].on('change', function(e) {
				changeHandler(kind, e, options.setSearchButtonState);
			});
			
			// Set the initial values of the selects from sessionStorage
			selectEl[kind].select2('val', getValueFromSession(kind));
			setEnabledStateFromSession(kind);
		};
		
		function initStaticSelect(kind /* String */, results /* Function (see select2 docs) */){
			$.ajax({
				url: options.searchUrl,
				data: {
					kind: kind,
					category: analyteDivEl.find('input[name="category"]').val(),
					subcategory: analyteDivEl.find('input[name="subcategory"]').val()
				},
				success : function(resp) {
					var selectData = results(resp);
					
					selectEl[kind].select2({
						width: 'off',
						data: selectData,
						maximumSelectionSize : options.maxSelectionSize,
						multiple: options.maxSelectionSize > 1,
						separator: '|',
						tokenSeparators: ['|'],
						formatSelection: function(object, container) {
							return object.id;
						},
					});
					selectEl[kind].on('change', function(e) {
						changeHandler(kind, e, options.setSearchButtonState);
					});
					
					// Set the initial values of the selects from sessionStorage
					selectEl[kind].select2('val', getValueFromSession(kind));
					setEnabledStateFromSession(kind);
				}
			});
		};
		
		function nameResults(data, page) {
			var r = {'results' : []}
			for (var i=0; i < data.values_list.length; i++) {
				r.results.push({
					id: data.values_list[i][0].toLowerCase(), 
					text : data.values_list[i][0] + ' (' + data.values_list[i][1] + ')'
				});
			}
			return r;
		};
		
		function codeResults(data, page) {
			var r = {'results' : []}
			for (var i=0; i < data.values_list.length; i++) {
				r.results.push({
					id: data.values_list[i].toLowerCase(), 
					text : data.values_list[i]
				});
			}
			return r;
		};
					
		
		// Initialize name then code which are always dynamic.
		if (options.dynamic) {
			initDynamicSelect('name', nameResults);
		}
		else {
			initStaticSelect('name', nameResults);
		}
		initDynamicSelect('code', codeResults);

	}
}

	