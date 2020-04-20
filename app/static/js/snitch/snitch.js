$(document).ready(function() {
    $('[data-toggle="popover"]').popover({
        html: true
    });

    $('[data-toggle="popover"]').click(function() {
        return false;
    });

    $('.submit-on-click').click(function() {
        $(this).closest('form').submit();
        return false;
    });
});