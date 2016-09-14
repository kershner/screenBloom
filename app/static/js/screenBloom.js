var screenBloom = {};

screenBloom.config = {
    'briUrl'            : '',
    'updateSpeedUrl'    : '',
    'defaultColorUrl'   : '',
    'partyModeUrl'      : '',
    'autoStartUrl'      : '',
    'regenConfigUrl'    : '',
    'zoneUrl'           : '',
    'bulbsUrl'          : '',
    'displayUrl'        : '',
    'defaultColor'      : '',
    'blackRgb'          : '',
    'lightsNumber'      : '',
    'state'             : '',
    'autoStartState'    : '',
    'colors'            : [],
    'bulbs'             : []
};

screenBloom.init = function() {
    updateCheck();

    ipHelp();
    clickRegister();

    callBloomColor();
    callHelloColor();
    callColorSettings();
    settingCircleEvents();

    settingsBtns();
    displaySelect();
    bulbSelect();
    startStopBtns();
    updateSettings();
    regenConfig();
    presets();

    colorPicker();
    lightsOnOff();
    sliderUpdate();

    goldBloom();

    for (var i=0; i<64; i++) {
        screenBloom.config.colors.push(randomColor());
    }

    Tipped.create('.simple-tooltip', {
        maxWidth    : 200
    });
};

function presets() {
    var icon = $('#settings-preset-icon');
    icon.on('click', function() {
       console.log('Halaldfasa');
    });
}

function activeBulbsCheck() {
    var allBulbsInactive = true;

    for (var i in screenBloom.config.bulbs) {
        var bulb = parseInt(screenBloom.config.bulbs[i]);
        if (bulb > 0) {
            allBulbsInactive = false;
        }
    }

    if (allBulbsInactive) {
        notification('No bulbs currently selected for ScreenBloom to address.');
        notification('Click on a bulb icon to enable it, then click "Update Bulbs" when ready.');
    }

    return allBulbsInactive;
}

function autoStart() {
    var btn = $('.auto-start-btn'),
        startBtn = $('#start'),
        inputText = startBtn.find('.setting-input-text'),
        state = screenBloom.config.state,
        autoStartState = btn.data('state'),
        color = randomColor();

    if (!state && autoStartState > 0) {
        if (!activeBulbsCheck()) {
            notification('Auto Start enabled!');
            inputText.addClass('hidden');
            screenBloom.config.state = true;
            $.getJSON($SCRIPT_ROOT + '/start', function (data) {
                notification(data.message);
                inputText.removeClass('hidden');
            });
            startBtn.addClass('button-selected');
            startBtn.css({
                'background-color': color,
                'border': '2px solid ' + color,
                'text-shadow': '1px 1px 3px rgba(0, 0, 0, 0.3)'
            });
            inputText.text('Running...');
        }
    }

    // Click event
    btn.on('click', function() {
        var autoRunState = $(this).data('state');

        if (autoRunState === 1) {
            $(this).data('state', 0);
            $(this).removeClass('activated');
        } else if (autoRunState === 0) {
            $(this).data('state', 1);
            $(this).addClass('activated');
        }

        $.ajax({
            url         : screenBloom.config.autoStartUrl,
            method      : 'POST',
            contentType : 'application/json;charset=UTF-8',
            data        : JSON.stringify(autoRunState),
            success     : function (result) {
                notification(result.message);
            },
            error       : function (result) {
                console.log(result);
            }
        });
    });
}

function regenConfig() {
    $('.regen-config').on('click', function() {
        var wrapper = $('.regen-config-confirm-wrapper'),
            container = $('.regen-config-confirm');
        wrapper.removeClass('hidden');

        $('#regen-cancel').on('click', function() {
            wrapper.addClass('hidden');
        });

        $('#regen-confirm').on('click', function() {
            $.ajax({
                url         : screenBloom.config.regenConfigUrl,
                method      : 'POST',
                contentType : 'application/json;charset=UTF-8',
                success     : function (result) {
                    notification(result.message);
                    if (result.success) {
                        var html = '<p>Success!  Your config file was removed.  Visit the registration page to create a new file.</p><a href="/new-user">ScreenBloom Registration</a>';
                        container.empty().append(html);
                    }
                },
                error       : function (result) {
                    console.log(result);
                }
            });
        });
    });
}

