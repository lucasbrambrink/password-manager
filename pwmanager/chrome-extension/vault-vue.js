/**
 * Created by lb on 2/18/17.
 */
(function() {

    var AuthSouce = (function ($) {
        var BASE_URL = 'http://127.0.0.1:8000';
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
            BASE_URL: BASE_URL,
            API_URL: BASE_URL + '/api/v0',
            csrf: csrfToken,
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


    var passwordItem = Vue.component('password-item', {
        template: '#passwordItem',
        props: ["lookup-key", "domain-name"],
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
            showRegistration: false,
            showLogin: true,
            loginHtml: '',
            userName: '',
            registrationHtml: '',
            TITLES: {
                NEW: "Create new password",
                HIDE: "Hide form"
            },
            create: {
                domainName: '',
                password: '',
                showPlaintext: false,
                length: 20,
                letters: true,
                digits: true,
                symbols: true,
            },
        },
        computed: {
            hideCreatePassword: function () {
                if (!this.showCreatePassword) {
                    $('form').setFormNeutral();
                }
                return !this.showCreatePassword;
            },
            isEmpty: function () {
                return this.passwords.length === 0;
            },
            toggleTitle: function () {
                return this.showCreatePassword ? this.TITLES.HIDE : this.TITLES.NEW;
            }
        },
        created: function () {
            this.guid = $('#guid').val();
            AuthSouce.csrf();
            // this.loadPasswords()
            this.loadLoginHtml();
        },
        mounted: function () {
            $('form').ezFormValidation();
        },
        methods: {
            loadLoginHtml: function () {
                var url = AuthSouce.BASE_URL + '/chrome-extension/auth';
                return AuthSouce.get(
                    url,
                    function (response) {
                        vmVault.loginHtml = response;
                    });
            },
            registrationLoginHtml: function () {
                var url = AuthSouce.BASE_URL + '/chrome-extension/registration';
                return AuthSouce.get(
                    url,
                    function (response) {
                        vmVault.registrationHtml = response;
                    });
            },
            showPassword: function (password) {
                window.prompt("Copy to clipboard: Ctrl+C, Enter", password);
            },
            requestData: function (data) {
                var url = AuthSouce.API_URL + '/auth/data/get';
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
                var isValid = EzForms.formIsValid('form', false);
                if (!isValid) {
                    return;
                }
                $('form').ezFormValidation();
                var url = AuthSouce.API_URL + '/auth/data/create';
                return AuthSouce.service(
                    url,
                    this.consumeCreateForm(),
                    this.createPasswordCallback
                )
            },
            generatePassword: function () {
                this.create.password = GeneratePassword.generate(
                    this.create.length,
                    this.create.letters,
                    this.create.digits,
                    this.create.symbols
                );
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
                    domainName: this.create.domainName,
                    password: this.create.password,
                    guid: this.guid
                };
                this.create.password = null;
                this.create.domainName = null;
                return data;
            },
            loadPasswords: function () {
                return AuthSouce.get(
                    AuthSouce.API_URL + '/vault/' + this.guid + '/list',
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
                                domainName: model.fields.domain_name
                            }
                        });
                }
            }

        }
    });
})();