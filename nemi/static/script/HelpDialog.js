HelpDialog = {
    dialogEl : {},
    initialize : function(el /* jquery element */) {
        HelpDialog.dialogEl = el;
        el.dialog({
            autoOpen : false,
            title : 'Basic Dialog',
            height : 200,
            width : 300
        });
    },
    show : function(header /* String */, info /* String */) {
        HelpDialog.dialogEl.html(info);
        // This preprends {{ STATIC_URL}} to any img tag in info
        HelpDialog.dialogEl.find('img').each(function() {
            var src = $(this).attr("src");
            $(this).attr("src", "{{ STATIC_URL }}" + src);
        });

        HelpDialog.dialogEl.dialog('option', 'title', header);
        HelpDialog.dialogEl.dialog('option', 'position', 'center');

        if (!HelpDialog.dialogEl.dialog('isOpen')) {
            HelpDialog.dialogEl.dialog('option', 'height', 250);
            HelpDialog.dialogEl.dialog('option', 'width', 350);
            HelpDialog.dialogEl.dialog('open');
        }
    }
};