function settingsBtns() {
    $('.setting').on('click', function (e) {
        var inputContainer = $(this).find('.setting-input'),
            target = $(e.target),
            settingCircle = $(this).find('.setting-circle');

        if ($(this).hasClass('party-mode-btn')) {
            var partyModeInput = $(this).find('input');

            settingCircle.toggleClass('setting-clicked');
            if (settingCircle.hasClass('setting-clicked')) {
                settingCircle.addClass('party-on');
                partyModeInput.val(1);
                settingCircle.find('span').text('On');
                togglePartyMode(1);
                colorSettingCircle(settingCircle);
            } else {
                settingCircle.removeClass('party-on');
                partyModeInput.val(0);
                settingCircle.find('span').text('Off');
                togglePartyMode(0);
                deColorSettingCircle(settingCircle);
            }
        } else {
            if (target.hasClass('setting-input') || target.hasClass('slider') || target.hasClass('slider-max') || target.hasClass('picker')) {
                // Do nothing if clicking inside input
            } else if (target.hasClass('setting-input-close')) {
                var defaultColorCircle = settingCircle.hasClass('default-color-circle');
                $(this).find('.setting-circle').toggleClass('setting-clicked');
                inputContainer.toggleClass('hidden');
                if (!defaultColorCircle) {
                    deColorSettingCircle(settingCircle);
                }
            } else {
                $('.setting-input').addClass('hidden');
                $('.setting-circle').removeClass('setting-clicked');
                $(this).find('.setting-circle').toggleClass('setting-clicked');
                inputContainer.toggleClass('hidden');
            }
        }
    });

    $('.black-color-choice').on('click', function() {
        $('.black-color-selection-indicator').remove();
        $(this).append('<div class="black-color-selection-indicator"></div>');
    });
}

function togglePartyMode(partyMode) {
    var btn = $('.party-mode-btn'),
        loadingIcon = btn.find('.loader'),
        inputText = btn.find('.setting-input-text');

    inputText.addClass('hidden');
    loadingIcon.removeClass('hidden');
    btn.find('.setting-circle').addClass('button-selected');

    $.ajax({
        url: screenBloom.config.partyModeUrl,
        method: 'POST',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify(partyMode),
        success: function (result) {
            notification(result.message);
            inputText.removeClass('hidden');
            loadingIcon.addClass('hidden');
            btn.find('.setting-circle').removeClass('button-selected');
        },
        error: function (result) {
            console.log(result);
            inputText.removeClass('hidden');
            loadingIcon.addClass('hidden');
            btn.find('.setting-circle').removeClass('button-selected');
        }
    });
}

function bulbSelect() {
    // Toggle class for bulbs on click
    $('.bulb-container').on('click', function () {
        $(this).toggleClass('bulb-inactive');
        $('.update-bulbs').removeClass('hidden');
    });

    // Create active bulbs string from .bulb-container CSS class, send to server to be written
    $('.update-bulbs').on('click', function () {
        var bulbs = [],
            loadingIcon = $(this).find('.loader'),
            inputText = $(this).find('.setting-input-text'),
            that = $(this);

        inputText.addClass('hidden');
        loadingIcon.removeClass('hidden');
        that.addClass('button-selected');

        $('.bulb-container').each(function () {
            if ($(this).hasClass('bulb-inactive')) {
                bulbs.push(0);
            } else {
                bulbs.push($(this).data('light'));
            }
        });
        $.ajax({
            url: screenBloom.config.bulbsUrl,
            method: 'POST',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify(bulbs.toString()),
            success: function (result) {
                screenBloom.config.bulbs = result.bulbs.split(',');
                notification(result.message);
                $('.update-bulbs').addClass('hidden');
                inputText.removeClass('hidden');
                loadingIcon.addClass('hidden');
                that.removeClass('button-selected');
                updateGridLights();
                buildGrid();
            },
            error: function (result) {
                console.log(result);
                inputText.removeClass('hidden');
                loadingIcon.addClass('hidden');
                that.removeClass('button-selected');
            }
        });
    });
}

