/**
 * Created by lb on 2/18/17.
 */
(function() {

    var AuthSouce = (function ($) {
        var BASE_URL = "http://127.0.0.1:8000"; //"https://simple-vault.tk";
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
            "show-index",
            "is-focused",
            "domain-name-new"],
        computed: {
            passwordObj: function () {
                return vmVault.objPasswords[this.lookupKey];
            },
            showIndex: {
                get: function () {
                    return this.passwordObj.showIndex;
                },
                set: function(value) {
                    return this.passwordObj.showIndex = value;
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
            setFocus: function(event) {
                var initialValue = !this.isFocused;
                if ($(event.target).is('button')) {
                    initialValue = true;
                }
                vmVault.passwords.map(function(p) {
                    p.isFocused = false;
                });
                this.isFocused = initialValue;
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
            showMainIndex: 1,
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
                url: '',
                hasPassword: false,
                domainName: '',
            }
        },
        computed: {
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
                        self.showMainIndex = 3;
                    }
                };
                var callback = function (self) {
                    return function() {
                        AuthSouce.service(
                            AuthSouce.BASE_URL + '/api/v0/auth/get-nonce/',
                            'PUT', {}, load(self), self.token)
                    }
                };
                this.provisionCsrfToken(callback(this));
            },
            submitLogin: function() {
                var cb = function(self) {
                    return function (resp) {
                        chrome.storage.local.set({ "public_token": resp.token },
                            function(){
                        });
                        showMainIndex = 3;
                        self.activateSession();
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
                    password.showIndex = 2;
                    password.isFocused = false;
                    password.domainNameNew = password.domainName;
                    obj[password.key] = password;
                    return password;
                }).sort(function(a, b) {
                    if (a.domainName < b.domainName) return -1;
                    if (a.domainName > b.domainName) return 1;
                    return 0;
                });
                vmVault.objPasswords = obj;
            },
            acceptPageInfo: function(sender) {
                this.currentWebsite.title = sender.tab.title.split('|')[0];
                this.currentWebsite.url = sender.tab.url;
                this.currentWebsite.domainName = this.parseDomainName(sender.tab.url);
                this.currentWebsite.hasPassword = this.hasPassword(this.currentWebsite.domainName);
            },
            parseDomainName: function(url) {
                var link = $('<a href="' + url + '">')[0];
                return link.hostname;
            },
            hasPassword: function(domainName) {
                return this.passwords.filter(function(p) {
                    return p.domainName === domainName;
                }).length > 0;
            }
        }
    });
    window.vmVault = vmVault;
    chrome.tabs.executeScript(null, {file: "content_script.js"});
    chrome.runtime.onMessage.addListener(
      function(request, sender, sendResponse) {
          vmVault.acceptPageInfo(sender);
    });

})();