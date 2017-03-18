var AuthSouce = (function ($) {
    var BASE_URL = "https://simple-vault.tk";
    if (window.location.href.indexOf("http://127.0.0.1:8000") > -1) {
        BASE_URL = "http://127.0.0.1:8000"
    }

    var provisionToken = function (csrf_token) {
        $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            jqXHR.setRequestHeader('X-CSRFToken', csrf_token);
        });
    };

    var csrfTokenFromHtml = function () {
        return $('input[name=csrfmiddlewaretoken]').val();
    };

    var callService = function (url, method, data, callback) {
        callback = callback || function () { };
        $.ajax({
            url: BASE_URL + url,
            processData: false,
            data: JSON.stringify(data),
            contentType: 'application/json',
            type: method,
            dataType: "json",
        }).done(function (response) {
            callback(response)
        }).fail(function (errResponse) {
            callback(errResponse)
        });
    };

    var getService = function (url, callback) {
        callback = callback || function () {
            };
        $.ajax({
            url: BASE_URL + url,
        }).done(function (response) {
            callback(response)
        }).fail(function (errResponse) {
            callback(errResponse)
        });
    };

    return {
        BASE_URL: BASE_URL,
        provisionToken: provisionToken,
        csrfTokenFromHtml: csrfTokenFromHtml,
        service: callService,
        get: getService
    };

})(jQuery);
