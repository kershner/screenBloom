function hue_project() {
	stopBloom();
	startBloom();
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