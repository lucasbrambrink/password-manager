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