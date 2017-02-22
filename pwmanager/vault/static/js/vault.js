/**
 * Created by lb on 2/18/17.
 */

var AuthSouce = (function($) {
    var csrfToken = function () {
        $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            var token = $('input[name=csrfmiddlewaretoken]').val();
            jqXHR.setRequestHeader('X-CSRFToken', token);
        });
    };

    var callService = function (url, data, callback) {
        callback = callback || function () {};
        $.ajax({
            url: url,
            processData: false,
            data: JSON.stringify(data),
            contentType: 'application/json',
            type: 'POST',
            dataType: "json",
        }).done(function(response) {
            callback(response)
        }).fail(function(errResponse) {
            callback(errResponse)
        });
    };

    var getService = function (url, callback) {
        callback = callback || function () {};
        $.ajax({
            url: url,
        }).done(function(response) {
            callback(response)
        }).fail(function(errResponse) {
            callback(errResponse)
        });
    };

    return {
        csrf: csrfToken,
        service: callService,
        get: getService
    };

})(jQuery);

var vmVault = new Vue({
    el: '#vault',
    data: {
        guid: '',
        error: false,
        passwords: [],
        showCreatePassword: false,
        create: {
            name: '',
            password: ''
        }
    },
    created: function () {
        this.guid = $('#guid').val();
        AuthSouce.csrf();
        this.loadPasswords()
    },
    methods: {
        showPassword: function(password) {
            window.prompt("Copy to clipboard: Ctrl+C, Enter", password);
        },
        requestPassword: function (event) {
            var key = $(event.target).attr('data-key');
            this.requestData({
                query: key,
                guid: this.guid
            });
        },
        requestData: function(data) {
            var url = '/auth/data/get';
            return AuthSouce.service(
                url,
                data,
                this.requestDataCallback);
        },
        requestDataCallback: function (response) {
            console.log(response);
            if (response.success) {
                vmVault.showPassword(response.data.value)
            } else {
                vmVault.error = true;
            }
        },
        createPassword: function (event) {
            var url = '/auth/data/create';
            return AuthSouce.service(
                url,
                this.consumeCreateForm(),
                this.createPasswordCallback
            )
        },
        createPasswordCallback: function (response) {
            console.log(response);
            if (response.success) {
                vmVault.loadPasswords();
            } else {
                vmVault.error = true;
            }
        },
        consumeCreateForm: function () {
            var data = {
                name: this.create.name,
                password: this.create.password,
                guid: this.guid
            };
            this.create = {};
            return data;
        },
        loadPasswords: function () {
            return AuthSouce.get(
                '/vault/' + this.guid + '/list',
                this.loadPasswordCallback
            )
        },
        loadPasswordCallback: function (response) {
            console.log(response);
            if (response.success) {
                vmVault.passwords = JSON.parse(response.data.passwords)
                    .map(function(model) {
                        return {
                            key: model.fields.key,
                            name: model.fields.name
                        }
                    });
            }
        }

    }
});