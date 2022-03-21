// Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
// GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 


function isInt(value) {
  var x;
  if (isNaN(value)) {
    return false;
  }
  x = parseFloat(value);
  return (x | 0) === x;
}

function get_basepath() {
  var loc = location.pathname.split('/');
  loc.pop();
  if (isInt(loc[loc.length-1])) {
    loc.pop();
  }
  return loc.join('/') + '/';
}

function get_id() {
  var loc = location.pathname.split('/');
  loc.pop();
  if (isInt(loc[loc.length-1])) {
    return parseInt(loc[loc.length-1]);
  }
  return undefined;
}

function set_nav() {
  var loc = get_basepath();
  if (loc !== '/') {
    $('nav li a').each(function() {
      $this = $(this)[0];
      ref = $this.getAttribute('href');
      if (ref !== null && ref.indexOf(loc) !== -1) {
        $this.setAttribute('class',$this.className + ' active');
      }
    });
  }
}

$(function() {
  set_nav();
  $('input[type=password]').attr('autocomplete','false')
});