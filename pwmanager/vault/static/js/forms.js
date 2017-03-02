/**
 * Created by lb on 10/29/16.
 */
var DateUtil = (function() {
    var isDate = function (d) {
        if (Object.prototype.toString.call(d) !== "[object Date]")
            return false;
        return !isNaN(d.getTime());
    };

    var isPastOrCurrentDate = function (dateOrMonth, day, year) {
        var date = isDate(dateOrMonth)
            ? dateOrMonth
            : new Date(year, dateOrMonth - 1, day);
        return (Date.now() - date.getTime()) > 0;
    };

    var calcAge = function(dateObj) {
        var mSecDiff = new Date() - dateObj;
        var ageDays = mSecDiff / 86400000;
        var ageYears = ageDays / 365.24;
        return Math.floor(ageYears);
    };


    var validateDate = function (month, day, year, mustBeOlderThan) {
        if (month.length > 2 || day.length > 2 || year.length > 4) {
            return false;
        }
        var dateObj = new Date(year, month - 1, day);
        if ((dateObj.getMonth() + 1 != month) ||
            (dateObj.getDate() != day) ||
            (dateObj.getFullYear() != year)) {
            return false;
        } else if (!isPastOrCurrentDate(dateObj)) {
            return false;
        }
        // valid
        if (typeof mustBeOlderThan === 'number') {
            return mustBeOlderThan > calcAge(dateObj);
        }
        return true;
    };


    var validateDateString = function (date, mustBeOlderThan) {
        var dateArr = date.replace(/\s/g, '').split("/");
        if (dateArr.length !== 3) return false;
        else return validateDate(dateArr[0], dateArr[1], dateArr[2], mustBeOlderThan);
    };

    return {
        validateDateString: validateDateString,
        validateDate: validateDate,
        isDate: isDate,
        calcAge: calcAge,
        isPastOrCurrentDate: isPastOrCurrentDate
    }
})();

var VALIDATORS = {
    required: {
        fn: function(value) {
            if (typeof value === 'undefined' || value === null) {
                return false;
            }
            return value.length > 0;
        },
        message: 'This value is required.'
    },
    digits: {
        fn: function(value) {
            return !isNaN(value);
        },
        message: 'This value must contain numbers only.'
    },
    phoneNumber: {
        fn: function (value) {
            if (Utils.stringIsNullOrEmpty(value)) return false;
            var re = new RegExp('/[-()+.]\s/');
            var stripped = value.replace(re, '');
            return !isNaN(stripped) && stripped.length >= 10;
        },
        message: 'This value should be a phone number.',
    },
    email: {
        fn: function (value) {
            if (Utils.stringIsNullOrEmpty(value)) return false;
            var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            return re.test(value);
        },
        message: 'Please enter a valid email.',
    },
    creditcard: {
        fn: function (value) {
            return /[\d]{15,19}/.test(ccString.replace(/ /g, '').replace(/-/g,''));
        },
        message: 'Please enter a valid credit card number.',
    },
    cvv: {
        fn: function (value) {
            return /[\d]{3,4}/.test(cvvString);
        },
        message: 'Please enter a valid code.',
    },
    zipcode: {
        fn: function (value) {
            return /^\d{5}(-\d{4})?$/.test(value);
        },
        message: 'Please enter a valid zip code.',
    },
    date: {
        fn: function (value) {
            return DateUtil.validateDateString(value);
        },
        message: 'Please enter a valid date (MM/DD/YYYY).',
    },
    mustBeOlderThan: {
        fn: function (value, mustBeOlderThan) {
            return DateUtil.validateDateString(value, mustBeOlderThan);
        },
        message: 'Please confirm your age.',
    },
    name: {
        fn: function (value) {
            var validName = new RegExp("^[a-zA-Z-' ]+$");
            return validName.test(value);
        },
        message: 'Names may only contain letters, dashes or apostrophes.',
    },
    matches: {
        fn: function(value, matches) {
            if (Utils.stringIsNullOrEmpty(value)) return false;
            return value === $(matches).val();
        },
        message: 'This value must match'
    }
    // password
};

