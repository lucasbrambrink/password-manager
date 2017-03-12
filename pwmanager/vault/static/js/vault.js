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

    var requestPasswordMixin = {
        methods: {
            requestPassword: function () {
                return this.requestData({
                    query: this.lookupKey,
                    guid: vmVault.guid
                })
            },
            requestData: function (data) {
                var url = '/api/v0/password/';
                return AuthSouce.service(
                    url,
                    "POST",
                    data,
                    this.requestDataCallback);
            },
            requestDataCallback: function (response) {
                console.log(response);
                if (response.value) {
                    vmVault.showPassword(response.value)
                } else {
                    vmVault.error = true;
                }
            }
        }
    };


    var passwordItem = Vue.component('password-item', {
        template: '#passwordItem',
        mixins: [requestPasswordMixin],
        props: ["lookup-key",
            "domain-name",
            "is-hovering",
            "password-entities",
            "new-password",
            "show-create-new",
            "show-delete",
            "is-focused",
            "show-history",
            "domain-name-new"],
        computed: {
            passwordObj: function () {
                return vmVault.objPasswords[this.lookupKey];
            },
            showPasswordHistory: {
                get: function () {
                    return this.passwordObj.showPasswordHistory;
                },
                set: function (value) {
                    if (this.changePassword || this.showDeleteSection) {
                        this.changePassword = false;
                        this.showDeleteSection = 0;
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
                    if (this.showPasswordHistory || this.showDeleteSection) {
                        this.showPasswordHistory = false;
                        this.showDeleteSection = 0;
                    }
                    this.isFocused = true;
                    this.passwordObj.showCreateNew = value;
                }
            },
            showDeleteSection: {
                get: function () {
                    return this.passwordObj.showDelete;
                },
                set: function (value) {
                    if (this.showPasswordHistory || this.changePassword) {
                        this.showPasswordHistory = false;
                        this.changePassword = false;
                    }
                    this.isFocused = true;
                    this.passwordObj.showDelete = value;
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
            requestCurrentPassword: function () {
                return this.requestData({
                    query: this.passwordEntities[0].guid
                })
            },
            toggleDelete: function () {
                if (this.showDelete > 0) {
                    this.showDelete = 0;
                } else {
                    this.showDelete = 1;
                }
            },
            deletePassword: function () {
                return AuthSouce.service(
                    "/api/v0/password/create/",
                    "DELETE",
                    {
                        passwordGuid: this.lookupKey
                    },
                    function () {
                        vmVault.loadPasswords();
                    }
                )
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

                var url = '/api/v0/password/create/';
                return AuthSouce.service(
                    url,
                    "POST",
                    {
                        password: newPassword,
                        passwordGuid: this.lookupKey,
                        domainName: this.domainNameNew
                    },
                    this.createPasswordCallback
                )
            },
            createPasswordCallback: function (resp) {
                vmVault.createPasswordCallback(resp);
                this.showPasswordHistory = true;
                this.isFocused = true;
            }
        }
    });

    var passwordHistoryItem = Vue.component('password-history-item', {
        template: '#passwordHistoryItem',
        props: ["lookup-key",
                "created-time",],
        mixins: [requestPasswordMixin]
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
            createPassword: function (event) {
                var selector = 'form.generate-password';
                var isValid = EzForms.formIsValid(selector, false);
                if (!isValid) {
                    return;
                }
                var url = '/api/v0/password/create/';
                return AuthSouce.service(
                    url,
                    "POST",
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
                if (response.status !== undefined) {
                    vmVault.error = true;
                } else {
                    vmVault.showCreatePassword = false;
                    vmVault.loadPasswords();
                }
            },
            consumeCreateForm: function () {
                var data = {
                    domainName: this.create.domainName,
                    password: this.create.password,
                    passwordGuid: '',
                };
                this.create.password = null;
                this.create.domainName = null;
                return data;
            },
            loadPasswords: function () {
                return AuthSouce.service(
                    '/api/v0/password/list/',
                    "POST",
                    {},
                    this.loadPasswordCallback
                )
            },
            loadPasswordCallback: function (passwords) {
                if (passwords.status !== undefined) {
                    console.log(passwords);
                    return;
                }
                var obj = {};
                vmVault.passwords = passwords.map(function (password) {
                    password.isHovering = false;
                    password.newPassword = "";
                    password.showCreateNew = false;
                    password.showPasswordHistory = false;
                    password.showDelete = 0;
                    password.isFocused = false;
                    password.domainNameNew = password.domainName;
                    obj[password.key] = password;
                    return password;
                });
                vmVault.objPasswords = obj;
            }
        }
    });
})();