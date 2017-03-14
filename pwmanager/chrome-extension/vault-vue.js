/**
 * Created by lb on 2/18/17.
 */
(function() {

    var AuthSouce = (function ($) {
        var BASE_URL = "http://127.0.0.1:8000";
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
            username: '',
            passwords: [],
            showCreatePassword: false,
            showVault: false,
            showLogin: true,
            showRegistration: false,
            viewNavIndex: 1,
            searchTerm: '',
            token: '',
            csrf: '',
            TITLES: {
                NEW: "Create new password",
                HIDE: "Hide form"
            },
            login: {
                email: '',
                password: '',
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
            currentWebsite: {
                title: '',
                url: ''
            }
        },
        computed: {
            // token: function () {
            //     return window.token;
            // },
            isAuthenticated: function () {
                return this.token !== undefined && this.token.length > 0;
            },
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
            },
            passwordsVisible: function () {
                if (this.searchTerm.length === 0) {
                    return this.passwords
                }
                var self = this;
                return this.passwords.filter(function(p) {
                    return p.domainName.indexOf(self.searchTerm) > -1;
                });
            }
        },
        created: function () {
            var cb = function (self) {
                return function(item) {
                    console.log(self, item);
                    self.token = item.public_token;
                    if (self.isAuthenticated) {
                        self.activateSession();
                    }
                }
            };
            chrome.storage.local.get(["public_token"], cb(this));
            this.provisionCsrfToken();
            chrome.tabs.onUpdated.addListener(function() {
                console.log(window);
                console.log(window.location);
            });

            //     code: '('  + ')();' //argument here is a string but function.toString() returns function's code
            // }, function(results) {
            // //Here we have just the innerHTML and not DOM structure
            // //     console.log('Popup script:')
            // //     console.log(results[0]);
            //     console.log(window);
            // });
            // this.currentWebsite.url = window.location.href;
            // this.currentWebsite.title = window.location.
            // this.loadLoginHtml();
            // this.loadVaultHtml()

        },
        mounted: function () {
            $('form').ezFormValidation();
        },
        methods: {
            provisionCsrfToken: function (callback) {
                var cb = function(self) {
                    return function (resp) {
                        var csrf = $(resp);
                        self.csrftoken = csrf.val();
                        AuthSouce.provisionToken(self.csrftoken);
                        if (typeof callback === 'function' ) callback();
                    };
                };
                AuthSouce.get(
                    AuthSouce.BASE_URL + '/chrome-extension/csrf-token',
                    cb(this));
            },
            activateSession: function () {
                // assign token to request;
                var load = function(self) {
                    return function (resp) {
                        console.log(resp);
                        self.loadPasswords();
                        self.showVault = true;
                        self.showLogin = false;
                    }
                };
                var callback = function (self) {
                    return function() {
                        AuthSouce.service(
                            AuthSouce.BASE_URL + '/api/v0/auth/get-token/',
                            'PUT', {}, load(self), self.token)
                    }
                };
                // this.provisionCallback =
                this.provisionCsrfToken(callback(this));
            },
            submitLogin: function() {
                var cb = function(self) {
                    return function (resp) {
                        console.log(resp);
                        chrome.storage.local.set({ "public_token": resp.token },
                            function(){
                        });
                        self.showVault = true;
                        self.provisionCsrfToken();
                    };
                };
                AuthSouce.service(
                    AuthSouce.BASE_URL + '/api/v0/auth/get-token/',
                    'POST',
                    {
                        email: this.login.email,
                        password: this.login.password,
                        csrftoken: this.csrftoken
                    },
                    cb(this));
            },

            // loadLoginHtml: function () {
            //     var self = this;
            //     var url = AuthSouce.BASE_URL + '/chrome-extension/auth/';
            //     console.log(url);
            //     return AuthSouce.get(
            //         url,
            //         function (response) {
            //             console.log(response);
            //             self.loginHtml = response;
            //             setTimeout(function() {
            //                 $('form')
            //                     .removeAttr('action')
            //                     .on('submit', function (e) {
            //                     e.preventDefault();
            //                     var data = {
            //                         email: $('form input[type=text]').val(),
            //                         password: $('form input[type=password]').val()
            //                     };
            //                     AuthSouce.service(
            //                         AuthSouce.BASE_URL + '/api/v0/auth/get-token/',
            //                         'POST',
            //                         data,
            //                         function (resp) {
            //                             console.log(resp);
            //                             chrome.storage.local.set({ "public_token": resp.token },
            //                                 function(){
            //                             });
            //                             self.loadVaultHtml();
            //                             self.showVault = true;
            //                         }
            //                     )
            //                 })
            //             }, 1000)
            //         });
            // },
            // registrationLoginHtml: function () {
            //     var that = this;
            //     var url = AuthSouce.BASE_URL + '/chrome-extension/registration/';
            //     return AuthSouce.get(
            //         url,
            //         function (response) {
            //             that.registrationHtml = response;
            //         });
            // },
            // loadVaultHtml: function () {
            //     var that = this;
            //     var url = AuthSouce.BASE_URL + '/chrome-extension/vault/';
            //     return AuthSouce.get(
            //         url,
            //         function (response) {
            //             that.vaultHtml = response;
            //         });
            // },
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
                    AuthSouce.BASE_URL + '/api/v0/password/list/',
                    "POST",
                    {},
                    this.loadPasswordCallback,
                    this.token
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
    window.vmVault = vmVault;
})();