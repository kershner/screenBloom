function screenBloom() {
	startBloom();
	stopBloom();
	callBloomColor();
	callHelloColor();
	callColorSettings();
	sliderUpdate();
	editSettings();
	selectBulbs();
	toggleDynamicBri();
	togglePartyMode();
	ipHelp();
	clickRegister();
	goldBloom();
	colorPicker();
}

// If ScreenBloom running, add CSS classes to visual indicators
function runningCheck() {
	$.getJSON($SCRIPT_ROOT + '/get-settings', {}, function(data) {
		if (data['running-state'] === '1') {
			console.log('Running!');
			$('#start').addClass('button-selected');
			var color = randomColor();
			$('#running').css('color', color);
			$('#on-status').empty();
			$('#on-status').append('ScreenBloom is running');
		} else {
			$('#start').removeClass('button-selected');
			$('#running').css('color', 'black');
			$('#on-status').empty();
			$('#on-status').append('ScreenBloom is not running');
		}
	});
	return false
}

// Hit Python route and add 'running' CSS indicators when Start button clicked
function startBloom(state) {
	var clicked = false;
	$('#start').on('click', function() {
		console.log('Clicked Start!');
		if (clicked) {
			console.log('Nothing!');
		} else {
			clicked = true;
			$.getJSON($SCRIPT_ROOT + '/start', function(data) {
				console.log(data);
			});
			$(this).addClass('button-selected');
			var color = randomColor();
			$('#running').css('color', color);
			$('#on-status').empty();
			$('#on-status').append('ScreenBloom is running');
		}
		return false
	});

	$('#stop').on('click', function() {
		clicked = false;
		$('#start').removeClass('button-selected');
		$('#running').css('color', 'black');
		$('#on-status').empty();
		$('#on-status').append('ScreenBloom is not running');
	});
}

// Hit Python route when Stop button clicked
function stopBloom() {
	$('#stop').on('click', function() {
		console.log('Clicked Stop!');
		$.getJSON($SCRIPT_ROOT + '/stop', function(data) {
			console.log(data);
		});
		return false
	});
}

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

// Function to color letters of giant 'HELLO' greeting
function callHelloColor() {
	helloColor();
	setInterval(helloColor, 4000);
}

function helloColor() {
	var elements = ['#h', '#e', '#l-1', '#l-2', '#o', '#exclaim'];
	for (i = 0; i < elements.length; i++) {
		var color = randomColor();
		$(elements[i]).css({
			'color': color
		}, 2000);
	}
	var color = randomColor();
}

// Functions to color the settings titles
function callColorSettings() {
	colorSettings();
	setInterval(colorSettings, 4000);
}

