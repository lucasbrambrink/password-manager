/**
 * Created by lb on 2/18/17.
 */
(function() {

    var vmVault = new Vue({
        el: '#vault',
        components: {passwordItem: passwordItem},
        data: {
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
                showPlaintext: false,
                length: 26,
                letters: true,
                digits: true,
                symbols: true,
            },
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
            toggleShow: function() {
                this.showIndex = this.showIndex === 1 ? 2 : 1;
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
                    password.showIndex = 2;
                    password.isFocused = false;
                    password.domainNameNew = password.domainName;
                    password.userNamenew = password.externalUniqueIdentifier;
                    obj[password.key] = password;
                    return password;
                }).sort(function(a, b) {
                    if (a.domainName < b.domainName) return -1;
                    if (a.domainName > b.domainName) return 1;
                    return 0;
                });
                vmVault.objPasswords = obj;
            }
        }
    });

    window.vmVault = vmVault;
})();