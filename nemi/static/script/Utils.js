Utils = {
	setEnabled: function(els /* jquery elements */, isEnabled /*Boolean */){
		/* If isEnabled is true, remove the disabled attribute and class from els.
		 * If false, add the attribute and class to els. For any of the els which hav
		 *  associated labels, remove/add the disabled class as appropriate.
		 */
		if (isEnabled) {
			els.removeAttr('disabled').removeClass('disabled');
			els.each(function(){
				$('label[for="' + $(this).attr('id') + '"]').removeClass('disabled');
			});
		}
		else {
			els.attr('disabled', 'disabled').addClass('disabled');
			els.each(function(){
				$('label[for="' + $(this).attr('id') + '"]').addClass('disabled');
			});
		}
	}
}
