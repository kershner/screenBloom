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