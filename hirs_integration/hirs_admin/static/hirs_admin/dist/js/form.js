// Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
// GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 


function doneProcess(ret_data,focus) {
  $('.is-invalid',focus).removeClass("is-invalid");
  $('.alert').alert('close');
  createAlert();
  if (ret_data["status"] != "success") {
    $('button:submit',focus).removeClass('btn-primary').addClass('btn-danger');
    if (Array.isArray(ret_data.fields)) {
      ret_data.fields.forEach(e => {$('input[name="'+e+'"]').addClass('is-invalid');})
    }
    if (Array.isArray(ret_data['errors'])) {
      $('#alert-inner').html(ret_data['errors'].join('<br>'));
    } else if (typeof ret_data.errors === "string") {
      $('#alert-inner').html(ret_data['errors']);
    }
    $('.alert').addClass("alert-danger");
    $('#alert-container').removeClass('d-none')
  } else {
    $('button:submit',focus).removeClass('btn-primary').removeClass('btn-danger').addClass('btn-success');
    $('#alert-container').addClass("d-none");
  }
}
function errorProcess(jqXHR,status,error,focus) {
  $('button:submit',focus).removeClass('btn-primary').addClass('btn-danger');
  $('#alert-container').removeClass('d-none');
  $(".alert").addClass('alert-danger');
  $("#alert-inner").html("<storng>"+status+":</strong> "+error);
}
function createAlert() {
  var alertBody = `  <div class="alert" role="alert">
  <div id="alert-inner"></div>
  <button type="button" class="close" data-dismiss="alert" aria-label="Close">
    <span aria-hidden="true">&times;</span>
  </button>
</div>`
  $('#alert-container').html(alertBody);
}
function is_new() {
  if (isNaN(get_id())) {return undefined;}
  else if (get_id() > 0) {return false;}
  else {return true;}
}
function do_delete() {
  $.ajax({
    method: "delete",
    url: location.href,
    })
  .done(function(data){
    location.replace(get_basepath());
  })
  .fail(function(jqXHR,Status,error) {errorProcess(jqXHR,status,error);});
}
function serialize_form(f) {
  d=$(f).serializeArray();
  $("input:disabled",f).each(function(i,e) {
    d.push({name:e.name,value:e.value});
  })
  $("input[type=checkbox]:not(:checked)",f).each(function(i,e) {
    d.push({name:e.name,value:"off"});
  })
  return d;
}
function getCookie(c_name)
{
    if (document.cookie.length > 0)
    {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1)
        {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
}
$('.alert').on('closed.bs.alert',function() {
  $('#alert-container').addClass('d-none');
  createAlert();
})
var snew = false;
function s(e) {return undefined;}
function s_new(e) {snew = true;}
var id = $('#form_list input[type=number]')[0]
$(function() {
  if (is_new()) {
    if (id !== undefined) {
      id.disabled = false;
      id.readOnly = false;
      //$('<input type="submit" name="submit-new" class="btn btn-primary" style="margin: 4pt 0 0 auto;" value="Submit & New"/>').insertBefore($('input[name=submit]'));
      //$('button[name=submit]').attr('style','margin: 4pt 0 0 4pt;');
    }
  }
  const csrftoken = getCookie('csrftoken')
  $.ajaxSetup({
    headers: { "X-CSRFToken": csrftoken }
  });
  $('#btn_back')[0].href = get_basepath()
});
