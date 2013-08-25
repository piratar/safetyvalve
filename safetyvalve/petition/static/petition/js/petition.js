
$(function () {

    $('a.unsign').bind('click', function (e) {
        if (!confirm('Ertu viss?')) {
            e.preventDefault();
            return false;
        }
    });

    $('.pre_selection_container a.addremove_signature').bind('click', function(e) {
        container = $(this).parent().parent();

        container.find('.pre_selection_container').hide();
        container.find('.post_selection_container').show();

        e.preventDefault();
        return false;
    });

    $('.post_selection_container a.addremove_signature').bind('click', function(e) {
        container = $(this).parent().parent();

        show_public = container.find('.show_public').is(':checked');

        petition_id = container.data('id');

        url = '/petition/' + petition_id + '/sign/?show_public=' + (show_public ? '1' : '0');

        location.href = url;

        e.preventDefault();
        return false;
    });

    $('.post_selection_container a.signature_cancel').bind('click', function(e) {
        container = $(this).parent().parent();

        container.find('.post_selection_container').hide();
        container.find('.pre_selection_container').show();

        e.preventDefault();
        return false;
    });

});

