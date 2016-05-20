var zoneGrid = {
    'width'         : 16,
    'height'        : 9,
    'colors'        : [],
    'defaultColor'  : 'grey',
    'zones'         : [],
    'lightsMaster'  : [],
    'activeLights'  : [],
    'state'         : false
};

zoneGrid.init = function() {
    addBulbNamesToZones();
    generateColors();
    buildGrid();
    updateZoneGridActiveLights();

    $('#toggle-zone-mode').on('click', function() {
        toggleZone();
    });

    $('#restart').on('click', function() {
        zoneGrid.zones = [];
        selectionStarted = false;
        buildGrid();
        saveResults();
    });

    $('#save_zones').on('click', function() {
        saveResults();
    });
};

function addBulbNamesToZones() {
    for (var i in zoneGrid.zones) {
        var bulb = zoneGrid.zones[i].bulb;
        zoneGrid.zones[i].bulbName = zoneGrid.lightsMaster[bulb];
    }
}

function clearZone(zoneIndex) {
    console.log('Deleting Zone!');
    zoneGrid.zones.splice(zoneIndex, 1);
    buildGrid();
    saveResults();
}

function updateZoneGridActiveLights() {
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
    var luminosity = 'dark';
    for (var i=0; i<64; i++) {
        if (luminosity === 'dark') {
            luminosity = 'light';
        } else {
            luminosity = 'dark';
        }

        var color = randomColor({
            luminosity: luminosity
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

    for (var line_index=0; line_index<zoneGrid.height; line_index++) {
        //build each line
        var line_id = "line_" + line_index;
        grid.append("<div class='line' id='" + line_id + "' ></div>");
        for (var cell_index=0; cell_index<zoneGrid.width; cell_index++) {
            //build each column
            var line = $('#' + line_id),
                cell_id = "cell_" + line_index + "_" + cell_index;
            line.append("<div class='cell' id='" + cell_id + "' >&nbsp;</div>");

            var cell = $('#' + cell_id);
            //default color
            cell.css('background-color', zoneGrid.defaultColor);

            // Restore color if cell is from saved zone
            for (var i in zoneGrid.zones) {
                var zone = zoneGrid.zones[i];
                if (line_index >= zone.y1 && line_index <= zone.y2 && cell_index >= zone.x1 && cell_index <= zone.x2) {
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

//get the top left and bottom right corners from two cell
function getCorners(cellA, cellB) {
    return {
        'x1': Math.min(cellA.attr('id').split('_')[2], cellB.attr('id').split('_')[2]),
        'y1': Math.min(cellA.attr('id').split('_')[1], cellB.attr('id').split('_')[1]),
        'x2': Math.max(cellA.attr('id').split('_')[2], cellB.attr('id').split('_')[2]),
        'y2': Math.max(cellA.attr('id').split('_')[1], cellB.attr('id').split('_')[1])
    };
}

//preview mode
function cellOver() {
    if (selectionStarted) {
        var cur_cell = $(this),
            corners = getCorners(startCell, cur_cell);
        clearPixels();
        selectZone(corners, false); //just preview
    }
}

//on click, for start or stop selection
var selectionStarted = false,
    startCell, endCell;

function cellClick() {
    var cur_cell = $(this);
    //first click to start selection
    if (!selectionStarted) {
        startCell = cur_cell;
        markCell(cur_cell, true);
        selectionStarted = true;
    } else {
        //second click to end selection
        endCell = cur_cell;
        selectionStarted = false;
        var corners = getCorners(startCell, endCell);
        validateZone(corners);
    }
}

//clear unselected pixels
function clearPixels() {
    for (var line_index=0; line_index<zoneGrid.height; line_index++) {
        for (var cell_index=0; cell_index<zoneGrid.width; cell_index++) {
            //restoring default color
            var cur_cell = $('#cell_' + line_index + "_" + cell_index);
            if (!cur_cell.hasClass('selected')) {
                cur_cell.css('background-color', zoneGrid.defaultColor);
            }
            //restoring zone zone_colors
            $.each(zoneGrid.zones, function(zone_index, zone) {
                if (line_index >= zone.y1 && line_index <= zone.y2 && cell_index >= zone.x1 && cell_index <= zone.x2) {
                    cur_cell.css('background-color', zoneGrid.colors[zone_index]);
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
    for (var line_index=corners.y1; line_index<=corners.y2; line_index++) {
        for (var cell_index=corners.x1; cell_index<= corners.x2; cell_index++) {
            var cell_id = "cell_" + line_index + "_" + cell_index,
                cell = $('#' + cell_id);
            markCell(cell, validate);
        }
    }
}

function selectZoneBulb(zoneIndex) {
    var select = $("#select_" + zoneIndex);
    zoneGrid.zones[zoneIndex].bulb = select.val();
    zoneGrid.zones[zoneIndex].bulbName = zoneGrid.lightsMaster[select.val()];
    updateZoneBulbs();
}

// Builds the form for bulb selection
function updateZoneBulbs() {
    updateZoneGridActiveLights();

    $('#zone-bulbs').html('');
    for (var zoneIndex in zoneGrid.zones) {
        var html =  '<div class="zone-color-circle" style="background-color: ' + zoneGrid.colors[zoneIndex] + ';"></div>' +
                    '<select id="select_' + zoneIndex + '" onchange="selectZoneBulb(' + zoneIndex + ')">';

        for (var lightId in zoneGrid.activeLights) {
            var selected = '';
            if (zoneGrid.zones[zoneIndex] && zoneGrid.zones[zoneIndex].bulb && zoneGrid.zones[zoneIndex].bulb === lightId) {
                selected = " selected='selected' ";
            }
            html += "<option value='" + lightId + "' " + selected + ">" + zoneGrid.lightsMaster[lightId] + "</option>";
        }
        html += "</select><br/>";

        $('#zone-bulbs').append(html);
        $("#select_" + zoneIndex).on('change', function() {
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

function saveResults(){
    var zoneData = {
        'zoneState' : zoneGrid.state,
        'zones'     : JSON.stringify(zoneGrid.zones)
    };

    $.ajax({
        url			: $SCRIPT_ROOT + '/update-zones',
        method		: 'POST',
        contentType	: 'application/json;charset=UTF-8',
        data		: JSON.stringify(zoneData),
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
    var oldZones = zoneGrid.zones.slice(0),
        zoneState = $("#zone-state");

    zoneGrid.zones = [];
    if (zoneGrid.state === true) {
        zoneGrid.state = 0;
        zoneState.html("Off");
    } else {
        zoneGrid.state = 1;
        zoneState.html("On");

        if (oldZones) {
            zoneGrid.zones = oldZones;
        }
    }
    $('#zone_btn .setting-circle').removeClass('setting-clicked');
    saveResults();
}