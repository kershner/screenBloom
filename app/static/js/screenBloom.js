var screenBloom = {};

screenBloom.config = {
	'minBriUrl'			: '',
	'updateSpeedUrl'	: '',
	'defaultColorUrl'	: '',
	'partyModeUrl'		: '',
	'bulbsUrl'			: '',
	'defaultColor'		: '',
	'lightsNumber'		: ''
};

screenBloom.init = function() {
	ipHelp();
	clickRegister();

	callBloomColor();
	callHelloColor();
	callColorSettings();

	settingsBtns();
	bulbSelect();
	startStopBtns();
	updateSettings();

	colorPicker();
	lightsOnOff();
	sliderUpdate();

	goldBloom();
};

function settingsBtns() {
	$('.setting').on('click', function(e) {
		var inputContainer = $(this).find('.setting-input'),
			target = $(e.target);

		if ($(this).hasClass('party-mode-btn')) {
			var partyModeInput = $(this).find('input'),
				settingCircle = $(this).find('.setting-circle');
			settingCircle.toggleClass('setting-clicked');
			if (settingCircle.hasClass('setting-clicked')) {
				partyModeInput.val(1);
				settingCircle.find('span').text('On');
				togglePartyMode(1);
			} else {
				partyModeInput.val(0);
				settingCircle.find('span').text('Off');
				togglePartyMode(0);
			}
		} else {
			if (target.hasClass('setting-input') || target.hasClass('slider') || target.hasClass('slider-max') || target.hasClass('picker')) {
				// Do nothing if clicking inside input
			} else if (target.hasClass('setting-input-close')) {
				$(this).find('.setting-circle').toggleClass('setting-clicked');
				inputContainer.toggleClass('hidden');
			} else {
				$('.setting-input').addClass('hidden');
				$('.setting-circle').removeClass('setting-clicked');
				$(this).find('.setting-circle').toggleClass('setting-clicked');
				inputContainer.toggleClass('hidden');
			}
		}
	});
}

function togglePartyMode(partyMode) {
	$.ajax({
		url			: screenBloom.config.partyModeUrl,
		method		: 'POST',
		contentType	: 'application/json;charset=UTF-8',
		data		: JSON.stringify(partyMode),
		success: function (result) {
			notification(result.message);
		},
		error: function (result) {
			console.log(result);
		}
	});
}


function bulbSelect() {
	// Toggle class for bulbs on click
	$('.bulb-container').on('click', function() {
		$(this).toggleClass('bulb-inactive');
		$('.update-bulbs').removeClass('hidden');
	});

	// Create active bulbs string from .bulb-container CSS class, send to server to be written
	$('.update-bulbs').on('click', function() {
		var bulbs = [];
		$('.bulb-container').each(function() {
			if ($(this).hasClass('bulb-inactive')) {
				bulbs.push(0);
			} else {
				bulbs.push($(this).data('light'));
			}
		});
		$.ajax({
			url			: screenBloom.config.bulbsUrl,
			method		: 'POST',
			contentType	: 'application/json;charset=UTF-8',
			data		: JSON.stringify(bulbs.toString()),
			success: function (result) {
				notification(result.message);
				$('.update-bulbs').addClass('hidden');
			},
			error: function (result) {
				console.log(result);
			}
		});
	});
}

function startStopBtns() {
	var clicked = false,
		startBtn = $('#start'),
		stopBtn = $('#stop');
	startBtn.on('click', function() {
		var color = randomColor();
		if (!clicked) {
			clicked = true;
			$.getJSON($SCRIPT_ROOT + '/start', function(data) {
				notification(data.message);
			});
			startBtn.addClass('button-selected');
			startBtn.css({
				'background-color': color,
				'border': '2px solid ' + color,
				'text-shadow': '1px 1px 3px rgba(0, 0, 0, 0.3)'
			});
			startBtn.text('Running...');
		}
	});

	stopBtn.on('click', function() {
		$.getJSON($SCRIPT_ROOT + '/stop', function(data) {
			notification(data.message);
		});
		clicked = false;
		startBtn.removeClass('button-selected');
		startBtn.css({
			'background-color': '#F2F2F2',
			'border': '2px solid #007AA3',
			'color': '#007AA3',
			'text-shadow': 'none'
		});
		startBtn.text('Start');
	});
}

// Updates setting slider to currently selected value
function sliderUpdate() {
	var sliders = ['#bri', '#dynamic-bri', '#update-speed'];
	for (var i = 0; i < sliders.length; i++) {
		$(sliders[i] + '-slider').on('input', function() {
			var id = $(this).attr('id');
			var value = $(this).val();
			var outputId = ('#' + id + '-output');
			$(outputId).html(value);
		});
	}
}

