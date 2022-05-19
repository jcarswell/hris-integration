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
      alert_error(ret_data['errors'].join('<br>'));
    } else if (typeof ret_data.errors === "string") {
      alert_error(ret_data['errors']);
    }
  } else {
    $('button:submit',focus).removeClass('btn-primary').removeClass('btn-danger').addClass('btn-success');
    $('#alert-container').addClass("d-none");
  }
}
function errorProcess(jqXHR,status,error,focus) {
  $('button:submit',focus).removeClass('btn-primary').addClass('btn-danger');
  alert_error(error,status)
}
function createAlert() {
  var alertBody = `<div class="alert" role="alert">
  <div id="alert-inner"></div>
  <button type="button" class="close" data-dismiss="alert" aria-label="Close">
    <span aria-hidden="true">&times;</span>
  </button>
</div>`
  $('#alert-container').html(alertBody);
}
function alert_success(msg,head) {
  if (head === undefined) {head = "Success:";}
  createAlert()
  $(".alert").addClass('alert-success');
  $("#alert-inner").html("<strong>"+head+"</strong><br>"+msg);
  $('#alert-container').removeClass('d-none');
  setTimeout(function(){$('#alert-container').addClass('d-none');},3500);
}
function alert_error(msg,head) {
  if (head === undefined) {head = "Error:";}
  createAlert()
  $(".alert").addClass('alert-danger');
  $("#alert-inner").html("<strong>"+head+"</strong><br>"+msg);
  $('#alert-container').removeClass('d-none');
}
function alert_warn(msg,head) {
  if (head === undefined) {head = "Warning:";}
  createAlert()
  $(".alert").addClass('alert-warning');
  $("#alert-inner").html("<strong>"+head+"</strong><br>"+msg);
  $('#alert-container').removeClass('d-none');
  setTimeout(function(){$('#alert-container').addClass('d-none');},10000);
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
  .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
}
function serialize_form(f) {
  var ret = []
  $(f).find('input').each(function(i,e) {
    if (e.type == "checkbox" || e.type == "radio") {
      ret.push({name:e.name,value:e.checked});
    } else {
      ret.push({name:e.name,value:e.value});
    }
  });
  $(f).find('select').each(function(i,e) {
    var selected = []
    $(e).find(':selected').each(function(e,i) {
      selected.push(e.value);
    });
    ret.push({name:e.name,value:selected});
  });
  return ret
}
function serialize_json(f,base_data) {
  var ret = {};
  if (base_data !== undefined) {ret = JSON.parse(JSON.stringify(base_data));}
  $(f).find('input').each(function(i,e) {
    if (e.type == "checkbox" || e.type == "radio") {
      ret[e.name] = e.checked;
    } else {
      ret[e.name] = e.value;
    }
  });
  $(f).find('select').each(function(i,e) {
    var selected = []
    $(e).find(':selected').each(function(i,s) {
      selected.push(s.value);
    });
    ret[e.name] = selected;
  });
  Object.keys(ret).forEach(function(k) {
    if (k.endsWith("-id")) {
      ret['id'] = ret[k];
      delete ret[k];
    } else if (k.endsWith("-primary")) {
      ret['primary'] = ret[k];
      delete ret[k];
    }
  });
  return ret
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
            return decodeURI(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
}
function reset_form(f) {
  $('input:not([type="hidden"])',f).not(':button,:submit,:reset').val('')
  .prop('checked',false).prop('selected',false);
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
      $('<input type="submit" name="submit-new" class="btn btn-primary" onclick="s_new($(this).closest(\'form\'))" style="margin: 4pt 0 0 auto;" value="Submit & New"/>')
      .insertBefore('button[name=submit]','.container');
      $('button[name=submit]').attr('style','margin: 4pt 0 0 4pt;');
    }
  }
  $('input[type=password]').attr('autocomplete','false')
  const csrftoken = getCookie('csrftoken')
  $.ajaxSetup({
    headers: { "X-CSRFToken": csrftoken }
  });
  $('#btn_back')[0].href = get_basepath()
});
