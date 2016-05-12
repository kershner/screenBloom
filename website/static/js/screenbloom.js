var siteConfig = {
    'analyticsUrl'  : ''
}

function screenBloom() {
	callFakeScreenBloom();
	clickScroll();
	hiddenMenu();
	crappyAnalytics();
}

function crappyAnalytics() {
    $('.download-btn').on('click', function() {
       var version = $(this).data('version');
       $.ajax({
			url			: siteConfig.analyticsUrl,
			method		: 'POST',
			contentType	: 'application/json;charset=UTF-8',
			data		: JSON.stringify(version),
			success: function (result) {
				console.log(result);
			},
			error: function (result) {
				console.log(result);
			}
		});
    });
}

function callFakeScreenBloom() {
	fakeScreenBloom();
	setInterval(fakeScreenBloom, 3000);
}

function fakeScreenBloom() {
	var color = randomColor();
	var newBoxShadow = '0 0 10vw 1vw ' + color
	var borderBottom = '.5vh solid ' + color
	var elements = ['#bloom', '#hidden-bloom', '#download-section-title', '#about-section-title', '#support-section-title'];

	for (i = 0; i < elements.length; i++) {
		$(elements[i]).css({'color': color});
	}

	$('#logo').css({'box-shadow': newBoxShadow});
	$('#hidden-menu').css({'border-bottom': borderBottom});
}

function clickScroll() {
	var windowHeight = $(window).height();
	var offset = windowHeight * 0.12;

	$('#download-button, #nav-download').on('click', function() {
		$('html, body').animate({
			scrollTop: $('#download-section').offset().top - offset
		}, 800);
	});

	$('#about-button, #nav-about').on('click', function() {
		$('html, body').animate({
			scrollTop: $('#about-section').offset().top - offset
		}, 800);
	});

	$('#help-button, #nav-support').on('click', function() {
		$('html, body').animate({
			scrollTop: $('#support-section').offset().top - offset
		}, 800);
	});

	$('#top').on('click', function() {
		$('html, body').animate({
			scrollTop: $('html').offset().top
		}, 800);
	});
}

function hiddenMenu() {
	var windowHeight = $(window).height();
	var newOffset = (windowHeight * 0.12) + (windowHeight * 0.021);
	var offset = $('#about-section').offset().top - newOffset;

	$(document).scroll(function() {
		var scrollTop = $(document).scrollTop();
		if (scrollTop > offset) {
			$('#hidden-menu').css('opacity', '1');
		} else {
			$('#hidden-menu').css('opacity', '0');
		}
	});
}