/**
 * Created by lb on 2/18/17.
 */
(function() {

    var vmVault = new VmVault({
        el: '#vault',
        mixins: [ContentScriptApi],
        data: {
            login: {
                email: '',
                password: '',
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