function startStopBtns() {
    var startBtn = $('#start'),
        stopBtn = $('#stop');

    startBtn.on('click', function () {
        var color = randomColor(),
            inputText = $(this).find('.setting-input-text');

        if (!screenBloom.config.state && activeBulbsCheck() === false) {
            inputText.addClass('hidden');
            screenBloom.config.state = true;
            $.getJSON($SCRIPT_ROOT + '/start', function (data) {
                notification(data.message);
                inputText.removeClass('hidden');
            });
            startBtn.addClass('button-selected');
            startBtn.css({
                'background-color': color,
                'border': '2px solid ' + color,
                'text-shadow': '1px 1px 3px rgba(0, 0, 0, 0.3)'
            });
            inputText.text('Running...');
            activeBulbsCheck();
        }
    });

    stopBtn.on('click', function () {
        var loadingIcon = $(this).find('.loader'),
            inputText = $(this).find('.setting-input-text'),
            startText = startBtn.find('.setting-input-text');

        loadingIcon.removeClass('hidden');
        inputText.addClass('hidden');

        $.getJSON($SCRIPT_ROOT + '/stop', function (data) {
            notification(data.message);
            inputText.removeClass('hidden');
            loadingIcon.addClass('hidden');
        });
        screenBloom.config.state = false;
        startBtn.removeClass('button-selected');
        startBtn.css({
            'background-color': '#F2F2F2',
            'border': '2px solid #007AA3',
            'color': '#007AA3',
            'text-shadow': 'none'
        });
        startText.text('Start');
    });
}

// Updates setting slider to currently selected value
function sliderUpdate() {
    var sliders = ['#bri', '#max-bri', '#min-bri', '#update-speed', '#update-buffer'],
        maxBriSlider = $('#max-bri-slider'),
        minBriSlider = $('#min-bri-slider');

    for (var i = 0; i < sliders.length; i++) {
        $(sliders[i] + '-slider').on('input', function () {
            var id = $(this).attr('id'),
                value = $(this).val(),
                outputId = ('#' + id + '-output'),
                maxBri = maxBriSlider.val(),
                minBri = minBriSlider.val();

            maxBriSlider.attr('min', minBri);
            minBriSlider.attr('max', maxBri);
            $(outputId).html(value);
        });
    }
}

function lightsOnOff() {
    var state = $('#on-state').text(),
        stateVar = '';

    $('#on-off').on('click', function () {
        var loadingIcon = $(this).find('.loader'),
            inputText = $(this).find('.setting-input-text');

        loadingIcon.removeClass('hidden');
        inputText.addClass('hidden');
        if (state === 'On') {
            state = 'Off';
            stateVar = 'On';
        } else {
            state = 'On';
            stateVar = 'Off';
        }
        $('#on-state').text(state);
        $.getJSON($SCRIPT_ROOT + '/on-off', {
            state: stateVar
        }, function (data) {
            notification(data['message']);
            loadingIcon.addClass('hidden');
            inputText.removeClass('hidden');
        });
        return false
    });
}

function displaySelect() {
    $('.display-icon').on('click', function() {
        $('.display-icon-selected').remove();
        $(this).append('<div class="display-icon-selected">Selected</div>');
    });
}