function lightsOnOff() {
	var state = $('#on-state').text();
	var stateVar = '';
	$('#on-off').on('click', function() {
		if (state === 'On') {
			state = 'Off';
			stateVar = 'On';
		} else {
			state = 'On';
			stateVar = 'Off';
		}
		$('#on-state').empty().append(state);
		$.getJSON($SCRIPT_ROOT + '/on-off', {
			state: stateVar
		}, function(data) {
			console.log(data['message']);
		});
		return false
	});
}

function updateSettings() {
	$('.setting-input-submit').on('click', function() {
		var url = $(this).data('url'),
			value = $(this).siblings('input').val(),
			settingContainer = $(this).parents('.setting'),
			valueDiv = settingContainer.find('.setting-value');

		if (url === 'defaultColorUrl') {
			value =  $('.colpick_hex_field input').val();
			valueDiv = undefined;
		}

		$.ajax({
			url			: screenBloom.config[url],
			method		: 'POST',
			contentType	: 'application/json;charset=UTF-8',
			data		: JSON.stringify(value),
			success: function (result) {
				notification(result.message);
				if (valueDiv === undefined) {
					settingContainer.find('.setting-circle').css('background-color', '#' + value);
				} else {
					valueDiv.text(result.value);
				}
				$('.setting-input').addClass('hidden');
				$('.setting-circle').removeClass('setting-clicked');
			},
			error: function (result) {
				console.log(result);
			}
		});
	});
}

function notification(text) {
	var notification = $('#notification');
	notification.empty().text(text);
	notification.css('opacity', '1');
	notification.removeClass('hidden');
	setTimeout(function() {
		notification.animate({
			'opacity': 0.0
		}, 1000, function() {
			notification.addClass('hidden');
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
	for (var i = 0; i < elements.length; i++) {
		var color = randomColor();
		$(elements[i]).css({
			'color': color
		}, 2000);
	}
}

//= Utility =======================================================================================
function randomNumber(min, max) {
	return Math.floor(Math.random() * (max - min)) + min
}

function colorPicker() {
	$('#picker').colpick({
		flat: true,
		layout: 'hex',
		submit: 0,
		color: {
			r: screenBloom.config.defaultColor[0],
			g: screenBloom.config.defaultColor[1],
			b: screenBloom.config.defaultColor[2]
		}
	});
}

// Really dumb easter egg
function goldBloom() {
	var clicked = false;
	$('#secret-goldblum').on('click', function() {
		if (clicked) {
			clicked = false;
			console.log('Goodbye, Jeff!');
			$(this).css({
				'height': '1em',
				'opacity': '0.0'
			});
			$('#secret-goldblum img').css({
				'top': '-5.75em'
			});
		} else {
			clicked = true;
			console.log('GoldBloom!');
			$(this).css({
				'height': '14em',
				'opacity': '1.0'
			});
			$('#secret-goldblum img').css({
				'top': '0'
			});
			$('#goldbloom-trigger').on('click', function() {
				console.log('TRIGGERED');
				var randomNumber1 = randomNumber(1, 7),
					randomNumber2 = randomNumber(1, 7);
				if (randomNumber2 === randomNumber1) {
					randomNumber2 = randomNumber(1, 7);
				}
				var imageUrl = 'goldblum';
				$('#header-container').css('min-width', '68vh');
				var html = '<img src="' + imageUrl + randomNumber1 + '.jpg" class="goldblum fa-spin"><h1 class="header-title raleway goldblum-text">Gold</h1><h1 class="header-title lobster goldblum-text"><span class="bloom color-animate">Bloom</span></h1><img src="' + imageUrl + randomNumber2 + '.jpg" class="goldblum fa-spin">';
				$('#header-container').empty().append(html);
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
	$('#ip-info').on('click', function() {
		$('#ip-tooltip').fadeIn('fast');
	});

	$('#ip-tooltip-close').on('click', function() {
		$('#ip-tooltip').fadeOut('fast');
	});
}

// Handles AJAX call to register new username and displays error/success message
function clickRegister() {
	$('#register').on('click', function() {
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
		}, function(data) {
			if (data['success'] === true) {
				console.log(data);
				var html = 	'<div class="result-type"><h1 class="raleway animate">Success!</h1>' +
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
				$('#try-again').on('click', function() {
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
	return 	'<div class="result-type"><h1 class="raleway animate">Whoops!</h1><span>' + text + '</span>' +
			'<div id="try-again" class="animate">Try Again</div><script type="text/javascript">colorLoading();</script>';
}