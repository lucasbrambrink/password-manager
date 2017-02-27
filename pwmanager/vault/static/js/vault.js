/**
 * Created by lb on 2/18/17.
 */
(function() {

    var AuthSouce = (function ($) {
        var csrfToken = function () {
            $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
                var token = $('input[name=csrfmiddlewaretoken]').val();
                jqXHR.setRequestHeader('X-CSRFToken', token);
            });
        };

        var callService = function (url, data, callback) {
            callback = callback || function () {
                };
            $.ajax({
                url: url,
                processData: false,
                data: JSON.stringify(data),
                contentType: 'application/json',
                type: 'POST',
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

    })(jQuery);

    var GeneratePassword = (function () {


        var rchoose = function (array) {
            return array[Math.floor(Math.random() * array.length)];
        };

        var generatePassword = function (length) {
            var lowercase = 'abcdefghijklmnopqrstuvwxyz';
            var upppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            var numbers = '1234567890';
            var symbols = '!@#$%^&*+=?';
            var choices = [
                lowercase,
                upppercase,
                numbers,
                symbols
            ];

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


    var passwordItem = Vue.component('password-item', {
        template: '#passwordItem',
        props: ["lookup-key", "name"],
        methods: {
            requestPassword: function () {
                return this.requestData({
                    query: this.lookupKey,
                    guid: vmVault.guid
                })
            },
            requestData: function (data) {
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
            changePassword: function () {
            },
            deletePassword: function () {
            }
        }
    });


    var vmVault = new Vue({
        el: '#vault',
        components: {passwordItem: passwordItem},
        data: {
            guid: '',
            error: false,
            passwords: [''],
            showCreatePassword: false,
            create: {
                name: '',
                password: '',
                showPlaintext: false,
            }
        },
        computed: {
            hideCreatePassword: function () {
                return !this.showCreatePassword;
            },
            isEmpty: function () {
                return this.passwords.length === 0;
            }
        },
        created: function () {
            this.guid = $('#guid').val();
            AuthSouce.csrf();
            this.loadPasswords()
        },
        methods: {
            showPassword: function (password) {
                window.prompt("Copy to clipboard: Ctrl+C, Enter", password);
            },
            requestData: function (data) {
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
            generatePassword: function () {
                this.create.password = GeneratePassword.generate(26);
                this.create.showPlaintext = true;
            },
            createPasswordCallback: function (response) {
                console.log(response);
                if (response.success) {
                    vmVault.showCreatePassword = false;
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
                this.create.password = null;
                this.create.name = null;
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
                        .map(function (model) {
                            return {
                                key: model.fields.key,
                                name: model.fields.name
                            }
                        });
                }
            }

        }
    });
})();