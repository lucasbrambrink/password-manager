/**
 * Created by lb on 2/18/17.
 */
// if request password

function requestPassword() {
    //get data
    var resp = {
        success: true,
        password: 'test'
    };
    window.prompt("Copy to clipboard: Ctrl+C, Enter", resp.password);
}

var passwords = [{
    name: "Password 1",
    key: "passwordId",
},{
    name: "Password 2",
    key: "password2Id",
}];

var AuthSouce = (function($) {
    var csrfToken = function () {
        $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            var token = $('input[name=csrfmiddlewaretoken]').val();
            jqXHR.setRequestHeader('X-CSRFToken', token);
        });
    };

    var callService = function (url, data, callback) {
        callback = callback || function () {};
        csrfToken();
        $.ajax({
            url: url,
            dataType: 'JSON',
            contentType: 'application/json; charset=utf-8',
            type: 'POST',
            data: JSON.stringify(data)
        }).done(function(response) {
            callback(response)
        }).fail(function(errResponse) {
            callback(errResponse)
        });
    };

    return {
        csrf: csrfToken,
        service: callService,
    };

})(jQuery);

var vmVault = new Vue({
    el: '#vault',
    data: {
        nonce: '',
        guid: '',
        error: false,
        passwords: passwords
    },
    created: function () {
        this.nonce = $('#nonce').val();
        this.guid = $('#guid').val();
    },
    methods: {
        showPassword: function(password) {
            window.prompt("Copy to clipboard: Ctrl+C, Enter", password);
        },
        requestPassword: function (event) {
            var key = $(event.target).attr('data-key');
            this.requestData({'key': key});
        },
            // get password from server using nonce
        requestData: function(data) {
            var url = '/auth/data';
            return AuthSouce.service(
                url,
                data,
                this.requestDataCallback);
        },
        requestDataCallback: function (response) {
            console.log(response);
            if (response.success) {
                vmVault.showPassword(response.value)
            } else {
                vmVault.error = true;
            }
        }
    }
});