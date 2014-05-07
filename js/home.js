$(function() {
    $('.picture-div').click(function(e) {
        e.preventDefault();
        window.location = "/mfa/" + $(this).data('id');
    });
});
