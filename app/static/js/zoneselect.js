var zoneGrid = {
    'width'             : 16,
    'height'            : 9,
    'defaultColor'      : 'grey',
    'colors'            : [],
    'zones'             : [],
    'lightsMaster'      : [],
    'activeLights'      : [],
    'availableLights'   : [],
    'state'             : false,
    'selectionStarted'  : false,
    'startCell'         : '',
    'endCell'           : '',
    'toggleZonesUrl'    : '',
    'updateZonesUrl'    : ''
};

zoneGrid.init = function() {
    updateGridLights();
    generateColors();
    buildGrid();

    $('#toggle-zone-mode').on('click', function() {
        toggleZoneMode();
    });

    $('#restart').on('click', function() {
        zoneGrid.zones = [];
        zoneGrid.selectionStarted = false;
        zoneGrid.state = 1;
        updateGridLights();
        buildGrid();
        saveGridResults();
        toggleZoneMode();
    });

    $('#save-zones').on('click', function() {
        saveGridResults();
    });
};

//////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////
// Remove zone from zoneGrid object, write config, rebuild grid
function clearZone(zoneIndex) {
    console.log('Deleting Zone!');
    zoneGrid.zones.splice(zoneIndex, 1);
    buildGrid();
    saveGridResults();
}
//////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////

// Rebuilds zoneGrid object light lists
function updateGridLights() {
    var activeLights = [],
        zones = zoneGrid.zones,
        bulbsInUse = [];

    $('.bulb-container').each(function() {
       if (!$(this).hasClass('bulb-inactive')) {
           var lightId = $(this).data('light');
           activeLights[lightId] = zoneGrid.lightsMaster[lightId];
       }
    });
    zoneGrid.activeLights = activeLights;

    // Get list of bulbs already assigned to a zone
    for (var i=0; i<zones.length; i++) {
        var bulbs = zones[i].bulbs;
        for (var j=0; j<bulbs.length; j++) {
            bulbsInUse.push(bulbs[j]);
        }
    }

    // Build new list of active lights not current used in a zone
    zoneGrid.availableLights = [];
    for (var k in zoneGrid.activeLights) {
        if ($.inArray(k, bulbsInUse) > -1) {
        } else {
            zoneGrid.availableLights.push(k);
        }
    }
}

function generateColors() {
    for (var i=0; i<64; i++) {
        var color = randomColor({
            luminosity: 'dark'
        });
        if (!$.inArray(color, zoneGrid.colors) > -1) {
            zoneGrid.colors.push(color);
        }
    }
}

//== Main HTML Grid/Form Functions ================================================================
// Builds the HTML grid, places click event
function buildGrid() {
    var grid = $('#grid');
    grid.html(''); // clear grid
    updateZoneBulbs(); // rebuild bulb selection forms
    addBulbsToZone();  // event handlers for the bulb selection forms

    for (var lineIndex=0; lineIndex<zoneGrid.height; lineIndex++) {
        //build each line
        var lineId = "line-" + lineIndex;
        grid.append("<div class='line' id='" + lineId + "' ></div>");
        for (var cellIndex=0; cellIndex<zoneGrid.width; cellIndex++) {
            //build each column
            var line = $('#' + lineId),
                cellId = "cell-" + lineIndex + "-" + cellIndex;
            line.append("<div class='cell' id='" + cellId + "' >&nbsp;</div>");

            var cell = $('#' + cellId);
            //default color
            cell.css('background-color', zoneGrid.defaultColor);

            // Restore color if cell is from saved zone
            for (var i in zoneGrid.zones) {
                var zone = zoneGrid.zones[i];
                if (lineIndex >= zone.y1 && lineIndex <= zone.y2 && cellIndex >= zone.x1 && cellIndex <= zone.x2) {
                    cell.css('background-color', zoneGrid.colors[i]);
                    cell.attr('data-zone', i);
                }
            }
            //place event
            cell.on('click', cellClick);
            cell.on('mouseover', cellOver);
        }
    }
}

// Builds the form for bulb selection
function updateZoneBulbs() {
    $('#zone-bulbs').html('');
    for (var zoneIndex in zoneGrid.zones) {
        var zone = zoneGrid.zones[zoneIndex],
            color = zoneGrid.colors[zoneIndex],
            html =  '<div class="zone-container" style="border: 2px solid ' + color + '" data-id="' + zoneIndex + '">' +
                    '<i class="fa fa-close delete-zone-btn" data-id="' + zoneIndex + '"></i>' +
                    '<i class="fa fa-plus-square add-zone-bulbs-btn"></i>' +
                    '<div class="zone-bulbs-wrapper">';

        // Add bulb objects
        for (var i=0; i<zone.bulbs.length; i++) {
            html += getZoneBulbWrapperHtml(color, zone.bulbs[i]);
        }

        html += getAddBulbsDiv();
        html += '</div>';
        html += getZoneInputs(zone);
        html += '</div>';

        $('#zone-bulbs').append(html);
    }
}

