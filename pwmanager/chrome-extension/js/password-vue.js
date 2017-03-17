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
        viewIndex: {
            get: function () {
                return this.passwordObj.showIndex;
            },
            set: function (value) {
                this.passwordObj.showIndex = value;
                if (value === 0)
                    this.isFocused = true;
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
            if (this.isFocused) {
                this.isFocused = false;
            }
            return this.requestData({
                query: this.passwordEntities[0].guid
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
        setFocus: function(event) {
            var initialValue = !this.isFocused;
            if ($(event.target).is('span, button')) {
                initialValue = true;
            }
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