function colorSettings() {
	var elements = [
		'#brightness-title',
		'#bulb-select-title',
		'#bulb-select-expanded-title',
		'#dynamic-brightness-title',
		'#settings-title',
		'#bulbs-title',
		'#update-speed-title',
		'#default-color-title',
		'#party-mode-title'		
	];
	for (i = 0; i < elements.length; i++) {
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

// Updates setting slider to currently selected value
function sliderUpdate() {
	var sliders = ['#bri', '#dynamic-bri', '#update-speed'];
	for (i = 0; i < sliders.length; i++) {
		$(sliders[i] + '-slider').on('input', function() {
			var id = $(this).attr('id');
			var value = $(this).val();
			var outputId = ('#' + id + '-output');
			$(outputId).html(value);
		});
	}
}

// Fade in 'Edit Settings' window
function editSettings() {
	$('#edit-settings-icon').on('click', function() {
		$('#edit-settings-wrapper').fadeIn('fast');
		$('#edit-settings').fadeIn('fast');

		$('#edit-settings-close').on('click', function() {
			$('#edit-settings-wrapper').fadeOut('fast');
		});
	});
	editSettingsPages();
}

function editSettingsPages() {
	$('#right-arrow').on('click', function() {
		var html = '<i id="left-arrow" class="fa fa-long-arrow-left animate"></i>';
		$('.edit-settings-arrows').empty().append(html);
		$('#page1').css({
			'opacity': '0.0',
			'z-index': '0'
		});
		$('#page2').css({
			'opacity': '1.0',
			'z-index': '5'
		});
		editSettingsPages();
	});
	
	$('#left-arrow').on('click', function() {
		var html = '<i id="right-arrow" class="fa fa-long-arrow-right animate"></i>';
		$('.edit-settings-arrows').empty().append(html);
		$('#page1').css({
			'opacity': '1.0',
			'z-index': '5'
		});
		$('#page2').css({
			'opacity': '0.0',
			'z-index': '0'
		});
		editSettingsPages();
	});
}

// Update 'selected_bulbs' value in config when icons clicked
function selectBulbs() {
	var clicked = false;
	$('.bulb-select-icon').on('click', function() {
		var id = $(this).attr('id');
		if (clicked) {
			clicked = false;
			$('[id=' + id + ']').removeClass('bulb-select-selected');
			$('[id=' + id + '] .bulb-select-input').val('0');
		} else {
			clicked = true;
			$('[id=' + id + ']').addClass('bulb-select-selected');
			$('[id=' + id + '] .bulb-select-input').val('1');
		}
	});
}

// Update hidden input with correct value when dynamic brightness button clicked
function toggleDynamicBri() {
	var clicked = false;
	$('#dynamic-bri-button').on('click', function() {
		if (clicked) {
			$('#dynamic-bri-input').val('0');
			dynamicBriButton(false);
			clicked = false;
		} else {
			$('#dynamic-bri-input').val('1');
			dynamicBriButton(true);
			clicked = true;
		}
	});
}

function togglePartyMode() {
	var clicked = false;
	$('#party-mode-button').on('click', function() {
		if (clicked) {
			$('#party-mode-input').val('0');
			var text = 'Off';
			$('#party-mode-button').removeClass('bulb-select-selected').empty().append(text);
			clicked = false;
		} else {
			$('#party-mode-input').val('1');
			var text = 'On';
			$('#party-mode-button').addClass('bulb-select-selected').empty().append(text);
			clicked = true;
		}
	});
}

// Grab values from sliders, send to a Python route
function updateConfig() {
	$('#apply').on('click', function() {
		var update = $('#update-speed-slider').val();
		var update = parseInt(update.replace('.', ''));
		if (update === 1) {
			update = '10';
		} else if (update == 2) {
			update = '20';
		}
		console.log('Update Speed value: ' + update);
		var bulbs = [];
		for (i = 0; i < window.lightsNumber; i++) {
			var id = '#light-' + i;
			var value = $(id).children().last().val();
			bulbs.push(value);
		}
		var bri = $('#bri-slider').val();
		var bulbsString = bulbs.toString();
		var dynamicBri = $('#dynamic-bri-input').val();
		var minBri = $('#dynamic-bri-slider').val()
		var defaultColor = $('.colpick_hex_field input').val()
		var partyMode = $('#party-mode-input').val();

		$('#notification').fadeIn(400);
		$('#edit-settings').fadeOut(400, function() {
			$('#edit-settings-wrapper').fadeOut(1500, function() {
				$('#notification').fadeOut(1500);
			});
		});
		$.getJSON($SCRIPT_ROOT + '/update-config', {
			bri: bri,
			bulbs: bulbsString,
			update: update,
			dynamicBri: dynamicBri,
			minBri: minBri,
			defaultColor: defaultColor,
			partyMode: partyMode
		}, function(data) {
			updateFront();
		});
		return false
	});
}

// Updates settings on main page to their current value
function updateFront() {
	$.getJSON($SCRIPT_ROOT + '/get-settings', {}, function(data) {
		elements = ['bulbs-value', 'bri-value', 'update-value'];
		for (i = 0; i < elements.length; i++) {
			elementId = '#' + elements[i];
			$(elementId).empty();
			var newData = data[elements[i]];
			if (elements[i] === 'update-value') {
				if (newData === '1' || newData === '2') {
					console.log(newData);
					newData = newData;
				} else {
					var newData = newData / 10 + '<span> seconds</span>';
				}
			}
			$(elementId).append(newData);
		}
		bulbIcon(data['bulbs-value'], data['all-bulbs']);
		dynamicBriButton(data['dynamic-brightness']);
		$('#dynamic-bri-value').empty();
		if (data['dynamic-brightness']) {
			var text = 'On';
		} else {
			var text = 'Off';
		}
		$('#dynamic-bri-value').append(text);
		var color = 'rgb(' + data['default'] + ')';
		$('#default-color-value').css({
			'background-color': color
		});
		if (data['party-mode'] === '1') {
			console.log('Party Mode Enabled!');
			var text = 'On';
			$('#party-mode-value').empty().append(text);
		} else {
			console.log('Party Mode Disabled!');
			var text = 'Off';
			$('#party-mode-value').empty().append(text);
		}
	});
	return false
}

// Apply correct classes to selected lights icons
function bulbIcon(selected, all) {
	for (i = 0; i < all.length; i++) {
		if (selected[i]) {
			var element = '#bulb-' + all[i];
			$(element).removeClass('bulb-inactive');
		} else {
			var element = '#bulb-' + all[i];
			$(element).addClass('bulb-inactive');
		}
	}
}

// Apply correct class to dynamic brightness button
function dynamicBriButton(running) {
	$('#dynamic-bri-state').empty();
	if (running) {
		$('#dynamic-bri-button').addClass('dynamic-bri-on');
		var text = 'On';
		$('#dynamic-bri-state').append(text);
	} else {
		$('#dynamic-bri-button').removeClass('dynamic-bri-on');
		var text = 'Off';
		$('#dynamic-bri-state').append(text);
	}
}

// Show button to expand bulb select if there are a lot of lights
function bulbExpand(lights) {
	if (lights > 3) {
		$('#more-bulbs').css('display', 'block');
		$('#more-bulbs').on('click', function() {
			$('#bulb-select-expanded').fadeIn('fast');
		});
		$('#bulb-select-expanded-close').on('click', function() {
			$('#bulb-select-expanded').fadeOut('fast');
		});
	} else {
		$('#more-bulbs').css('display', 'none');
	}
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
		$('.result-wrapper').empty();
		var loadingIcon = '<i id="loading" class="fa fa-spinner fa-spin"></i>';
		var script = '<script type="text/javascript">colorLoading();</script>'
		$('.result-wrapper').append(loadingIcon);
		$('.result-wrapper').append(script);

		var username = $('#username').val();
		var hue_ip = $('#hue-ip').val();
		if (hue_ip) {
			console.log('IP entered manually');
			var hue_ip = $('#hue-ip').val();
		}

		if (username.length < 10) {
			$('.validation').fadeIn('fast', function() {
				setTimeout(function() {
					$('.validation').fadeOut('fast');
				}, 2000);
			});
		} else {
			$('.result-wrapper').fadeIn('fast');
			$.getJSON($SCRIPT_ROOT + '/register', {
				username: username,
				hue_ip: hue_ip
			}, function(data) {
				if (data['success'] === true) {
					console.log(data);
					var html = '<div class="result-type"><h1 class="raleway animate">Success!</h1><span>ScreenBloom was registered with your Hue Bridge.</span><span>Click the link below to continue!</span><a class="animate" href="/">Continue</a>';
					var script = '<script type="text/javascript">colorLoading();</script>'
					$('.result-wrapper').append(html);
					$('.result-wrapper').append(script);
				} else if (data['error_type'] === '101') {
					console.log('Link button not pressed');
					var html = '<div class="result-type"><h1 class="raleway animate">Whoops!</h1><span>Looks like the Bridge\'s link button wasn\'t pressed first.</span><div id="try-again" class="animate">Try Again</div>';
					var script = '<script type="text/javascript">colorLoading();</script>'
					$('.result-wrapper').append(html);
					$('.result-wrapper').append(script);
					$('#try-again').on('click', function() {
						$('.result-wrapper').fadeOut('fast');
					});
				} else if (data['error_type'] === 'Invalid URL') {
					console.log('LocalHost Error, try again...');
					var html = '<div class="result-type"><h1 class="raleway animate">Whoops!</h1><span>Looks like there was an error with the network, please try again.</span><div id="try-again" class="animate">Try Again</div>';
					var script = '<script type="text/javascript">colorLoading();</script>'
					$('.result-wrapper').append(html);
					$('.result-wrapper').append(script);
					$('#try-again').on('click', function() {
						$('.result-wrapper').fadeOut('fast');
					});
				} else if (data['error_type'] === 'manual') {
					console.log('Redirecting to manual IP entry...');
					window.location.href = '/manual';
				} else if (data['error_type'] === 'permission') {
					console.log('Permission Error');
					var html = '<div class="result-type"><h1 class="raleway animate">Whoops!</h1><span>ScreenBloom needs administrator permissions to create a config file.  Please restart the application as an administrator. </span><div id="try-again" class="animate">Try Again</div>';
					var script = '<script type="text/javascript">colorLoading();</script>'
					$('.result-wrapper').append(html);
					$('.result-wrapper').append(script);
					$('#try-again').on('click', function() {
						$('.result-wrapper').fadeOut('fast');
					});
				}
			});
		}
	});
}