// Events for the add bulbs to zone menus
function addBulbsToZone() {
    $('.add-zone-bulbs-btn').on('click', function() {
        var zoneIndex = $(this).data('id'),
            zone = zoneGrid.zones[zoneIndex],
            wrapper = $(this).parent().find('.add-bulbs-to-zone-wrapper');

        if (zoneGrid.availableLights.length > 0) {
            wrapper.removeClass('hidden');
        } else {
            notification('No active lights available to assign to this zone');
        }
    });

    $('.close-add-bulbs-to-zone-wrapper').on('click', function() {
       $(this).parent().addClass('hidden');
    });

    $('.available-bulb').on('click', function() {
        $(this).toggleClass('available-bulb-selected');
    });

    $('.add-bulbs-to-zone-confirm').on('click', function() {
        var container = $(this).parent(),
            input = container.parents('.zone-container').find('.zone-bulb-values'),
            selectedBulbs = input.val().split(','),
            selectedBulbsNew = [];

        for (var i=0; i<selectedBulbs.length; i++) {
            if (selectedBulbs[i].length) {
                selectedBulbsNew.push(selectedBulbs[i]);
            }
        }

        container.find('.available-bulb').each(function() {
           if ($(this).hasClass('available-bulb-selected')) {
               var lightId = $(this).data('id');
               selectedBulbsNew.push(lightId);
           }
        });
        if (selectedBulbsNew.length) {
            input.val(selectedBulbsNew);
        }
    });
}

// DOM Building Helper Functions
function getAddBulbsDiv() {
    var html =  '<div class="add-bulbs-to-zone-wrapper hidden">' +
                '<i class="fa fa-times close-add-bulbs-to-zone-wrapper"></i>' +
                '<div class="available-bulbs-wrapper"><span class="available-bulbs-title">Available Bulbs</span>';


    for (var i=0; i<zoneGrid.availableLights.length; i++) {
        var lightId = zoneGrid.availableLights[i];
        html += '<div class="available-bulb" data-id="' + lightId + '">' +
                '<i class="fa fa-lightbulb-o"></i>' +
                '<span class="available-bulb-label">' + zoneGrid.lightsMaster[lightId] + '</span>' +
                '</div>';
    }

    html += '</div><div class="add-bulbs-to-zone-confirm">Add Bulbs</div></div>';
    return html;
}

function getZoneBulbWrapperHtml(color, bulbId) {
    var bulb = zoneGrid.lightsMaster[bulbId];
    return  '<div class="zone-bulb-wrapper">' +
            '<i class="fa fa-close delete-zone-bulb-btn" data-id="' + bulbId +'"></i>' +
            '<i class="fa fa-lightbulb-o zone-bulb" style="color: ' + color + '"></i>' +
            '<div class="zone-bulb-label">' + bulb + '</div></div>';
}

function getZoneInputs(zone) {
    return  '<input class="zone-bulb-values" type="text" value="' + zone.bulbs + '">' +
            '<input class="grid-values x1" type="text" value="' + zone.x1 + '">' +
            '<input class="grid-values x2" type="text" value="' + zone.x2 + '">' +
            '<input class="grid-values y1" type="text" value="' + zone.y1 + '">' +
            '<input class="grid-values y2" type="text" value="' + zone.y2 + '">';
}

//== HTML Grid Helper Functions ===================================================================
//preview mode
function cellOver() {
    if (zoneGrid.selectionStarted) {
        var curCell = $(this),
            corners = getCorners(zoneGrid.startCell, curCell);
        clearPixels();
        selectZone(corners, false); //just preview
    }
}

//on click, for start or stop selection
function cellClick() {
    var curCell = $(this);

    if (zoneGrid.availableLights.length > 0) {
        //first click to start selection
        if (!zoneGrid.selectionStarted) {
            zoneGrid.startCell = curCell;
            markCell(curCell, true);
            zoneGrid.selectionStarted = true;
        } else {
            //second click to end selection
            zoneGrid.endCell = curCell;
            zoneGrid.selectionStarted = false;
            var corners = getCorners(zoneGrid.startCell, zoneGrid.endCell);
            validateZone(corners);
            buildGrid();
        }
    } else {
        notification('No active lights are available for a new zone');
    }
}

