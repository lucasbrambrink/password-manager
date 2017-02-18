/**
 * Created by lb on 2/18/17.
 */
// if request password

function requestPassword() {
    //get data
    var resp = {
        success: true,
        password: 'test'
    };
    window.prompt("Copy to clipboard: Ctrl+C, Enter", resp.password);
}

var passwords = [{
    name: "Password 1",
    publicKey: "passwordId",
},{
    name: "Password 2",
    publicKey: "password2Id",
}];

var vmVault = new Vue({
    el: '#vault',
    data: {
        passwords: passwords
    },
    methods: {
        showPassword: function(password) {
            window.prompt("Copy to clipboard: Ctrl+C, Enter", password);

        },
        requestPassword: function () {
            // get nonce from server
            // get password from server using nonce
            var password = "Password123";
            this.showPassword(password);
        }
    }
});