function updateSettings() {
    $('.setting-input-submit').on('click', function () {
        var url = $(this).data('url'),
            value = $(this).siblings('input').val(),
            settingContainer = $(this).parents('.setting'),
            valueDiv = settingContainer.find('.setting-value'),
            loadingIcon = $(this).find('.loader'),
            inputText = $(this).find('.setting-input-text'),
            that = $(this);

        inputText.addClass('hidden');
        loadingIcon.removeClass('hidden');
        that.addClass('button-selected');

        if (url === 'defaultColorUrl') {
            value = $('.colpick_hex_field input').val();
            valueDiv = undefined;
        } else if (url === 'briUrl') {
            var max = $('#max-bri-slider').val(),
                min = $('#min-bri-slider').val(),
                blackRgb = '0,0,0';

            $('.black-color-choice').each(function() {
                var indicator = $(this).find('.black-color-selection-indicator');
                if (indicator.length) {
                    blackRgb = $(this).data('rgb');
                }
            });
            value = [max, min, blackRgb];
        } else if (url === 'zoneUrl') {
            console.log('zone mode cliqued');
        } else if (url === 'updateSpeedUrl') {
            value = {
                'transition': $('#update-speed-slider').val(),
                'buffer'    : $('#update-buffer-slider').val()
            };
        } else if (url === 'displayUrl') {
            value = $('.display-icon-selected').parent().data('index');
        }

        $.ajax({
            url: screenBloom.config[url],
            method: 'POST',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify(value),
            success: function (result) {
                notification(result.message);
                if (url === 'defaultColorUrl') {
                    settingContainer.find('.setting-circle').css('background-color', '#' + value);
                } else if (url === 'briUrl') {
                    $('#circle-max').text(result['max_bri']);
                    $('#circle-min').text(result['min_bri']);
                } else if (url === 'displayUrl') {
                    $('.setting-img').attr('src', 'data:image/png;base64,' + result.img);
                } else {
                    valueDiv.text(result.value);
                }
                $('.setting-input').addClass('hidden');
                $('.setting-circle').each(function() {
                    var defaultColorCircle = $(this).hasClass('default-color-circle'),
                        partyModeCircle = $(this).hasClass('party-mode-circle');
                    if (!defaultColorCircle && !partyModeCircle) {
                        deColorSettingCircle($(this));
                    }
                    $(this).removeClass('setting-clicked');
                });
                inputText.removeClass('hidden');
                loadingIcon.addClass('hidden');
                that.removeClass('button-selected');
            },
            error: function (result) {
                console.log(result);
                inputText.removeClass('hidden');
                loadingIcon.addClass('hidden');
                that.removeClass('button-selected');
            }
        });
    });
}

function notification(text) {
    var notification = $('<div id="notification"></div>');
    notification.text(text);
    $('.notification-sidebar').append(notification);
    setTimeout(function () {
        notification.animate({
            'opacity': 0.0
        }, 800, function () {
            setTimeout(function () {
                notification.remove();
            }, 100);
        });
    }, 3000);
}

//= Front end stuff ===============================================================================
// Apply random color to ScreenBloom logos
function callBloomColor() {
    bloomColor();
    setInterval(bloomColor, 4000);
}

function bloomColor() {
    var color = randomColor();
    $('.bloom').css({
        'color': color
    });
}

// Functions to color the settings titles
function callColorSettings() {
    colorSettings();
    setInterval(colorSettings, 4000);
}

function colorSettings() {
    var elements = [
        '#settings-title',
        '#bulbs-title',
        '#update-speed-title',
        '#default-color-title',
        '#party-mode-title'
    ];
    for (var i=0; i<elements.length; i++) {
        var color = randomColor();
        $(elements[i]).css({
            'color': color
        }, 2000);
    }
}

// UI Color Stuff
function settingCircleEvents() {
    $('.setting-circle').on({
        mouseenter: function () {
            var defaultColorCircle = $(this).hasClass('default-color-circle');
            if (defaultColorCircle) {
                colorSettingCircleBorder($(this));
            } else {
                colorSettingCircle($(this));
            }
        },
        mouseleave: function () {
            var defaultColorCircle = $(this).hasClass('default-color-circle'),
                settingClicked = $(this).hasClass('setting-clicked'),
                partyModeCircleOn = $(this).hasClass('party-on');
            if (defaultColorCircle) {
                deColorSettingCircleBorder($(this));
            } else if (!settingClicked && !partyModeCircleOn) {
                deColorSettingCircle($(this));
            }
        },
        click: function () {
            var defaultColorCircle = $(this).hasClass('default-color-circle'),
                inputLabel = $(this).siblings('.setting-input').find('.setting-input-label').find('div');
            if (!defaultColorCircle) {
                addSettingSelectedColor($(this));
            }
            inputLabel.colorWave(screenBloom.config.colors);
        }
    });
}

