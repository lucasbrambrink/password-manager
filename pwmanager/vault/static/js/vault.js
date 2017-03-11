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
        props: ["lookup-key",
            "domain-name",
            "is-hovering",
            "password-entities",
            "new-password",
            "show-create-new",
            "is-focused",
            "show-history"],
        computed: {
            passwordObj: function () {
                return vmVault.objPasswords[this.lookupKey];
            },
            showPasswordHistory: {
                get: function () {
                    return this.passwordObj.showPasswordHistory;
                },
                set: function (value) {
                    if (this.changePassword) {
                        this.changePassword = false;
                    }
                    this.isFocused = true;
                    this.passwordObj.showPasswordHistory = value;
                }
            },
            changePassword: {
                get: function () {
                    return this.passwordObj.showCreateNew;
                },
                set: function (value) {
                    if (this.showPasswordHistory) {
                        this.showPasswordHistory = false;
                    }
                    this.isFocused = true;
                    this.passwordObj.showCreateNew = value;
                }
            },
            isFocused: {
                get: function () {
                    return this.passwordObj.isFocused;
                },
                set: function (value) {
                    this.passwordObj.isFocused = value;
                }
            },

        },
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
                if (response.success) {
                    vmVault.showPassword(response.data.value)
                } else {
                    vmVault.error = true;
                }
            },
            submitNewPassword: function() {

            },
            deletePassword: function () {
            },
            setFocus: function(event) {
                var initialValue = !this.isFocused;
                vmVault.passwords.map(function(p) {
                    p.isFocused = false;
                });
                this.isFocused = initialValue;
            },
            updatePassword: function () {
                var selector = '#' + this.lookupKey;
                var isValid = EzForms.formIsValid(selector, false);
                if (!isValid) {
                    return;
                }
                var $password = $(selector).find('input');
                var newPassword = $password.val();
                $password.val(newPassword
                    .split('')
                    .map(function() {return '*'})
                    .join(''));
                $('form').ezFormValidation();
                var url = '/auth/data/update';
                return AuthSouce.service(
                    url,
                    newPassword,
                    this.createPasswordCallback
                )
            }
        }
    });

    var passwordHistoryItem = Vue.component('password-history-item', {
        template: '#passwordHistoryItem',
        props: ["lookup-key",
                "created-time",],
        methods: {
            showHistoryItem: function () {
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
                if (response.success) {
                    vmVault.showPassword(response.data.value)
                } else {
                    vmVault.error = true;
                }
            }
        }
    });


    var vmVault = new Vue({
        el: '#vault',
        components: {passwordItem: passwordItem},
        data: {
            guid: '',
            error: false,
            objPasswords: {},
            passwords: [],
            showCreatePassword: false,
            TITLES: {
                NEW: "Create new password",
                HIDE: "Hide form"
            },
            create: {
                domainName: '',
                password: '',
                showPlaintext: false,
                length: 26,
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
            this.loadPasswords()
        },
        mounted: function () {
            $('form').ezFormValidation();
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
                var isValid = EzForms.formIsValid('form', false);
                if (!isValid) {
                    return;
                }
                $('form').ezFormValidation();
                var url = '/auth/data/create';
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
                    '/api/v0/password/' + this.guid + '/',
                    this.loadPasswordCallback
                )
            },
            updatePasswordItem: function(passwordKey, key, value) {
                var password;
                var found = false;
                for (var i = 0; i < this.passwords.length; i++) {
                    password = this.passwords[i];
                    if (password.key === passwordKey) {
                        found = true;
                        break;
                    }
                }
                if (found) {
                    password[key] = value;
                }
            },
            loadPasswordCallback: function (passwords) {
                var obj = {};
                vmVault.passwords = passwords.map(function (password) {
                    password.isHovering = false;
                    password.newPassword = "";
                    password.showCreateNew = false;
                    password.showPasswordHistory = false;
                    password.isFocused = false;
                    obj[password.key] = password;
                    return password;
                });
                vmVault.objPasswords = obj;
            }
        }
    });
})();