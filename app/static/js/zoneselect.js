var zoneGrid = {
    'width'             : 16,
    'height'            : 9,
    'colors'            : [],
    'defaultColor'      : 'grey',
    'zones'             : [],
    'lightsMaster'      : [],
    'activeLights'      : [],
    'state'             : false,
    'selectionStarted'  : false,
    'startCell'         : '',
    'endCell'           : '',
    'toggleZonesUrl'    : '',
    'updateZonesUrl'    : ''
};

zoneGrid.init = function() {
    addBulbNamesToZones();
    generateColors();
    buildGrid();
    updateGridActiveLights();

    $('#toggle-zone-mode').on('click', function() {
        toggleZone();
    });

    $('#restart').on('click', function() {
        zoneGrid.zones = [];
        zoneGrid.selectionStarted = false;
        buildGrid();
        saveGridResults();
    });

    $('#save-zones').on('click', function() {
        saveGridResults();
    });
};

function addBulbNamesToZones() {
    for (var i in zoneGrid.zones) {
        var bulb = zoneGrid.zones[i].bulb;
        zoneGrid.zones[i].bulbName = zoneGrid.lightsMaster[bulb];
    }
}

//////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////
// Remove zone from zoneGrid object, write config, rebuild grid
function clearZone(zoneIndex) {
    console.log('Deleting Zone!');
    zoneGrid.zones.splice(zoneIndex, 1);
    buildGrid();
    saveGridResults();
}

function updateGridActiveLights() {
    var activeLights = [];
    $('.bulb-container').each(function() {
       if (!$(this).hasClass('bulb-inactive')) {
           var lightId = $(this).data('light');
           activeLights[lightId] = zoneGrid.lightsMaster[lightId];
       }
    });
    zoneGrid.activeLights = activeLights;
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

//build the grid, place click event
function buildGrid() {
    var grid = $('#grid');
    grid.html(''); // clear grid
    updateZoneBulbs(); // rebuild bulb selection forms

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

//get the top left and bottom right corners from two cells
function getCorners(cellA, cellB) {
    return {
        'x1': Math.min(cellA.attr('id').split('-')[2], cellB.attr('id').split('-')[2]),
        'y1': Math.min(cellA.attr('id').split('-')[1], cellB.attr('id').split('-')[1]),
        'x2': Math.max(cellA.attr('id').split('-')[2], cellB.attr('id').split('-')[2]),
        'y2': Math.max(cellA.attr('id').split('-')[1], cellB.attr('id').split('-')[1])
    };
}

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
    }
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

function selectZoneBulb(zoneIndex) {
    var select = $("#select-" + zoneIndex);
    zoneGrid.zones[zoneIndex].bulb = select.val();
    zoneGrid.zones[zoneIndex].bulbName = zoneGrid.lightsMaster[select.val()];
    updateZoneBulbs();
}

// Builds the form for bulb selection
function updateZoneBulbs() {
    updateGridActiveLights();

    $('#zone-bulbs').html('');
    for (var zoneIndex in zoneGrid.zones) {
        var html =  '<div class="zone-color-circle" style="background-color: ' + zoneGrid.colors[zoneIndex] + ';"></div>' +
                    '<select id="select-' + zoneIndex + '" onchange="selectZoneBulb(' + zoneIndex + ')">';

        for (var lightId in zoneGrid.activeLights) {
            var selected = '';
            if (zoneGrid.zones[zoneIndex] && zoneGrid.zones[zoneIndex].bulb && zoneGrid.zones[zoneIndex].bulb === lightId) {
                selected = " selected='selected' ";
            }
            html += "<option value='" + lightId + "' " + selected + ">" + zoneGrid.lightsMaster[lightId] + "</option>";
        }
        html += "</select><br/>";

        $('#zone-bulbs').append(html);
        $("#select-" + zoneIndex).on('change', function() {
            selectZoneBulb(zoneIndex);
        });
    }
}

function validateZone(corners) {
    //here you have the 2 point for the zone selection
    //so you could save that value for the calc matrix
    selectZone(corners, true); //update color and mark as selected
    corners.bulb = Object.keys(zoneGrid.activeLights)[0]; //add a default bulb
    zoneGrid.zones.push(corners); //add the zone in result
    updateZoneBulbs();
}

function saveGridResults(){
    $.ajax({
        url			: $SCRIPT_ROOT + zoneGrid.updateZonesUrl,
        method		: 'POST',
        contentType	: 'application/json;charset=UTF-8',
        data		: JSON.stringify(zoneGrid.zones),
        success: function (result) {
            console.log(result);
            buildGrid();
            notification(result['message']);
        },
        error: function (result) {
            console.log(result);
        }
    });
}

function toggleZone() {
    var zoneStateDiv = $("#zone-state"),
        settingCircle = $('#zoneBtn.setting-circle');

    if (zoneGrid.state) {
        zoneStateDiv.html("Off");
        zoneGrid.state = 0;
    } else {
        zoneStateDiv.html("On");
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