var screenBloomPresets = {};

screenBloomPresets.init = function() {
    var wrapper = $('.presets-wrapper'),
        icon = wrapper.find('#settings-preset-icon'),
        inputWrapper = wrapper.find('.setting-input'),
        saveNewPresetBtn = $('#save-preset'),
        closeBtn = wrapper.find('.setting-input-close'),
        preset = $('.saved-preset'),
        savedPresetContainer = $('#saved-preset-container'),
        iconSelect = '.saved-preset .edit-preset-container .black-color-container .select-preset-icon-container .preset-icon-select',
        deletePresetBtn = '.saved-preset .edit-preset-container .delete-preset',
        savePresetBtn = '.saved-preset .edit-preset-container .save-preset',
        closeEditContainer = '.saved-preset .black-color-container .close-edit-preset-container';

    preset.each(function() {
        $(this).css({
           'border-color': randomColor({'luminosity' : 'dark'})
        });
    });

    // Events
    icon.on('click', function() {
        icon.toggleClass('active');
        inputWrapper.toggleClass('hidden');
        if (icon.hasClass('active')) {
            inputWrapper.find('.setting-input-label div').colorWave(screenBloom.config.colors);
        }
    });

    closeBtn.on('click', function() {
        inputWrapper.addClass('hidden');
        icon.removeClass('active');
    });

    // Edit preset button
    savedPresetContainer.on('click', '.saved-preset .edit-preset', function() {
        $('.edit-preset-container').addClass('hidden');
        $('.saved-preset .edit-preset').removeClass('active');
        $(this).parent().find('.edit-preset-container').removeClass('hidden');
        $(this).addClass('active');

        $('.saved-preset').each(function() {
            $(this).removeClass('active');
            var presetName = $(this).find('.preset-label').text();
            if (presetName === screenBloom.config.currentPreset) {
                $(this).addClass('active');
            }
        });

        $(this).parents('.saved-preset').addClass('active');
    });

    savedPresetContainer.on('click', closeEditContainer, function() {
        var parent = $(this).parents('.saved-preset'),
            container = parent.find('.edit-preset-container'),
            presetName = parent.find('.preset-label').text();

        if (presetName !== screenBloom.config.currentPreset) {
            parent.removeClass('active');
        }

        container.addClass('hidden');
    });

    savedPresetContainer.on('click', '.saved-preset', function(e) {
        var presetNumber = $(this).data('preset-number'),
            target = $(e.target),
            wrapper = $(this).find('.saved-preset-wrapper'),
            loader = $(this).find('.preset-loading');

        if (target.hasClass('preset-icon') || target.hasClass('saved-preset') || target.hasClass('preset-label')) {
            console.log('Applying preset...');
            $('.saved-preset').removeClass('active');
            $(this).addClass('active');
            wrapper.addClass('hidden');
            loader.removeClass('hidden');
            $.ajax({
                url         : '/apply-preset',
                method      : 'POST',
                data        : JSON.stringify(presetNumber),
                contentType : 'application/json;charset=UTF-8',
                success     : function (result) {
                    notification(result.message);
                    notification('Reloading the page...');
                    location.reload();
                },
                error       : function (result) {
                    console.log(result);
                    wrapper.removeClass('hidden');
                    loader.addClass('hidden');
                }
            });
        }
    });

    saveNewPresetBtn.on('click', function() {
        $.ajax({
            url         : '/save-preset',
            method      : 'POST',
            contentType : 'application/json;charset=UTF-8',
            success     : function (result) {
                var clone = $('#base-saved-preset').clone(),
                    presetName = 'Preset ' + result.preset_number,
                    icon = clone.find('.preset-icon');

                screenBloom.config.currentPreset = presetName;
                $('.saved-preset').removeClass('active');
                clone.removeAttr('id');
                clone.addClass('active');
                clone.css({
                    'border-color'  : randomColor(),
                    'display'       : 'inline-block'
                });
                clone.attr('data-preset-number', result.preset_number);
                clone.find('p').text(presetName);
                clone.find('input').val(presetName);
                icon.removeClass().addClass('fa ' + result.icon_class + ' preset-icon');
                savedPresetContainer.append(clone);
                clone.find('.preset-icon-select').each(function() {
                    var icon = $(this).find('i');
                    $(this).removeClass('active');
                    if (icon.hasClass(result.icon_class)) {
                        $(this).addClass('active');
                    }
                });
                notification(result.message);
            },
            error       : function (result) {
                console.log(result);
            }
        });
    });

    savedPresetContainer.on('click', deletePresetBtn, function() {
        var presetNumber = $(this).parents('.saved-preset').data('preset-number'),
            presetDiv = $(this).parents('.saved-preset');
        $.ajax({
            url         : '/delete-preset',
            method      : 'POST',
            data        : JSON.stringify(presetNumber),
            contentType : 'application/json;charset=UTF-8',
            success     : function (result) {
                notification(result.message);
                presetDiv.remove();
            },
            error       : function (result) {
                console.log(result);
            }
        });
    });

    savedPresetContainer.on('click', savePresetBtn, function() {
        var thisBtn = $(this),
            presetNumber = $(this).parents('.saved-preset').data('preset-number'),
            presetName = $(this).parent().find('input').val(),
            parent = thisBtn.parents('.saved-preset'),
            iconsContainer = parent.find('.select-preset-icon-container'),
            iconClass = '',
            dataToSend = {
                'presetNumber'  : presetNumber,
                'presetName'    : presetName
            };

        iconsContainer.find('.preset-icon-select ').each(function() {
            if ($(this).hasClass('active')) {
                iconClass = $(this).data('class');
            }
        });
        dataToSend.iconClass = iconClass;

        $.ajax({
            url         : '/update-preset',
            method      : 'POST',
            data        : JSON.stringify(dataToSend),
            contentType : 'application/json;charset=UTF-8',
            success     : function (result) {
                var icon = parent.find('.preset-icon');
                notification(result.message);
                icon.removeClass().addClass('fa ' + iconClass + ' preset-icon');
                parent.find('.preset-label').text(presetName);
                parent.find('.edit-preset').removeClass('active');
                thisBtn.parent().addClass('hidden');

                if (presetName === screenBloom.config.currentPreset) {
                    console.log('This is the current preset being edited');
                } else {
                    console.log('Not current preset, should remove active class');
                    parent.removeClass('active');
                }
            },
            error       : function (result) {
                console.log(result);
            }
        });
    });

    savedPresetContainer.on('click', iconSelect, function() {
        $(this).parent().find('.preset-icon-select').removeClass('active');
        $(this).addClass('active');
    });
};