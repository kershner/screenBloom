function hue_project() {
	fillSquare();
	turnOff();
}

function fillSquare() {
	$('#test-button-on').on('click', function() {
		console.log('Clicked On Button!');
		var timer = window.setInterval(function() {
			ajaxColor();
		}, 1000);
	});
}

function turnOff() {
	$('#test-button-off').on('click', function() {
		console.log('Clicked Off Button!');
		$('#color-tester').css({'background-color': 'white'});
		window.clearInterval();
	});
}

function ajaxColor() {
	$.getJSON($SCRIPT_ROOT + '/get-screen-color', function(data) {
        console.log(data);
        $('#color-tester').css({'background-color': data['screen_hex']});
    });
    return false
}