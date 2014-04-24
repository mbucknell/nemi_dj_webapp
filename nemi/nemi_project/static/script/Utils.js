Utils = {
    setEnabled : function(els /* jquery elements */, isEnabled /* Boolean */) {
        /*
         * If isEnabled is true, remove the disabled attribute and class from
         * els. If false, add the attribute and class to els. For any of the els
         * which have associated labels, remove/add the disabled class as
         * appropriate.
         */
        if (isEnabled) {
            els.removeAttr('disabled').removeClass('disabled');
            els.each(function() {
                $('label[for="' + $(this).attr('id') + '"]').removeClass(
                        'disabled');
            });
        } else {
            els.attr('disabled', 'disabled').addClass('disabled');
            els.each(function() {
                $('label[for="' + $(this).attr('id') + '"]').addClass(
                        'disabled');
            });
        }
    },

    setSelect2Enabled : function(els /* jquery elements */, isEnabled /* Boolean */) {
        /*
         * Set the enable state of els to isEnabled. Also set the state of the
         * associate label element. This function assumes that the associated
         * label has the same id as the select2 element with '-label' appended.
         */
        if (isEnabled) {
            els.select2('enable');
            els.each(function() {
                $('#' + $(this).attr('id') + '-label').removeClass('disabled');
            });
        } else {
            els.select2('disable');
            els.each(function() {
                $('#' + $(this).attr('id') + '-label').addClass('disabled');
            });
        }
    },

    createSelectMenu : function(select2Id /* hidden element id */,
            url /* String */, data /* Object */) {
        // Create a select2 option menu by retrieving the choices using url and
        // data.
        $.ajax({
            url : url,
            data : data,
            success : function(resp) {
                var selectData = [];
                var maxChar = 0; // Used to set the width to the display
                                    // value with the most characters.

                for ( var i = 0; i < resp.choices.length; i++) {
                    selectData.push({
                        id : resp.choices[i].value,
                        text : resp.choices[i].display_value
                    });

                    if (resp.choices[i].display_value.length > maxChar) {
                        maxChar = resp.choices[i].display_value.length;
                    }
                }

                var select2El = $('#' + select2Id);

                select2El.select2({
                    width : 'off',
                    data : selectData,
                    placeholder : 'All',
                    allowClear : true,
                    minimumResultsForSearch : 15,
                });

                var enableFn = select2El.data('enableFn');
                if (enableFn) {
                    Utils.setSelect2Enabled(select2El, enableFn());
                }
                //Set state of menu from web storage and set up change handler to store currents state
                if (sessionStorage[select2Id]) {
                    select2El.select2('val', sessionStorage[select2Id]);
                } else {
                    select2El.select2('val', 'all');
                }
                select2El.on('change', function(e) {
                    sessionStorage[select2Id] = e.val;
                });
            }
        });
    },
    getHiddenInputHtml : function(name /* String */, value /* String */) {
        /* Return a string containing the html for a hidden input with name and value.
         */
        return '<input type="hidden" name="' + name + '" value="' + value
                + '" />';
    }
}
