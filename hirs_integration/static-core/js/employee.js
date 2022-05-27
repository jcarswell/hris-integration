const phoneTemplate = (phone) => {
    return `<div class="tab-pane fade" id="phone-${phone['id']}"
    role="tabpanel" aria-labelledby="phone-${phone['id']}-tab">
      <form id="phone-form-${phone['id']}" class="phone-form">
        <input type="hidden" name="id" value="${phone['id']}"/>
        <div class="form-row">
          <div class="form-group col-md-5">
            <label for="label">Label</label>
            <input type="text" name="label" value="${phone['label']}" class="form-control"
                   required/>
          </div>
          <div class="form-group col-md-5">
            <label for="number">Number</label>
            <input type="text" name="number" value="${phone['number']}" required
                   onkeypress="return is_num_key(event,this)" class="form-control"/>
          </div>
          <div class="form-group col-md-2">
            <label for="primary">Primary</label>
            <input type="checkbox" name="primary" class="form-control"/>
          </div>
        </div>
        <div class="form-row">
          <button type="submit" class="btn btn-primary mb-2">Update</button>
          <button type="button" class="btn btn-danger mb-2" onclick="delete_phone(${phone['id']})">
            <ion-icon name="trash"></ion-icon></i></button>
        </div>
      </form>
    </div>`
};
const phoneTabTemplate = (phone) => {
    return `<li class="nav-item">
    <a class="nav-link" id="phone-${phone['id']}-tab" data-toggle="tab" role="tab"
      aria-controls="phone-${phone['id']}" href="#phone-${phone['id']}" aria-selected="true">
      ${phone['label']}</a>
    </li>`
};
const phoneFormBase = {
    'label': '',
    'phone': '',
    'primary': false
};
const addressTemplate = (address) => {
    return `<div class="tab-pane fade" id="address-${address['id']}"
    role="tabpanel" aria-labelledby="address-${address['id']}-tab">
      <form id="address-form-${address['id']}" class="address-form">
        <input type="hidden" name="id" value="${address['id']}"/>
        <div class="form-group">
          <label for="label">Label</label>
          <input type="text" class="form-control" name="label" value="${address['label']}"
                 required>
        </div>
        <div class="form-group">
            <label for="primary">Primary</label>
            <input type="checkbox" name="primary" class="col-md-2"/>
        <div class="form-group">
          <label for="address">Address</label>
          <input type="text" class="form-control" name="street1" 
                 value="${address['street1']}" required>
          <input type="text" class="form-control" name="street2" 
                 value="${address['street2']}">
          <input type="text" class="form-control" name="street3" 
                 value="${address['street3']}">
        </div>
        <div class="form-group">
          <label for="city">City</label>
          <input type="text" class="form-control" name="city" value="${address['city']}"
                 required>
        </div>
        <div class="form-group">
          <label for="state">State or Province</label>
          <input type="text" class="form-control" name="province" 
                 value="${address['province']}" required>
        </div>
        <div class="form-group">
          <label for="postal_code">Postal Code or ZIP</label>
          <input type="text" class="form-control" name="postal_code" 
            value="${address['postal_code']}" required>
        </div>
        <div class="form-group">
          <label for="country">Country</label>
          <input type="text" class="form-control" name="country"
                 value="${address['country']}" required>
        </div>
        <div class="row">
          <button type="submit" class="btn btn-primary mb-2">Update</button>
          <button type="button" class="btn btn-danger mb-2" onclick="delete_address(${address['id']})">
            <ion-icon name="trash"></ion-icon></i></button>
        </div>
      </form>
    </div>`
};
const addressTabTemplate = (address) => {
    return `<li class="nav-item">
    <a class="nav-link" id="address-${address['id']}-tab" data-toggle="tab" role="tab"
      aria-controls="address-${address['id']}" href="#address-${address['id']}" aria-selected="true">
      ${address['label']}</a>
    </li>`
};
const addressFormBase = {
    'label': '',
    'street1': '',
    'street2': '',
    'street3': '',
    'city': '',
    'province': '',
    'postal_code': '',
    'country': '',
    'primary': false
};
const softwareTemplate = (software) => {
    return `<div class="modal-body">
    <form id="software-form-${software['id']}">
        <input type="hidden" name="id" value="${software['id']}"/>
        <div class="form-group">
            <label for="software">Software</label>
            <select name="software" class="form-control" disabled>
                <option value="${software['software']['id']}" selected>
                    ${software['software']['name']}</option>
            </select>
        </div>
        <div class="form-group">
            <label for="notes">Notes</label>
            <textarea class="form-control" name="notes" rows="3">${software['notes']}</textarea>
        </div>
        <div class="form-group">
            <label for="expiry_date">Expiry</label>
            <input type="date" class="form-control" name="expiry_date">
        </div>
    </form>
    </div>
    <div class="modal-footer">
    <button type="button" class="btn btn-secondary" data-dismiss="modal">Discard</button>
    <button type="button" class="btn btn-primary" onclick="update_software(this)">Save</button>
    <button type="button" class="btn btn-danger" onclick="delete_software(this)">Delete</button>
    </div>`
};
const softwareListTemplate = (software) => {
    return `<button id="software-${software['id']}" type="button"
                    class="list-group-item list-group-item-action"
                    onclick="edit_software(${software['id']})">
                    ${software['software']['name']}
            </button>`
}
const softwareNewTemplate = `<div class="modal-body">
    <form id="software-form-0">
        <div class="form-group">
            <label for="software">Software</label>
            <select class="form-control" name="software" required>
            </select>
        </div>
        <div class="form-group">
            <label for="notes">Notes</label>
            <textarea class="form-control" name="notes" rows="3"></textarea>
        </div>
        <div class="form-group">
            <label for="expiry_date">Expiry</label>
            <input type="date" class="form-control" name="expiry_date">
        </div>
    </form>
    </div>
    <div class="modal-footer">
    <button type="button" class="btn btn-secondary" data-dismiss="modal">Discard</button>
    <button type="button" class="btn btn-primary" onclick="update_software(this)">Save</button>
    </div>`;
