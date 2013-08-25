
$(function () {

    $('.change-public').bind('click', function (e) {

        var row=$(this).parent().parent(),
            anchor=$(this),
            href=$(this).attr('href'),
            is_public = $(this).data('show-public') == 'yes',
            success = false;

        $.ajax({
            url: href,
            method: 'GET',
            async: false,
            success: function () {
                success = true;
                anchor.text(yesno[is_public*1]);  // Now is_public has changed
                anchor.data('show-public', ['yes', 'no'][is_public*1]);
            }
        })
        if (success) {
            e.preventDefault();
            return false;
        }
        return true;
    });

    $('.remove-signature').bind('click', function (e) {

        var row=$(this).parent().parent(),
            href=$(this).attr('href'),
            method=$(this).data('method');

        if (method == 'browser-confirm') {

            var dialog = undefined;
            $.ajax({
                url: href,
                data: { 'method': method },
                method: 'GET',
                dataType: 'json',
                async: false,
                success: function (data) {
                    dialog = data;
                }
            });
            if (confirm(dialog.title + ':\n\n' + dialog.text)) {
                $.ajax({
                    url: href,
                    method: 'GET',
                    data: { 'answer': 'yes' },
                    success: function (data) {
                        row.fadeOut();
                    }
                });
            }
            e.preventDefault();
            return false;

        } else {
            return true;
        }
    })

});
