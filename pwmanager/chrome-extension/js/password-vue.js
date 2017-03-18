var domainNameItem = Vue.component('domain-name-item', {
    template: '#domainNameItem',
    props: ["domain-name",
            "is-focused",
            "externalauthentication-set",
            "created-time",],
    computed: {
        domainObj: function () {
            return vmVault.objPasswords[this.domainName];
        },
        isFocused: {
            get: function () {
                return this.domainObj.isFocused;
            },
            set: function (value) {
                this.domainObj.isFocused = value;
            }
        },
    },
    methods: {
        setFocus: function(event) {
            var initialValue = !this.isFocused;
            if ($(event.target).is('.inert-click,span,button,input,li')) {
                initialValue = true;
            }
            vmVault.passwords.map(function(p) {
                p.isFocused = false;
            });
            this.isFocused = initialValue;
        },
    }


});

var passwordItem = Vue.component('password-item', {
    template: '#externalAuthenticationItem',
    mixins: [requestPasswordMixin, tooltipMixin],
    props: ["domain-name",
        "lookup-key",
        "user-name",
        "is-hovering",
        "passwordentity-set",
        "new-password",
        "show-index"],
    computed: {
        passwordObj: function () {
            return vmVault.objPasswords[this.domainName]
                .externalAuthObj[this.lookupKey];
        },
        viewIndex: {
            get: function() {},
            set: function (value) {
                this.$set(this.passwordObj, 'showIndex', value);
            }
        },
        showPasswordHistory: function () {
            return this.viewIndex === 2;
        },
        showUpdateForm: function () {
            return this.viewIndex === 1;
        },
        showDelete: function () {
            return this.viewIndex === 3;
        },
        userNameReadOnly: {
            get: function () {
                return this.userName;
            },
            set: function(value) {}
        },
        userNameNew: {
            get: function () {
                return this.passwordObj.userNameNew;
            },
            set: function(value) {
                this.passwordObj.userNameNew = value;
            }
        },
        passwordNew: {
            get: function () {
                return this.passwordObj.passwordNew;
            },
            set: function(value) {
                this.passwordObj.passwordNew = value;
            }
        },
        domainNameNew: {
            get: function () {
                return this.passwordObj.domainNameNew;
            },
            set: function(value) {
                this.passwordObj.domainNameNew = value;
            }
        }
    },
    methods: {
        requestCurrentPassword: function () {
            var self = this;
            return this.requestData({
                query: self.passwordentitySet[0].guid
            })
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
                    domainName: this.domainNameNew,
                    username: this.userNameNew
                },
                this.createPasswordCallback
            )
        },
        handleChange: function() {},
        handleClick: function(event) {
            $(event.target).select();
            this.viewIndex = 0;
        },
        createPasswordCallback: function (resp) {
            vmVault.createPasswordCallback(resp);
            this.viewIndex = 2;
        },
        generatePassword: function () {
            vmVault.generatePassword();
            this.$set(this.passwordObj, 'passwordNew', vmVault.create.password);
        }
    }
});


var passwordHistoryItem = Vue.component('password-history-item', {
    template: '#passwordHistoryItem',
    props: ["lookup-key",
            "created-time",],
    mixins: [requestPasswordMixin]
});