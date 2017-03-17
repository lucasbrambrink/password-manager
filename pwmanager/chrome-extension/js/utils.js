var AuthSouce = (function ($) {
    var BASE_URL = "https://simple-vault.tk";
    var provisionToken = function (csrf_token) {
        $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            jqXHR.setRequestHeader('X-CSRFToken', csrf_token);
        });
    };

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var callService = function (url, method, data, callback, token) {
        callback = callback || function () { };
        var requestObj = {
            url: url,
            processData: false,
            data: JSON.stringify(data),
            contentType: 'application/json',
            type: method,
            dataType: "json",
        };
        if (token !== undefined || token !== null) {
            requestObj.headers = {
                'Authorization':'Token ' + token
            };
        }
        $.ajax(requestObj)
        .done(function (response) {
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
        BASE_URL: BASE_URL,
        provisionToken: provisionToken,
        getCookie: getCookie,
        service: callService,
        get: getService
    };

})(jQuery);

var GeneratePassword = (function () {


    var rchoose = function (array) {
        return array[Math.floor(Math.random() * array.length)];
    };

    var generatePassword = function (length, withLetters, withDigits, withSymbols) {
        var lowercase = 'abcdefghijklmnopqrstuvwxyz';
        var upppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        var numbers = '1234567890';
        var symbols = '!@#$%^&*+=?';
        var choices = [];
        if (withLetters) {
            choices.push(lowercase);
            choices.push(upppercase);
        }
        if (withDigits) {
            choices.push(numbers);
        }
        if (withSymbols) {
            choices.push(symbols);
        }

        var password = [],
            category;
        for (var x = 0; x < length; x++) {
            category = rchoose(choices);
            password.push(rchoose(category));
        }

        return password.join('');
    };

    return {
        generate: generatePassword
    };
})();