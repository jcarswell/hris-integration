// Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
// GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 
function doneProcess(ret_data,focus) {
  $('.is-invalid',focus).removeClass("is-invalid");
  $('.alert').alert('close');
  createAlert();
  if (ret_data["status"] === "error") {
    Object.keys(ret_data).forEach(function (key) {
      if (key === "errors") {
        alert_error(ret_data[key]);
        alert_triggered = true;
      } else if (key === "fields") {
        for (var i = 0; i < ret_data[key].length; i++) {
          $('[name="'+ret_data[key][i]+'"]',focus).addClass('is-invalid')
          .selectpicker("setStyle");
        }
      }
      else {
        $('[name="'+ret_data[key]+'"]',focus).addClass('is-invalid')
          .selectpicker("setStyle");
        $('[name="'+ret_data[key]+'"]',focus)
          .after('<div class="invalid-feedback">' + ret_data[key] + "</div>");
      }
    });
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
    $('button:submit',focus).removeClass('btn-primary').removeClass('btn-danger')
      .addClass('btn-success');
    $('#alert-container').addClass("d-none");
  }
}
function errorProcess(jqXHR,status,error,focus) {
  console.log(jqXHR);
  console.log(status);
  console.log(error);
  if (focus === undefined) {focus = $('body');}
  var alert_triggered = false;
  if (jqXHR.responseJSON === undefined) {
    if (jqXHR.responseText !== undefined) {
      alert_error(jqXHR.responseText);
    } else {
      alert_error(`An error has occurred. Server returned status ${jqXHR.status}`);
    }
    return;
  }
  Object.keys(jqXHR.responseJSON).forEach(function (key) {
    if (key === "errors") {
      alert_error(jqXHR.responseJSON[key]);
      alert_triggered = true;
    } else if (key === "fields") {
      for (var i = 0; i < jqXHR.responseJSON[key].length; i++) {
        $('input[name="'+jqXHR.responseJSON[key][i]+'"]',focus).addClass('is-invalid');
      }
    }
    else {
      $('input[name="'+jqXHR.responseJSON[key][i]+'"]',focus).addClass('is-invalid');
    }
  });
  if (!alert_triggered) {
    alert_error("Please check the form for errors.");
  }
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
    if (url_params.has('next')) {
      href = url_params.get('next');
    } else if (url_params.has('last')) {
      href = url_params.get('last');
    } else {
      location.replace(get_basepath());
    }
  })
  .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
}
function serialize_form(f) {
  var ret = new FormData();
  $(f).find('input').each(function(i,e) {
    if (e.name == "" || e.name === undefined) {}
    else if (e.type === "checkbox" || e.type === "radio") {
      ret.append(e.name,e.checked);
    } else {
      if (e.value === "" || e.value === undefined) {
        ret.append(e.name,null);
      } else {
        ret.append(e.name,e.value);
      }
    }
  });
  $(f).find('select').each(function(i,e) {
    var selected = []
    $(e).find(':selected').each(function(i,s) {
      selected.push(s.value);
    });
    if (selected.length > 0) {
      ret.append(e.name,selected);
    }
  });
  $(f).find('textarea').each(function(i,e) {
    ret.append(e.name,e.value);
  });
  $(f).find('input[type="file"]').each(function(i,e) {
    ret.append(e.name,e.files[0],e.files[0].name);
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
  $(f).find('textarea').each(function(i,e) {
    ret[e.name] = e.value;
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
      $('<input type="submit" name="submit-new" class="btn btn-primary" ' + 
        'onclick="s_new($(this).closest(\'form\'))" style="margin: 4pt 0 0 auto;" ' +
        'value="Submit & New"/>')
        .insertBefore('button[name=submit]','.container');
      $('button[name=submit]').attr('style','margin: 4pt 0 0 4pt;');
    }
  }
  $('input[type=password]').attr('autocomplete','false')
  const csrftoken = getCookie('csrftoken')
  $.ajaxSetup({
    headers: { "X-CSRFToken": csrftoken }
  });
  if (url_params.has('last')) {
    $('#btn_back')[0].href = url_params.get('last');
  } else {
    $('#btn_back')[0].href = get_basepath();
  }
});
