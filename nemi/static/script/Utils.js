Utils = {
	setEnabled: function(els /* jquery elements */, isEnabled /*Boolean */){
		/* If isEnabled is true, remove the disabled attribute and class from els.
		 * If false, add the attribute anc class to els. For any of the els which are inputs
		 * find their associated labels and remove/add the disabled class as appropriate.
		 */
		var inputEls = els.filter('input[id]');
		if (isEnabled) {
			els.removeAttr('disabled').removeClass('disabled');
			inputEls.each(function(){
				$('label[for="' + $(this).attr('id') + '"]').removeClass('disabled');
			});
		}
		else {
			els.attr('disabled', 'disabled').addClass('disabled');
			inputEls.each(function(){
				$('label[for="' + $(this).attr('id') + '"]').addClass('disabled');
			});
		}
	}
}