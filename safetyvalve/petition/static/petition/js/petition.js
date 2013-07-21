
$(function () {

    $('a.unsign').bind('click', function (e) {
        if (!confirm('Ertu viss?')) {
            e.preventDefault();
            return false;
        }
    })

});