function addSettingSelectedColor(circle) {
    $('.setting-clicked').each(function () {
        var defaultColorCircle = $(this).hasClass('default-color-circle'),
            partyModeCircle = $(this).hasClass('party-mode-circle');
        if (!defaultColorCircle && !partyModeCircle) {
            deColorSettingCircle($(this));
        }
    });
    colorSettingCircle(circle);
}

function colorSettingCircle(circle) {
    var color = randomColor();
    circle.css({
        'background-color': color,
        'border-color': color,
        'color': 'white',
        'text-shadow': '0 1px 1px rgba(0, 0, 0, 0.46)'
    });
}

function colorSettingCircleBorder(circle) {
    var color = randomColor();
    circle.css({
        'border-color': color
    });
}

function deColorSettingCircle(circle) {
    circle.css({
        'background-color': '#F2F2F2',
        'border-color': '#007AA3',
        'color': '#007AA3',
        'text-shadow': 'none'
    });
}

function deColorSettingCircleBorder(circle) {
    circle.css({
        'border-color': '#007AA3'
    });
}

// My colorWave code
// http://codepen.io/kershner/pen/Yyyzjz
(function ($) {
    $.fn.colorWave = function (colors) {
        function _colorWave(colors, element) {
            var finalHtml = '',
                text = $(element).text(),
                defaultColor = $(element).css('color'),
                wait = text.length * 350,
                tempHtml = '';

            // Placing <spans> around each letter with class="colorwave"
            for (var i = 0; i < text.length; i++) {
                tempHtml = '<span class="colorwave" style="position: relative;">' + text[i] + '</span>';
                finalHtml += tempHtml;
            }
            $(element).empty().append(finalHtml);
            _colorLetters(colors, element, wait, defaultColor);
        }

        // Iterates through given color array, applies color to a colorwave span
        function _colorLetters(colors, element, wait, defaultColor) {
            var counter = (Math.random() * (colors.length + 1)) << 0,
                delay = 100,
                adjustedWait = wait / 5;
            $(element).find('.colorwave').each(function () {
                if (counter >= colors.length) {
                    counter = 0;
                }
                $(this).animate({
                    'color': colors[counter],
                    'bottom': '+=6px'
                }, delay);
                delay += 75;
                counter += 1;
            });
            setTimeout(function () {
                _removeColor(element, defaultColor);
            }, adjustedWait);
        }

        // Iterates through color wave spans, returns each to default color
        function _removeColor(element, defaultColor) {
            var delay = 100;
            $(element).find('.colorwave').each(function () {
                $(this).animate({
                    'color': defaultColor,
                    'bottom': '-=6px'
                }, delay);
                delay += 75;
            });
        }

        return this.each(function () {
            _colorWave(colors, this);
        });
    }
}(jQuery));

//= Utility =======================================================================================
function randomNumber(min, max) {
    return Math.floor(Math.random() * (max - min)) + min
}

function colorPicker() {
    $('#picker').colpick({
        flat    : true,
        layout  : 'hex',
        submit  : 0,
        color   : {
            r: screenBloom.config.defaultColor[0],
            g: screenBloom.config.defaultColor[1],
            b: screenBloom.config.defaultColor[2]
        }
    });
}

function updateCheck() {
    var version = $('.version').data('version');

    $.ajax({
        url: 'http://www.screenbloom.com/version-check',
        method: 'POST',
        data: JSON.stringify(version),
        contentType: 'application/json',
        success: function (result) {
            var message = result['message'];
            if (message) {
                notification(result['message']);
                notification('Visit screenbloom.com to download');
            }
        },
        error: function (result) {
            console.log(result);
        }
    });
}

