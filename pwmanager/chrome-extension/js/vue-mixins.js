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