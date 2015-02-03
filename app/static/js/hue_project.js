function hue_project() {
	runningCheck();
	startBloom();
	stopBloom();
	colorLogo();
	editSettings();
	updateConfig();
}

// If ScreenBloom running, add CSS classes to visual indicators
function runningCheck() {
	$.getJSON($SCRIPT_ROOT + '/get-settings', {
		}, function(data) {
        	if (data['running-state'] === 'True') {
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

// Called by colorLogo() to apply random color to ScreenBloom logos
function bloomChange() {
	var color = randomColor();
	$('.bloom').css({'color': color}, 6000);
}

function colorLogo() {
	var color = randomColor();
	$('.bloom').css({'color': color}, 2000);
	setInterval(bloomChange, 6500);
}


// Updates setting slider to currently selected value
function outputUpdate(divID, value) {
    $(divID).empty();
    $(divID).append(value);
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
}


// Grab values from sliders, send to a Python route
function updateConfig() {
	$('#apply').on('click', function() {
		var sat = $('#sat-slider').val();
		var bri = $('#bri-slider').val();
		var transition = $('#transition-slider').val();

		$('#notification').fadeIn(400);
		$('#edit-settings').fadeOut(400, function() {
	    	$('#edit-settings-wrapper').fadeOut(1500, function() {
    			$('#notification').fadeOut(1500);
    		});
	    });
		$.getJSON($SCRIPT_ROOT + '/update-config', {
			sat: sat,
			bri: bri,
			transition: transition
		}, function(data) {
        	updateFront();
	    });
	    return false	    
	});
}

// Updates settings on main page to their current value
function updateFront() {
	$.getJSON($SCRIPT_ROOT + '/get-settings', {
		}, function(data) {
        	elements = ['bulbs-value', 'sat-value', 'bri-value', 'trans-value'];        	
        	for (i = 0; i < elements.length; i++) {
        		elementId = '#' + elements[i];
        		$(elementId).empty();
        		$(elementId).append(data[elements[i]]);
        	}
	    });
	    return false
}