/**
 * Created by lb on 2/18/17.
 */
(function() {

    var vmVault = new VmVault({
        el: '#vault',
        created: function () {
            var token = AuthSouce.csrfTokenFromHtml();
            AuthSouce.provisionToken(token);
            this.loadPasswords()
        },
        mounted: function () {
            $('form').ezFormValidation();
        }
    });

    window.vmVault = vmVault;
})();