//= Stupid ========================================================================================
function goldBloom() {
    var clicked = false,
        img = $('#secret-goldblum img'),
        headerContainer = $('#header-container');

    $('#secret-goldblum').on('click', function () {
        if (clicked) {
            clicked = false;
            console.log('Goodbye, Jeff!');
            $(this).css({
                'height'    : '1em',
                'opacity'   : '0.0'
            });
            img.css({
                'top': '-5.75em'
            });
        } else {
            clicked = true;
            console.log('GoldBloom!');
            $(this).css({
                'height'    : '14em',
                'opacity'   : '1.0'
            });
            img.css({
                'top': '0'
            });
            $('#goldbloom-trigger').on('click', function () {
                console.log('TRIGGERED');
                var randomNumber1 = randomNumber(1, 7),
                    randomNumber2 = randomNumber(1, 7);
                if (randomNumber2 === randomNumber1) {
                    randomNumber2 = randomNumber(1, 7);
                }
                var imageUrl = 'goldblum';
                headerContainer.css('min-width', '68vh');
                var html = '<img src="' + imageUrl + randomNumber1 + '.jpg" class="goldblum fa-spin"><h1 class="header-title raleway goldblum-text">Gold</h1><h1 class="header-title lobster goldblum-text"><span class="bloom color-animate">Bloom</span></h1><img src="' + imageUrl + randomNumber2 + '.jpg" class="goldblum fa-spin">';
                headerContainer.empty().append(html);
            });
        }
    });
}

//= Registration Functions ========================================================================
// Function to color letters of giant 'HELLO' greeting
function callHelloColor() {
    helloColor();
    setInterval(helloColor, 4000);
}

function helloColor() {
    var elements = ['#h', '#e', '#l-1', '#l-2', '#o', '#exclaim'];
    for (var i = 0; i < elements.length; i++) {
        var color = randomColor();
        $(elements[i]).css({
            'color': color
        }, 2000);
    }
}

// Colors the loading spinner
function colorLoading() {
    var color = randomColor();
    $('#loading').css({
        'color': color
    }, 2000);
    $('.result-type > h1').css({
        'color': color
    }, 2000);
}

// Display a tooltip with information on where to find Bridge IP
function ipHelp() {
    $('#ip-info').on('click', function () {
        $('#ip-tooltip').fadeIn('fast');
    });

    $('#ip-tooltip-close').on('click', function () {
        $('#ip-tooltip').fadeOut('fast');
    });
}

// Handles AJAX call to register new username and displays error/success message
function clickRegister() {
    $('#register').on('click', function () {
        var wrapper = $('.result-wrapper'),
            loadingIcon = '<i id="loading" class="fa fa-spinner fa-spin"></i>',
            script = '<script type="text/javascript">colorLoading();</script>',
            hue_ip = $('#hue-ip').val();

        wrapper.empty();
        wrapper.append(loadingIcon);
        wrapper.append(script);

        wrapper.fadeIn('fast');
        $.getJSON($SCRIPT_ROOT + '/register', {
            hue_ip: hue_ip
        }, function (data) {
            if (data['success'] === true) {
                console.log(data);
                var html = '<div class="result-type"><h1 class="raleway animate">Success!</h1>' +
                    '<span>ScreenBloom was registered with your Hue Bridge.</span>' +
                    '<span>Click the link below to continue!</span><a class="animate" href="/">Continue</a>' +
                    '<script type="text/javascript">colorLoading();</script>';
                wrapper.append(html);
            } else if (data['error_type'] === 'manual') {
                console.log('Redirecting to manual IP entry...');
                window.location.href = '/manual';
            } else {
                console.log('An error occurred!');
                wrapper.append(getRegisterErrorHtml(data['error_type'], data['error_description']));
                $('#try-again').on('click', function () {
                    wrapper.fadeOut('fast');
                });
            }
        });
    });
}

function getRegisterErrorHtml(error, description) {
    var text = 'An error occurred, please try again.<br>Error Text: ' + description;
    if (error === '101') {
        text = 'Looks like the Bridge\'s link button wasn\'t pressed first.';
    }
    return '<div class="result-type"><h1 class="raleway animate">Whoops!</h1><span>' + text + '</span>' +
        '<div id="try-again" class="animate">Try Again</div><script type="text/javascript">colorLoading();</script>';
}