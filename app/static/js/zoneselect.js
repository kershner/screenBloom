//settings for the visual grid
grid_width = 16;
grid_height = 9;
zone_colors = ['green', 'blue', 'black', 'yellow', 'cyan', 'pink','red','orange'];
default_color = 'grey';

//build the grid, and place click event
function startGrid() {
  var grid = $('#grid');
  grid.html(''); //clear grid
  updateComboForm();//clear result
  var line_index = 0;
  for (line_index = 0; line_index < grid_height; line_index++) {
    //build each lines
    line_id = "line_" + line_index;
    grid.append("<div class='line' id='" + line_id + "' ></div>");
    for (row_index = 0; row_index < grid_width; row_index++) {
      //build each colums
      line = $('#' + line_id);
      row_id = "row_" + line_index + "_" + row_index;
      line.append("<div class='row' id='" + row_id + "' >&nbsp;</div>");
      row = $('#' + row_id);
      //default color
      row.css('background-color', default_color);
      //restore colour if zone is got from config
      $.each(zones,function(zone_index,zone){
        console.log('test zone');
        if( line_index >= zone.y1 && line_index <= zone.y2 && row_index >= zone.x1 && row_index <= zone.x2){
          console.log('found');
          row.css('background-color', zone_colors[zone_index]);
        }
      });
      //place event
      row.on('click', cellClick);
      row.on('mouseover', cellOver);
    };
  }
}

//get the top left and bottom right corners from two cell
function getCorners(cellA, cellB) {
  var x1 = Math.min(cellA.attr('id').split('_')[2], cellB.attr('id').split('_')[2]);
  var x2 = Math.max(cellA.attr('id').split('_')[2], cellB.attr('id').split('_')[2]);
  var y1 = Math.min(cellA.attr('id').split('_')[1], cellB.attr('id').split('_')[1]);
  var y2 = Math.max(cellA.attr('id').split('_')[1], cellB.attr('id').split('_')[1]);
  return {
    'x1': x1,
    'y1': y1,
    'x2': x2,
    'y2': y2
  };
}

//preview mode
function cellOver() {
  if (selectionStarted) {
    var cur_cell = $(this);
    var corners = getCorners(startCell, cur_cell);
    clearPixels();
    selectZone(corners, false); //just preview
  }
}

//on click, for start or stop selection
var selectionStarted = false;
var startCell, endCell;
function cellClick() {
  var cur_cell = $(this);
  //first click to start selection
  if (!selectionStarted) {
    startCell = cur_cell;
    markCell(cur_cell,true);
    selectionStarted = true;
  }
  //second click to end selection
  else {
    endCell = cur_cell;
    selectionStarted = false;
    var corners = getCorners(startCell, endCell);
    validateZone(corners);
  }
}

//clear unselected pixels
function clearPixels() {
  for (line_index = 0; line_index < grid_height; line_index++) {
    for (row_index = 0; row_index < grid_width; row_index++) {
      //restoring default color
      var cur_cell = $('#row_' + line_index + "_" + row_index);
      if (!cur_cell.hasClass('selected')) {
        cur_cell.css('background-color', default_color);
      }
      else{
      	//restoring zone zone_colors
      	$.each(zones,function(zone_index,zone){
        	if( line_index >= zone.y1 && line_index <= zone.y2 && row_index >= zone.x1 && row_index <= zone.x2){
          	cur_cell.css('background-color', zone_colors[zone_index]);
          }
        });
      }
    }
  }
}

function markCell(cell,validate){
	if (validate == true)
    cell.addClass('selected');
  cell.css('background-color', zone_colors[zones.length]);
}

//change the color of cells, and add class 'selected' if validate is true
function selectZone(corners, validate) {
  for (line_index = corners.y1; line_index <= corners.y2; line_index++) {
    for (row_index = corners.x1; row_index <= corners.x2; row_index++) {
      cell_id = "row_" + line_index + "_" + row_index;
      cell = $('#' + cell_id);
      markCell(cell,validate);
    };
  }
}

function selectZoneBulb(zone_index){
	var select = $("#select_"+zone_index);
	//var select = $(this);
  //var zone_index = select.attr['id'].split('_')[1];
  zones[zone_index].bulb = select.val();
  updateComboForm();
}

function updateComboForm(){
  //builds the form for bulb selection
  $('#combo').html('');
  $.each(zones,function(zone_index,elem){
  	html = "<label for='select_"+zone_index+"'>Zone "+zone_colors[zone_index]+": </label><select id='select_"+zone_index+"' onchange='selectZoneBulb("+zone_index+")'>";
    $.each(available_lights,function(index_light,name){
    	var selected = '';
      if(zones[zone_index] && zones[zone_index].bulb && zones[zone_index].bulb == index_light){
      	selected = " selected='selected' ";
      }
    	html += "<option value='"+index_light+"' "+selected+">"+name+"</option>";
    });
		html += "</select><br/>";
    $('#combo').append(html);
    $("#select_"+zone_index).on('change',function(){
    	selectZoneBulb(zone_index);
    });
  });
}

function saveResults(){
  console.log('Saving Zones')
  //verify if no bulb is used twice
  var used_bulbs = {};
  var found = false;
  zones.forEach(function(zone){
    if( typeof used_bulbs[zone.bulb] !== 'undefined' ){
      found = true;
    }
    else{
      used_bulbs[zone.bulb] = true;
    }
  });
  if(found){
    alert("Each bulb must be assign to only one zone");
    return false;
  }
  else{
    $.ajax({
  		url			: $SCRIPT_ROOT + '/update-zones',
  		method		: 'POST',
  		contentType	: 'application/json;charset=UTF-8',
  		data		: JSON.stringify(zones),
  		success: function (result) {
  			console.log(result)
  		},
  		error: function (result) {
  			console.log(result);
  		}
  	});
  }
}

function validateZone(corners){
  //here you have the 2 point for the zone selection
  //so you could save that value for the calc matrix
  selectZone(corners, true); //update color and mark as selected
  corners.bulb = Object.keys(available_lights)[0]; //add a default bulb
  zones.push(corners);//add the zone in result
  updateComboForm();
}

function toggleZone(){
  if(zone_state_val === true){
    console.log('disactivating multiple zones')
    zone_state_val = false;
    $("#zone_state").html("Off");
    $('#zone_select').hide();
    old_zones = zones.slice(0);
    zones = [];
  }
  else{
    console.log('activating multiple zones')
    zone_state_val = true;
    $("#zone_state").html("On");
    $('#zone_select').show();
    if(typeof old_zones !== 'undefined'){
      zones = old_zones;
    } else {
      zones = [];
    }
  }
  $('#zone_btn .setting-circle').removeClass('setting-clicked');
  saveResults();
}
