var screenBloom = {};

screenBloom.config = {
	'timer'			: '',
	'colorWave'		: ['.sb-nav-logo'],
	'bloomHover'	: ['.bloomHover']
};

screenBloom.init = function() {
	$('[data-toggle="tooltip"]').tooltip({
		animation: true
	});

	startColorWave(screenBloom.config.colorWave);
	bloomHover(screenBloom.config.bloomHover);
};

// Generic function to create JS intervals, store them on the
// global screenBloom object so they can be cleared later
function createInterval(f, element, interval) {
	screenBloom.config.timer = setInterval(function() {
		f(element);
	}, interval);
}

// Applies colorWave to list of elements in screenBloom config
function startColorWave(elements) {
	for (var i=0; i<elements.length; i++) {
		$(elements[i]).each(function() {
			var colors = randomColor({
				count: $(this).text().length,
				luminosity: 'light'
			});
			var thisInstance = $(this);
			$(thisInstance).colorWave(colors);
			setInterval(function() {
				colors = randomColor({
					count: $(thisInstance).text().length,
					luminosity: 'light'
				});
				$(thisInstance).colorWave(colors);
			}, 8000);
		});
	}
}

// Continuously cycles random colors on hover for elements in config
function bloomHover(elements) {
	for (var i=0; i<elements.length; i++) {
		$(elements[i]).each(function() {
			var color = randomColor({luminosity: 'light'}),
				startingColor = '',
				timer = undefined;

			if ($(this).hasClass('options-icon')) {
				startingColor = $(this).css('color');
			} else if ($(this).hasClass('sb-portlet')) {
				startingColor = $(this).css('background-color');
			}

			$(this).addClass('bloomColor-animate');
			$(this).on({
				mouseenter: function() {
					if ($(this).hasClass('options-icon')) {
						$(this).css('color', color);
					} else if ($(this).hasClass('sb-portlet')) {
						$(this).css('background-color', color);
					}
					createInterval(bloomColors, $(this), 1000);
				},
				mouseleave: function() {
					clearInterval(screenBloom.config.timer);
					if ($(this).hasClass('options-icon')) {
						$(this).css({
							'color'	: startingColor
						});
					} else if ($(this).hasClass('sb-portlet')) {
						$(this).css({
							'background-color'	: startingColor
						});
					}
				}
			});
		});
	}
}

// Reusable function to generate color/apply to specified element
function bloomColors(element) {
	var color = randomColor({luminosity: 'light'});

	if ($(element).hasClass('options-icon')) {
		$(element).css({
			'color'	: color
		});
	} else if ($(element).hasClass('sb-portlet')) {
		$(element).css({
			'background-color'	: color
		});
	}
}