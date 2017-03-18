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

var tooltipMixin = {
    mounted: function() {
        $('[data-toggle="tooltip"]').tooltip({
            trigger: "hover"
        });
    },
};


var ContentScriptApi = {
    mounted: function() {
        // bind chrome tabs
        chrome.tabs.executeScript(null, {file: "content_script.js"});
        chrome.runtime.onMessage.addListener(
          function(request, sender, sendResponse) {
              this.acceptPageInfo(sender);
        });
    },
    methods: {
        acceptPageInfo: function (sender) {
            this.currentWebsite.title = sender.tab.title.split('|')[0];
            this.currentWebsite.url = sender.tab.url;
            this.currentWebsite.domainName = this.parseDomainName(sender.tab.url);
            this.currentWebsite.hasPassword = this.hasPassword(this.currentWebsite.domainName);
        },
        parseDomainName: function (url) {
            var link = $('<a href="' + url + '">')[0];
            return link.hostname;
        },
        hasPassword: function (domainName) {
            return this.passwords.filter(function (p) {
                    return p.domainName === domainName;
                }).length > 0;
        }
    }
};


var VmVault = Vue.extend({
    data: function () {
        return {
            guid: '',
            error: false,
            objPasswords: {},
            passwords: [],
            TITLES: {
                NEW: "Create new password",
                HIDE: "Hide form"
            },
            searchTerm: '',
            showIndex: 1,
            create: {
                domainName: '',
                password: '',
                username: '',
                showPlaintext: false,
                length: 26,
                letters: true,
                digits: true,
                symbols: true
            },
            profile: {
                firstName: '',
                lastName: '',
                phone: '',
            },
            previousState: {
                activeDomain: null,
                authIndexes: {},
            }
        };
    },
    computed: {
        passwordsVisible: function () {
            if (this.searchTerm.length === 0) {
                return this.passwords
            }
            var self = this;
            return this.passwords.filter(function(p) {
                return p.domainName.indexOf(self.searchTerm) > -1;
            });
        },
        isEmpty: function () {
            return this.passwords.length === 0;
        },
        toggleTitle: function () {
            var original = this.showIndex;
            return original !== 2 ? this.TITLES.NEW : original;
        },
        showCreateNew: function() {
            return this.showIndex === 2;
        },
        showPasswords: function () {
            return this.showIndex === 1;
        },
        showProfile: function () {
            return this.showIndex === 3;
        }
    },
    mounted: function () {
        $('form').ezFormValidation();
        $('[data-toggle="tooltip"]').tooltip({
            trigger: "hover"
        });
    },
    methods: {
        showPassword: function (password) {
            window.prompt("Copy to clipboard: Ctrl+C, Enter", password);
        },
        setPreviousState: function() {
            var active = this.passwords.filter(function(p) {
                return p.isFocused === true;
            });
            if (active.length === 0) {
                this.previousState.activeDomain = null
            } else {
                var domain = active[0];
                this.previousState.activeDomain = domain.domainName;
                var indexes = {};
                domain.externalauthenticationSet.map(function(ea) {
                    indexes[ea.key] = ea.showIndex;
                });
                this.previousState.authIndexes = indexes;
            }
        },
        toggleViewIndex: function(targetIndex, defaultIndex) {
            var original = this.showIndex;
            if (original === targetIndex) original = 1;
            this.showIndex = this.showIndex !== targetIndex
                ? targetIndex
                : original;
        },
        toggleProfile: function () {
            return this.toggleViewIndex(0, 1);
        },
        toggleShow: function() {
            return this.toggleViewIndex(2, 1);
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
        createPasswordCallback: function (response) {
            if (response.status !== undefined) {
                vmVault.error = true;
            } else {
                vmVault.showIndex = 1;
                vmVault.loadPasswords();
            }
        },
        consumeCreateForm: function () {
            var data = {
                domainName: this.create.domainName,
                password: this.create.password,
                username: this.create.username,
                passwordGuid: '',
            };
            this.create.password = null;
            this.create.domainName = null;
            return data;
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
        loadPasswords: function () {
            return AuthSouce.service(
                '/api/v0/password/list/',
                "POST",
                {},
                this.loadPasswordCallback
            )
        },
        loadPasswordCallback: function (passwords) {
            var self = this;
            if (passwords.status !== undefined) {
                console.log(passwords);
                return;
            }
            self.setPreviousState();

            var obj = {};
            self.passwords = passwords.map(function (password) {
                password.isHovering = false;
                password.showIndex = 1;
                password.isFocused = self.previousState.activeDomain === password.domainName;
                var extAuth = {};
                password.externalauthenticationSet.map(function(ea) {
                    ea.showIndex = 0;
                    if (password.isFocused) {
                        ea.showIndex = self.previousState.authIndexes[ea.key];
                    }
                    ea.domainNameNew = password.domainName;
                    ea.userNameNew = ea.userName;
                    ea.newPassword = "";
                    extAuth[ea.key] = ea;
                });
                password.externalAuthObj = extAuth;
                obj[password.domainName] = password;
                return password;
            }).sort(function(a, b) {
                if (a.domainName < b.domainName) return -1;
                if (a.domainName > b.domainName) return 1;
                return 0;
            });
            self.objPasswords = obj;
        },
        updateProfile: function() {}
    }
});