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

var AuthSouce = (function($) {
    var callService = function (url, data, callback) {
        callback = callback || function () {};
        $.ajax({
            url: url,
            dataType: 'JSON',
            contentType: 'application/json; charset=utf-8',
            type: 'POST',
            data: JSON.stringify(data)
        }).done(function(response) {
            callback(response)
        }).fail(function(errResponse) {
            callback(errResponse)
        });
    };

    var requestSecondNonce = function (guid, nonce, callback) {
        var url = '/auth/' + guid;
        return callService(url, {
            guid: guid,
            nonce: nonce
        }, callback)
    };

    return {
        service: callService,
        updateNonce: requestUpdatedNonce
    };

})(jQuery);

var vmVault = new Vue({
    el: '#vault',
    data: {
        nonce: '',
        guid: '',
        error: false,
        passwords: passwords
    },
    created: function () {
        this.nonce = $('#nonce').val();
        this.guid = $('#guid').val();
    },
    methods: {
        showPassword: function(password) {
            window.prompt("Copy to clipboard: Ctrl+C, Enter", password);

        },
        requestPassword: function () {
            // get nonce from server
            this.requestNonce();
            // get password from server using nonce
            //var password = "Password123";
            //this.showPassword(password);
        },
        requestSecondNonceCallback: function (response) {
            if (response.success) {
                var first_hash = response.data.nonce;
                var second_hash = response.data.second_nonce;
                var url = '/auth/request-access';
                return AuthSouce.service(url, {
                    nonce: first_hash,
                    second_none: second_hash,
                    guid: vmVault.guid
                }, vmVault.requestDataCallback)
            } else {
                vmVault.error = true;
            }
        },
        requestDataCallback: function (response) {
            if (response.success) {
                vmVault.showPassword(response.value)
            } else {
                vmVault.error = true;
            }
        },
        requestNonce: function () {
            var url = '/auth/request-nonce';
            return AuthSouce.service(url, {
                guid: this.guid,
                nonce: this.nonce
            }, this.requestSecondNonceCallback);
        }
    }
});