var Utils = (function($) {
    var STATES = {
        VALID: 'valid',
        INVALID: 'invalid',
        DISABLED: 'disabled'
    };
    var DATA = {
        VALIDATE: 'validate',
        ERROR_MESSAGE: 'error-message',
        OLDER_THAN: 'older-than',
        MATCH_TO: 'match-to',
        NEVER_DISABLED: 'never-disabled'
    };
    var ERROR_LABEL = 'label.error';

    var stringIsNullOrEmpty = function(value) {
        if (typeof value === 'undefined' || value === null) {
            return false;
        }
        return value.trim().length === 0;
    };

    var setDisabled = function(selector, isDisabled) {
        var $el = $(selector);
        var disabledAttr = $el.attr(STATES.DISABLED);
        if (isDisabled && disabledAttr === undefined) {
            $el.attr(STATES.DISABLED, STATES.DISABLED);
        } else if (!isDisabled && disabledAttr === STATES.DISABLED) {
            $el.removeAttr(STATES.DISABLED);
        }
    };

    var setState = function(selector, isValid) {
        isValid
            ? $(selector)
                .removeClass(STATES.INVALID)
                .addClass(STATES.VALID)
            : $(selector)
                .removeClass(STATES.VALID)
                .addClass(STATES.INVALID);
    };

    var setNeutral = function (selector) {
        selector = selector || this;
        $(selector)
            .removeClass(STATES.VALID)
            .removeClass(STATES.INVALID)
            .siblings(ERROR_LABEL).remove();
    };

    var setInvalid = function (selector, msg) {
        var $element = $(selector);
        var $label = $element.siblings(ERROR_LABEL);
        if ($label.length === 0) {
            $label = $('<label class="error"></label>');
            $element.after($label);
        }
        var message = $element.data(DATA.ERROR_MESSAGE) || msg;
        $label.text(message);
        $element
            .removeClass(STATES.VALID)
            .addClass(STATES.INVALID);
    };

    var setValid = function(selector) {
        setNeutral(selector);
        $(selector).addClass(STATES.VALID);
    };

    var setSubmittable = function(form, isValid) {
        var $submit = $(form).find('[type=submit]');
        setDisabled($submit, !isValid);
    };

    return {
        STATES: STATES,
        DATA: DATA,
        VALIDATORS: VALIDATORS,
        DateUtil: DateUtil,
        stringIsNullOrEmpty: stringIsNullOrEmpty,
        setDisabled: setDisabled,
        setState: setState,
        setValid: setValid,
        setInvalid: setInvalid,
        setNeutral: setNeutral,
        setSubmittable: setSubmittable
    }

})(jQuery);

/*
    Easy Form validation
*/

var EzForms = (function ($) {
    var STATES = Utils.STATES;
    var DATA = Utils.DATA;

    var validateInput = function (element, dispatchSuccessOnly) {
        var $element = $(element);
        var validateOver = $element.data(DATA.VALIDATE);
        if (typeof validateOver === 'undefined') return;

        var value = $element.val();
        var keys = validateOver.split(",");

        var validator, key, isValid;
        for (var i = 0; i < keys.length; i++) {
            key = keys[i].trim();
            validator = Utils.VALIDATORS[key];
            if (typeof validator === 'undefined' || validator === null) continue;

            switch (key) {
                case 'mustBeOlderThan':
                    isValid = validator.fn(value, $element.data(DATA.OLDER_THAN));
                    break;
                case 'matches':
                    isValid = validator.fn(value, $element.data(DATA.MATCH_TO));
                    break;
                default:
                    isValid = validator.fn(value);
                    break;
            }
            if (!isValid) break;
        }
        if (dispatchSuccessOnly && !isValid) {
            return;
        }

        isValid ? Utils.setValid(element)
                : Utils.setInvalid(element, validator.message);
    };

    var formIsValid = function (form) {
        $(form)
            .find('[data-validate]')
            .map(function() {
                validateInput(this, true);
            });
        var formIsValid = $(form).find('.' + STATES.INVALID).length === 0;
        Utils.setState(form, formIsValid);
        return formIsValid;
    };

    var formIsComplete = function (form) {
        var requiredInputs = $(form)
            .find('[data-validate]')
            .filter(function() {
                return $(this).data('validate').indexOf('required') > -1;
            });
        for (var i = 0; i < requiredInputs.length; i++) {
            if (Utils.stringIsNullOrEmpty($(requiredInputs[i]).val())) {
                return false;
            }
        }
        return true;
    };

    var setSubmittable = function() {
        var isValid = formIsComplete(this) && formIsValid(this);
        Utils.setSubmittable(this, isValid);
    };

    var init = function (form) {
        var $form = $(form);
        $form
            .find('[data-validate]')
            .on('blur', function() {
                validateInput(this);
            })
            .on('keyup', function() {
                validateInput(this, true);
            });

        if ($form.data(DATA.NEVER_DISABLED) !== 'true') {
            $form
                .ready(setSubmittable)
                .on('focus keyup change', setSubmittable)
        }
        $form
            .on('submit',
                function(event) {
                    if (!formIsValid(form)) {
                        event.preventDefault();
                    }
                });

    };

    var setFormNeutral = function (form) {
        $('form')
            .find('[data-validate]')
            .each(function () {
                Utils.setNeutral(this);
            });
    };

    var initAll = function(selector) {
        $(selector)
            .map(function() {
                init(this);
            });
    };

    return {
        VALIDATORS: VALIDATORS,
        STATES: STATES,
        validateInput: validateInput,
        formIsValid: formIsValid,
        setFormNeutral: setFormNeutral,
        init: init,
        initAll: initAll
    }
})(jQuery);

(function($) {
    $.fn.extend({
        ezFormValidation: function () {
            EzForms.init(this);
        },
        setFormNeutral: function() {
            EzForms.setFormNeutral(this);
        }
    });
    $('form').ezFormValidation();
})(jQuery);