function randomNumber(min, max) {
	return Math.floor(Math.random() * (max - min)) + min
}

// Really dumb easter egg
function goldBloom() {
	var clicked = false;
	$('#secret-goldblum').on('click', function() {
		if (clicked) {
			clicked = false;
			console.log('Goodbye, Jeff!');
			$(this).css({
				'height': '-=160vh',
				'opacity': '0.0'
			});
			$('#secret-goldblum img').css({
				'top': '-=60vh'
			});
			$('#goldbloom-trigger').css({
				'display': 'none',
				'top': '-=58vh',
				'left': '-=45vh'
			});
		} else {
			clicked = true;
			console.log('GoldBloom!');
			$(this).css({
				'height': '+=160vh',
				'opacity': '1.0'
			});
			$('#secret-goldblum img').css({
				'top': '+=60vh'
			});
			$('#goldbloom-trigger').css({
				'display': 'block',
				'top': '+=58vh',
				'left': '+=45vh'
			});
			$('#goldbloom-trigger').on('click', function() {
				console.log('TRIGGERED');
				randomNumber1 = randomNumber(1, 7);
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

function colorPicker() {
	$('#picker').colpick({
		flat: true,
		layout: 'hex',
		submit: 0,
		color: {
			r: window.defaultColor[0],
			g: window.defaultColor[1],
			b: window.defaultColor[2]
		}
	});
}