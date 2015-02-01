function hue_project() {
	stopBloom();
	startBloom();
	colorLogo();
	editSettings();
	updateConfig();
}

function stopBloom() {
	$('#stop').on('click', function() {
		console.log('Clicked Stop!');
		$.getJSON($SCRIPT_ROOT + '/stop', function(data) {
        	console.log(data);    
	    });
	    return false
	});
}

function startBloom() {
	$('#start').on('click', function() {
		console.log('Clicked Start!');
		$.getJSON($SCRIPT_ROOT + '/start', function(data) {
        	console.log(data);    
	    });
	    return false
	});
}

function bloomChange() {
	var color = randomColor();
	$('.bloom').css({'color': color}, 6000);
}

function colorLogo() {
	var color = randomColor();
	$('.bloom').css({'color': color}, 2000);
	setInterval(bloomChange, 6500);
}

function outputUpdate(divID, value) {
    $(divID).empty();
    $(divID).append(value);
}

function editSettings() {
	$('#edit-settings-icon').on('click', function() {
		$('#edit-settings-wrapper').fadeIn('fast');

		$('#edit-settings-close').on('click', function() {
			$('#edit-settings-wrapper').fadeOut('fast');
		});
	});
}

function updateConfig() {
	$('#apply').on('click', function() {
		var sat = $('#sat-slider').val();
		var bri = $('#bri-slider').val();
		var transition = $('#transition-slider').val();

		$.getJSON($SCRIPT_ROOT + '/update-config', {
			sat: sat,
			bri: bri,
			transition: transition
		}, function(data) {
        	console.log(data);    
	    });
	    return false
	});
}