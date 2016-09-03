var analytics = {};

analytics.config = {
    'dates'         : [],
    'groupedDates'  : [],
    'downloads'     : [],
    'dataUrl'       : '',
    'loader'        : $('.loading-icon'),
    'containerDiv'  : $('.container'),
    'countSpan'     : $('#download-count'),
    'labelSpan'     : $('#daterange-label'),
    'dataTable'     : $('#downloads-table')
};

analytics.init = function() {
    var date1 = moment().subtract('days', 6).format('YYYY-MM-DD'),
        date2 = moment().add('days', 1).format('YYYY-MM-DD');

    dateRangeInit();
    getAnalyticsData(date1, date2, 'Last 7 Days');
};

function dateRangeInit() {
    $('input[name="daterange"]').daterangepicker(
    {
        locale: {
            format: 'YYYY-MM-DD'
        },
        startDate: moment().subtract('days', 6),
        endDate: moment().startOf('day'),
        ranges: {
            'Today'         : [moment().startOf('day'), moment().add('days', 1)],
            'Yesterday'     : [moment().subtract('days', 1), moment()],
            'Last 7 Days'   : [moment().subtract('days', 6), moment().add('days', 1)],
            'This Month'    : [moment().startOf('month'), moment().endOf('month')],
            'Last Month'    : [moment().subtract('month', 1).startOf('month'), moment().subtract('month', 1).endOf('month')],
            'Since May \'16': ['2016-05-06', moment().startOf('day')]
        }
    },
    function(start, end, label) {
        var startDate = start.format('YYYY-MM-DD'),
            endDate = end.format('YYYY-MM-DD');

        analytics.config.loader.removeClass('hidden');
        analytics.config.containerDiv.addClass('hidden');
        getAnalyticsData(startDate, endDate, label);
    });
}

function getAnalyticsData(date1, date2, label) {
    console.log('Grabbing analytics data...');
    var data = {
        'date1' : date1,
        'date2' : date2
    };

    $.ajax({
        url         : analytics.config.dataUrl,
        method      : 'POST',
        contentType : 'application/json;charset=UTF-8',
		data		: JSON.stringify(data),
        success     : function (result) {
            analytics.config.downloads = result.downloads;

            analytics.config.countSpan.text(analytics.config.downloads.length);

            if (label === 'Custom Range') {
                date1 = moment(date1).format('MMM Do');
                date2 = moment(date2).format('MMM Do');
                label = 'between ' + date1 + ' and ' + date2;
            }

            analytics.config.labelSpan.text(label);
            analytics.config.loader.addClass('hidden');
            analytics.config.containerDiv.removeClass('hidden');

            populateDownloadsTable();

            getGroupedDates();
            createDownloadsChart();
            analytics.config.dataTable.dataTable().fnDestroy();
            analytics.config.dataTable.DataTable({
                'order' : [0, 'desc']
            });
        },
        error       : function (result) {
            console.log(result);
        }
    });
}

function populateDownloadsTable() {
    $('#downloads-table tbody').remove();
    analytics.config.dataTable.append('<tbody></tbody>');
    for (var i=0; i<analytics.config.downloads.length; i++) {
        var download = analytics.config.downloads[i],
            date = moment(download.date).format('M/D/YYYY - h:mm a'),
            location = getLocationString(download.location_info),
            userAgent = download.user_agent,
            html = '<tr id="' + download.id +'" class="download"><td>' +
            download.id + '</td><td class="date">' + date + '</td><td>' +
            download.version + '</td><td class="build">' +
            download.build + '</td><td>'
            + location + '</td></tr>';
        $('#downloads-table tbody').append(html);
    }
}

function getLocationString(locStr) {
    if (locStr !== null) {
        var locObj = JSON.parse(locStr),
            city = locObj.city,
            country = getCountryName(locObj.country),
            region = locObj.region,
            finalStr = '';

        if (locPropertyExists(city)) {
            finalStr += city + ', ';
        }
        if (locPropertyExists(region)) {
            finalStr += region + ' | ';
        }
        if (locPropertyExists(country)) {
            finalStr += '<strong>' + country + '</strong>';
        }

        return finalStr;
    } else {
        return 'No data'
    }
}

function locPropertyExists(prop) {
    if (prop !== null && prop !== undefined && prop.length) {
        return true;
    }
    return false;
}

function getGroupedDates() {
    var downloads = analytics.config.downloads,
        dates = [];

    for (var i in downloads) {
        var download = downloads[i],
            dateString = moment(download.date).format('M/D/YYYY');
        dates.push([dateString, download.id]);
    }

    newDates = _.groupBy(dates, getDateString);
    analytics.config.groupedDates = newDates;
}

function getDateString(listElement) {
    return listElement[0];
}

function createDownloadsChart() {
    var chartData = getChartData(),
        backgroundColors = [],
        numDates = Object.keys(analytics.config.groupedDates).length;

    for (var i=0; i<numDates; i++) {
        var color = randomColor();
        backgroundColors.push(color);
    }

    var newLabels = [];
    for (var i=0; i<chartData.labels.length; i++) {
        var label = chartData.labels[i],
            newLabel = moment(label).format('ddd M/D');
        newLabels.push(newLabel);
    }

    var chartOptions = {
        legend: {
            display: false,
        }
    }

    if (numDates < 40) {
        // Add values to the graph bars
        chartOptions.animation = {
            duration: 500,
                easing: "easeOutQuart",
                onComplete: function () {
                    var ctx = this.chart.ctx;
                    ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontFamily, 'normal', Chart.defaults.global.defaultFontFamily);
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'bottom';

                    this.data.datasets.forEach(function (dataset) {
                        for (var i = 0; i < dataset.data.length; i++) {
                            var model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model,
                                scale_max = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._yScale.maxHeight;
                            ctx.fillStyle = '#6e6e6e';
                            var y_pos = model.y - 5;
                            // Make sure data value does not get overflown and hidden
                            // when the bar's value is too close to max value of scale
                            // Note: The y value is reverse, it counts from top down
                            if ((scale_max - model.y) / scale_max >= 0.93)
                                y_pos = model.y + 20;
                            ctx.fillText(dataset.data[i], model.x, y_pos);
                        }
                    });
                }
        }
    }

    var data = {
        labels      : newLabels,
        datasets    : [
            {
                label           : 'Downloads',
                backgroundColor : backgroundColors,
                data            : chartData.numDownloads,
            }
        ]
    };

    $('.chart-container').empty().append('<canvas id="downloadsChart" width="400" height="200"></canvas>');
    var downloadsPerDayChart = new Chart($('#downloadsChart'), {
        type    : 'bar',
        data    : data,
        options : chartOptions
    });
}

function getChartData() {
    var numDownloadsList = [],
        days = analytics.config.groupedDates,
        labels = [];

    for (var day in days) {
        if (day !== undefined) {
            var numDownloads = days[day].length;
        } else {
            var numDownloads = 0;
        }
        numDownloadsList.push(numDownloads);
        labels.push(day);
    }

    var returnValues = {
        'labels'        : labels,
        'numDownloads'  : numDownloadsList
    }
    return returnValues;
}
