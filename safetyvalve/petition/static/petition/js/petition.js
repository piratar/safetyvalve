
$(function () {

    $('a.unsign').bind('click', function (e) {
        var msg = $('#msg_are_you_sure').text();
        if (!confirm('are you sure?')) {
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

        url = '/frumvarp/' + petition_id + '/skra/?show_public=' + (show_public ? '1' : '0');

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

    $('.fb_share').sharrre({
        share: {
            facebook: true
        },
        template: '<div class="icon share_icon"><i class="fa fa-facebook-square"></i><span class="detail_figure">{total}</span></div>',
        enableHover: false,
        enableTracking: true,
        click: function(api, options) {
            api.simulateClick();
            api.openPopup('facebook');
        }
    });

    $('.twitter_share').sharrre({
        share: {
            facebook: true
        },
        template: '<div class="icon share_icon"><i class="fa fa-twitter-square"></i><span class="detail_figure">{total}</span></div>',
        enableHover: false,
        enableTracking: true,
        click: function(api, options) {
            api.simulateClick();
            api.openPopup('twitter');
        }
    });

});

