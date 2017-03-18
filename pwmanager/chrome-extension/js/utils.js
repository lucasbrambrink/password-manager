var GeneratePassword = (function () {


    var rchoose = function (array) {
        return array[Math.floor(Math.random() * array.length)];
    };

    var generatePassword = function (length, withLetters, withDigits, withSymbols) {
        var lowercase = 'abcdefghijklmnopqrstuvwxyz';
        var upppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        var numbers = '1234567890';
        var symbols = '!@#$%^&*+=?';
        var choices = [];
        if (withLetters) {
            choices.push(lowercase);
            choices.push(upppercase);
        }
        if (withDigits) {
            choices.push(numbers);
        }
        if (withSymbols) {
            choices.push(symbols);
        }

        var password = [],
            category;
        for (var x = 0; x < length; x++) {
            category = rchoose(choices);
            password.push(rchoose(category));
        }

        return password.join('');
    };

    return {
        generate: generatePassword
    };
})();