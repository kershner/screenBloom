var siteConfig = {
    'analyticsUrl'  : ''
};

function screenBloom() {
	callFakeScreenBloom();
	clickScroll();
	hiddenMenu();
	crappyAnalytics();
}

function crappyAnalytics() {
    $('.download-btn').on('click', function() {
        var version = $(this).data('version'),
            build = $(this).data('build'),
            downloadData = {
                'build': build,
                'version': version
            };
        $.ajax({
        	url			: siteConfig.analyticsUrl,
        	method		: 'POST',
        	contentType	: 'application/json;charset=UTF-8',
        	data		: JSON.stringify(downloadData),
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
	var color = randomColor(),
		newBoxShadow = '0 0 10vw 1vw ' + color,
		borderBottom = '.5vh solid ' + color,
		elements = ['#bloom', '#hidden-bloom', '#download-section-title', '#about-section-title', '#media-section-title', '#support-section-title'];

	for (var i=0; i<elements.length; i++) {
		$(elements[i]).css({'color': color});
	}
	$('#logo').css({'box-shadow': newBoxShadow});
	$('#hidden-menu').css({'border-bottom': borderBottom});
}

function clickScroll() {
	var windowHeight = $(window).height(),
		offset = windowHeight * 0.12;

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

	$('#media-button, #nav-media').on('click', function() {
		$('html, body').animate({
			scrollTop: $('#media-section').offset().top - offset
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
	var windowHeight = $(window).height(),
		newOffset = (windowHeight * 0.12) + (windowHeight * 0.021),
		offset = $('#about-section').offset().top - newOffset;

	$(document).scroll(function() {
		var scrollTop = $(document).scrollTop();
		if (scrollTop > offset) {
			$('#hidden-menu').css('opacity', '1');
		} else {
			$('#hidden-menu').css('opacity', '0');
		}
	});
}

// Deferring video loads
function deferVideos() {
    var vidDefer = document.getElementsByTagName('iframe');
    for (var i=0; i<vidDefer.length; i++) {
    if(vidDefer[i].getAttribute('data-src')) {
    vidDefer[i].setAttribute('src',vidDefer[i].getAttribute('data-src'));
        }
    }
}
setTimeout(function() {
    deferVideos();
}, 3000);