const softwareFormBase = {
    'software': '',
    'notes': '',
    'expiry_date': ''
};
const selectTemplate = (row) => {
    return `<option value="${row['id']}">${row['text']}</option>`;
}
function valid_photo_check(e) {
    var photo = e.currentTarget;
    if (photo.files.length == 0 && photo.checkValidity() === false) {
        return false;
    }
    if (photo.files[0].size > 5000000) {
        $(photo).closest(".custom-file").find(".invalid-feedback")
        .removeClass("d-none")
        .text("File size must be less than 5MB");
        return false;
    }
    if (photo.files[0].type === 'image/jpeg') {
        return true;
    } else if (photo.files[0].type === 'image/png') {
        return true;
    } else {
        $(photo).closest(".custom-file").find(".invalid-feedback")
        .removeClass("d-none")
        .text("File type must be jpeg or png");
        return false;
    }
}
$('input[type=file]').on("change",function(e) {
    if (valid_photo_check(e)) {
        $(e.currentTarget).closest(".custom-file").find(".invalid-feedback")
        .addClass("d-none")
        .text("");
        $(e.currentTarget).closest(".custom-file").find(".custom-file-label")
        .text(e.currentTarget.files[0].name);
        let reader = new FileReader();
        reader.onload = function(e){
            $('#employee-photo').attr('src', e.target.result);
        }
        reader.readAsDataURL(this.files[0]);
    }
});
function is_num_key(e,f) {
    if (f.value.length === 10) {return false;}
    if (e.key.match("[0-9]")) {return true;}
    else {return false;}
}
function get_phones() {
    $.ajax({
        url: phones_url +'?employee='+employee_id,
        type: 'GET',
        dataType: 'json'
    })
    .done(function(data) {
        if (Object.keys(data).length > 0) {
            data.forEach(function(phone) {
                $("#phone-new").before(phoneTemplate(phone));
                $("#phone-new-li").before(phoneTabTemplate(phone));
                if (phone['primary']) {
                    $('#phone-'+phone['id']+'-tab').tab('show');
                    $('#phone-'+phone['id']).find('input[name=primary]').prop('checked', true);
                }
            });
        }
    })
    .fail(function(jqXHR,status,error) {
        alert_error("There was an error loading the page, please refresh.");
    });
    setTimeout(function() {
        $('.phone-form').on('submit', function(e) {submit_phone(e);});
    },500);
}
function delete_phone(id) {
    if ($('input[name="primary"]', '#phone-'+id).prop('checked')) {
        alert_error("Cannot delete primary phone number");
        return;
    }
    $.ajax({
        url: phones_url+id+'/',
        type: 'DELETE',
        dataType: 'json'
    })
    .done(function(data) {
        $('#phone-'+id).remove();
        $('#phone-'+id+'-tab').remove();
        $('.nav-tabs a:first','#phone').tab('show');
    })
    .fail(function(jqXHR,status,error) {alert_error("Failed to delete address ", error);});
}
function submit_phone(e) {
    e.preventDefault();
    var data = serialize_json(e.currentTarget, phoneFormBase);
    var id = $(e.currentTarget).find('input[name=id]');
    var url = phones_url;
    var method = 'POST';
    console.log(id)
    if (id.length > 0) {
        method = 'PUT';
        url += id[0].value+'/';
    } else {
        delete data['id'];
        data['primary'] = false;
    }
    data['employee'] = employee_id;
    $.ajax({
        method: method,
        url: url,
        data: data,
        dataType: 'json'
    })
    .done(function(res) {
        if (method === 'POST') {
            $("#phone-new").before(phoneTemplate(res));
            $("#phone-new-li").before(phoneTabTemplate(res));
            $("#phone-new").find("input").each(function(i,e) {e.value="";});     
            $('#phone-'+res['id']+'-tab').tab('show');
        } else {
            $("#phone-" + id).html(phoneTemplate(res));
            $(e.currentTarget).find('submit').addClass('btn-success').removeClass('btn-primary');
            setTimeout(function() {
                $(e.currentTarget).find('submit').addClass('btn-primary').removeClass('btn-success');
            },25000);
        }
        if (res['primary']) {
            $("input[name=primary]", '#phones').prop('checked', false);
            $("input[name=primary]", '#phones-'+res['id']).prop('checked', true);
        }
    })
    .fail(function(jqXHR,status,error) {alert_error("Failed to update/create phone ",error);});
}
function get_addresses() {
    $.ajax({
        url: address_url +'?employee='+employee_id,
        type: 'GET',
        dataType: 'json'
    })
    .done(function(data) {
        if (Object.keys(data).length > 0) {
            data.forEach(function(address) {
                $("#address-new").before(addressTemplate(address));
                $("#address-new-li").before(addressTabTemplate(address))
                if (address['primary']) {
                    $('#address-'+address['id']+'-tab').tab('show');
                    $('#address-'+address['id']).find('input[name=primary]').prop('checked', true);
                }
            });
        }
    })
    .fail(function(jqXHR,status,error) {
        alert_error("There was an error loading the page, please refresh.");
    });
    setTimeout(function() {
        $('.address-form').on('submit', function(e){submit_address(e);});
    },500);
};
function delete_address(id) {
    if ($('input[name="primary"]', '#address-'+id).prop('checked')) {
        alert_error("Cannot delete primary address");
        return;
    }
    $.ajax({
        url: address_url + id + '/',
        type: 'DELETE'
    })
    .done(function(data) {
        $('#address-'+id).remove();
        $('#address-'+id+'-tab').remove();
        $('.nav-tabs a:first','#address').tab('show');
    })
    .fail(function(jqXHR,status,error) {alert_error("Failed to delete address",error);});
}
function submit_address(e) {
    e.preventDefault();
    var data = serialize_json(e.currentTarget, addressFormBase);
    var id = $(e.currentTarget).find('input[name=id]');
    var url = address_url;
    var method = 'POST';
    if (id.length > 0) {
        method = 'PUT';
        url += id[0].value+'/';
    } else {
        delete data['id'];
        data['primary'] = false;
    }
    data['employee'] = employee_id;
    $.ajax({
        method: method,
        url: url,
        data: data,
        dataType: 'json'
    })
    .done(function(res) {
        if (method === 'POST') {
            $("#address-new").before(addressTemplate(res));
            $("#address-new-li").before(addressTabTemplate(res));
            $("#address-new").find("input").each(function(i,e) {e.value="";});
            $('#address-'+res['id']+'-tab').tab('show');
        } else {
            $("#address-" + id).html(addressTemplate(res));
            $(e.currentTarget).find('submit').addClass('btn-success').removeClass('btn-primary');
            setTimeout(function() {
                $(e.currentTarget).find('submit').addClass('btn-primary').removeClass('btn-success');
            },25000);
        }
        if (res['primary']) {
            $("input[name=primary]", '#addresses').prop('checked', false);
            $("input[name=primary]", '#addresses-'+res['id']).prop('checked', true);
        }
    })
    .fail(function(jqXHR,status,error) {alert_error("Failed to update/create address ",error);});
}
function strip_id(t) {
    return Number(t.replace(/id_/g, ''));
}
var software = {}
function get_software() {
    $.ajax({
        url: accounts_url +'?employee='+employee_id,
        type: 'GET',
        dataType: 'json'
    })
    .done(function(data) {
        if (Object.keys(data).length) {
            data.forEach(function(i) {
                software[i['id']] = i;
                $("#software-list").append(softwareListTemplate(i));
            });
        }
    })
    .fail(function(jqXHR,status,error) {
        alert_error("There was an error loading the page, please refresh.");
    });
}
function edit_software(id) {
    $('.modal-header').after(softwareTemplate(software[id]));
    $('.modal-title').text('Edit Software');
    $("#modal-default").modal('show');
}
function add_software() {
    $('.modal-header').after(softwareNewTemplate);
    $('.modal-title').text('Add Software');
    populate_select('software');
    $("option[value='false']").remove();
    $("#modal-default").modal('show');
}
function update_software(e) {
    var f = $(e).closest('.modal-content').find('form')[0];
    var data = serialize_json(f, softwareFormBase);
    var id = $(f).find('input[name=id]');
    var url = accounts_url;
    var method = 'POST';
    if (id.length > 0) {
        method = 'PUT';
        url += id[0].value + '/';
    }
    data['software'] = strip_id(data['software'][0]);
    data['employee'] = employee_id;
    $.ajax({
        method: method,
        url: url,
        data: data,
        dataType: 'json'
    })
    .done(function(r) {
        if (method === 'POST') {
            $("#software-list").append(softwareListTemplate(i));
            software[r['id']] = r;
        }
        $(e).closest('.modal').modal('hide');
    })
    .fail(function(jqXHR,status,error) {alert_error("Failed to update software ",error);});
}
function delete_software(e) {
    var id = $(e).closest('.modal-content').find('id')[0].val();
    $.ajax({
        method: 'DELETE',
        url: software_url + id + '/',
        dataType: 'json'
    })
}
$(".modal").on("hidden.bs.modal", function() {
    $('.modal-body').remove();
    $('.modal-footer').remove();
})
$("#employee-form input[type=file]").on("change",function(e) {
    form = $(e.currentTarget).closest('form');
    if (validCheck() === false) {
        $(e.currentTarget).addClass('is-invalid');
        $(e.currentTarget).attr('type',false).attr('type','file');
    } else {
        $(e.currentTarget).removeClass('is-invalid');
        $('button',form).attr('disabled',false);
        $('label[for=photo]',form).text(this.files[0].name);
        var r = new FileReader();
        r.onload = function(e) {
            $('img',form).attr('src',e.target.result);
        }
        r.readAsDataURL(this.files[0]);
    }
})
$("#edit").on("submit",function(e) {
    e.preventDefault();
    form = new FormData(this);
    $.ajax({
        method: "POST",
        url: location.pathname,
        data: form,
        cache: false,
        processData: false,
        contentType: false
    })
    .done(function(r) {doneProcess(r,this);})
    .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
});
function revert_field(e) {
    $('input[name="'+e+'"]').val(employee_import[e]);
    $('input[name="'+e+'"]').closest('.input-group').find('.input-group-append').remove()
}
function revert_select(e) {
    if (typeof(employee_import[e]) === 'string') {
        $('select[name="'+e+'"]').selectpicker('val',e);
    } else if (employee_import[e][0] === undefined) {
        $('select[name="'+e+'"]').selectpicker('deselectAll');   
    } else if (typeof(employee_import[e]) === 'object') {
        $('select[name="'+e+'"]').selectpicker('val',employee_import[e]);
    }
    $('select[name="'+e+'"]').closest('.input-group').find('.input-group-append').remove()
}
function employee_undo() {
    if (employee_import === false) {return}
    Object.keys(employee_import).forEach(function(e) {
        var t = $('input[name=' + e + ']');
        if (t.val() === undefined) {
            t = $('select[name=' + e + ']');
        }
        if (t.val() != employee_import[e] && ["","None"].indexOf(employee_import[e]) === -1) {
            console.log(t.val(), employee_import[e]);
            var action;
            if (t.is('select')) {
                action = 'revert_select';
            } else {
                action = 'revert_field';
            }
            t.after(`<div class="input-group-append">
                        <button class="btn btn-outline-secondary" type="button"
                            onclick="${action}('${e}')">
                            <i class="fa-solid fa-clock-rotate-left"></i>
                        </button>
                    </div>`);
        }
    });
}
function populate_select(field,url) {
    var s = [];
    var select = $('select[name='+field+']');
    if (url === undefined) {
        url = window["select_" + field + "_url"];
    }
    $(select).find('option').each(function (i,f) {s.push(f.value);});
    $.ajax({
        method: "GET",
        url: url,
        dataType: 'json'
    })
    .done(function(res) {
        if (res.length > 0) {
            res.forEach(function (e,i) {
                if (s.indexOf(e['id']) === -1) {select.append(selectTemplate(e));}
            });
        }
    })
    .fail(function(jqXHR,status,error) {
        alert_error("There was an error loading the page, please refresh." + error);
    });
    $(select).selectpicker({
        style: '',
        styleBase: 'form-control'
    });
    setTimeout(function(){$(select).selectpicker('refresh');},200);
}