//get the top left and bottom right corners from two cells
function getCorners(cellA, cellB) {
    return {
        'x1': Math.min(cellA.attr('id').split('-')[2], cellB.attr('id').split('-')[2]),
        'y1': Math.min(cellA.attr('id').split('-')[1], cellB.attr('id').split('-')[1]),
        'x2': Math.max(cellA.attr('id').split('-')[2], cellB.attr('id').split('-')[2]),
        'y2': Math.max(cellA.attr('id').split('-')[1], cellB.attr('id').split('-')[1])
    };
}

// Called when a new zone is created
function validateZone(corners) {
    corners.bulbs = [];
    zoneGrid.zones.push(corners); // add zone to zoneGrid object

    selectZone(corners, true); // update color and mark as selected
    updateGridLights();
    buildGrid();
}

//clear unselected pixels
function clearPixels() {
    for (var lineIndex=0; lineIndex<zoneGrid.height; lineIndex++) {
        for (var cellIndex=0; cellIndex<zoneGrid.width; cellIndex++) {
            //restoring default color
            var curCell = $('#cell-' + lineIndex + "-" + cellIndex);
            if (!curCell.hasClass('selected')) {
                curCell.css('background-color', zoneGrid.defaultColor);
            }
            //restoring zone zone-colors
            $.each(zoneGrid.zones, function(zoneIndex, zone) {
                if (lineIndex >= zone.y1 && lineIndex <= zone.y2 && cellIndex >= zone.x1 && cellIndex <= zone.x2) {
                    curCell.css('background-color', zoneGrid.colors[zoneIndex]);
                }
            });
        }
    }
}

function markCell(cell, validate) {
    if (validate === true) {
        cell.addClass('selected');
    }
    cell.css({
        'background-color': zoneGrid.colors[zoneGrid.zones.length]
    });
}

//change the color of cells, and add class 'selected' if validate is true
function selectZone(corners, validate) {
    for (var lineIndex=corners.y1; lineIndex<=corners.y2; lineIndex++) {
        for (var cellIndex=corners.x1; cellIndex<= corners.x2; cellIndex++) {
            var cellId = "cell-" + lineIndex + "-" + cellIndex,
                cell = $('#' + cellId);
            markCell(cell, validate);
        }
    }
}

//== AJAX Calls ===================================================================================
// Grabs values from DOM, sends to server to be persisted
function saveGridResults() {
    zoneGrid.zones = [];
    $('.zone-container').each(function() {
        var zoneIndex = $(this).data('id'),
            bulbs = $(this).find('.zone-bulb-values').val().split(','),
            x1 = $(this).find('.x1').val(),
            x2 = $(this).find('.x2').val(),
            y1 = $(this).find('.y1').val(),
            y2 = $(this).find('.y2').val();

        zoneGrid.zones[zoneIndex] = {};
        zoneGrid.zones[zoneIndex].bulbs = bulbs;
        zoneGrid.zones[zoneIndex].x1 = x1;
        zoneGrid.zones[zoneIndex].x2 = x2;
        zoneGrid.zones[zoneIndex].y1 = y1;
        zoneGrid.zones[zoneIndex].y2 = y2;
    });

    $.ajax({
        url			: $SCRIPT_ROOT + zoneGrid.updateZonesUrl,
        method		: 'POST',
        contentType	: 'application/json;charset=UTF-8',
        data		: JSON.stringify(zoneGrid.zones),
        success: function (result) {
            console.log(result);
            updateGridLights();
            buildGrid();
            notification(result['message']);
        },
        error: function (result) {
            console.log(result);
        }
    });
}

function toggleZoneMode() {
    var zoneStateDiv = $('#zone-state'),
        settingCircle = $('#zoneBtn.setting-circle');

    if (zoneGrid.state) {
        zoneStateDiv.html('Off');
        zoneGrid.state = 0;
    } else {
        zoneStateDiv.html('On');
        zoneGrid.state = 1;
    }
    $.ajax({
        url			: $SCRIPT_ROOT + zoneGrid.toggleZonesUrl,
        method		: 'POST',
        contentType	: 'application/json;charset=UTF-8',
        data		: JSON.stringify(zoneGrid.state),
        success: function (result) {
            console.log(result);
            notification(result['message']);
            settingCircle.removeClass('setting-clicked');
        },
        error: function (result) {
            console.log(result);
        }
    });
}