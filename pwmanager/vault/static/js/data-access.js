var AuthSouce = (function ($) {
    var csrfToken = function () {
        $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            var token = $('input[name=csrfmiddlewaretoken]').val();
            jqXHR.setRequestHeader('X-CSRFToken', token);
        });
    };

    var callService = function (url, method, data, callback) {
        callback = callback || function () { };
        $.ajax({
            url: url,
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
            url: url,
        }).done(function (response) {
            callback(response)
        }).fail(function (errResponse) {
            callback(errResponse)
        });
    };

    return {
        csrf: csrfToken,
        service: callService,
        get: getService
    };

})(jQuery);/**
 * Created by lucasbrambrink on 3/13/17.
 */
