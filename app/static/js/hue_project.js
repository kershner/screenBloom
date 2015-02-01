function hue_project() {
	stopBloom();
	startBloom();
	colorLogo();
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