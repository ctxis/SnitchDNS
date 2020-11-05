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

    $('.confirm-delete').click(function() {
        var formToSubmit = $(this).closest('form').attr('id');
        var text = $(this).data('text') !== undefined ? $(this).data('text') : '';
        if (text.length > 0) {
            $('#delete-confirmation-text').text(text);
        }
        $('#delete-form-to-submit').val(formToSubmit);
        $('#delete-confirmation-box').modal('show');
        return false;
    });

    $('.delete-confirmation-button').click(function() {
        var formToSubmit = $('#delete-form-to-submit').val();
        $('#' + formToSubmit).submit();
        $('#delete-confirmation-box').modal('hide');
    });

    $('.toggle-error-box').click(function() {
        var boxId = $(this).attr('data-id');
        var box = $('.error-box-' + boxId);
        if ($(box).hasClass('d-none')) {
            $(box).removeClass('d-none');
            $('html, body').animate({
                scrollTop: $(box).offset().top
            });
        } else {
            $(box).addClass('d-none');
        }
        return false;
    });
});