const phoneTemplate = (phone) => {
    return `<div class="row mb-1 phone-field" id="phone-${phone.id}">
      <input type="hidden" name="id" value="${phone.id}"/>
      <input type="text" name="label" value="${phone.label}" class="col-md-4"/>
      <input type="text" name="number" value="${phone.number}"
      onkeypress="return is_num_key(event,this)" class="col-md-4"/>
      <input type="radio" name="phone-primary" class="col-md-2"/>
      <div class="col-md-2 phone-actions d-flex flex-row">
        <button type="button" class="btn btn-danger" onclick="delete_phone(${phone.id})"
          name="delete">
          <ion-icon name="trash"></ion-icon></button>
      </div>
    </div>`
};
const phoneUpdateButton = (id) => {
    return `<button type="button" class="btn btn-primary" onclick="update_phone(${id})" name="update"> 
      <ion-icon name="add"></ion-icon></button>`
};
const phoneNewTemplate = `<div class="row mb-1 phone-field" id="phone-0">
      <input type="hidden" name="id" value="0"/>
      <input type="text" name="label" class="col-md-4"/>
      <input type="text" name="number" onkeypress="return is_num_key(event,this)" 
        class="col-md-4"/>
      <div class="col-md-2 phone-actions d-flex flex-row">
        <button type="button" class="btn btn-primary" onclick="update_phone(0)" name="update">
          <ion-icon name="add"></ion-icon></button>
      </div>
    </div>`;
const addressTemplate = (address) => {
    return `<div class="tab-pane fade show active" id="address-${address.id}" role="tabpanel" 
    aria-labelledby="address-new-tab">
      <form id="address-form-${address.id}">
        <div class="form-group">
          <label for="label">Label</label>
          <input type="text" class="form-control" name="label" value="${address.label}">
        </div>
        <div class="form-group">
            <label for="address-primary">Primary</label>
            <input type="radio" name="address-primary" class="col-md-2"/>
        <div class="form-group">
          <label for="address">Address</label>
          <input type="text" class="form-control" name="street1" value="${address.street1}">
          <input type="text" class="form-control" name="street2" value="${address.street2}">
          <input type="text" class="form-control" name="street3" value="${address.street3}">
        </div>
        <div class="form-group">
          <label for="city">City</label>
          <input type="text" class="form-control" name="city" value="${address.city}">
        </div>
        <div class="form-group">
          <label for="state">Province or State</label>
          <input type="text" class="form-control" name="province" value="${address.city}">
        </div>
        <div class="form-group">
          <label for="postal_code">Postal Code or ZIP</label>
          <input type="text" class="form-control" name="postal_code" 
            value="${address.postal_code}">
        </div>
        <div class="form-group">
          <label for="country">Country</label>
          <input type="text" class="form-control" name="country" value="${address.country}">
        </div>
      </form>
      <div class="row">
        <button type="submit" class="btn btn-primary mb-2" onclick="update_address(${address.id})">
          Update</button>
        <button type="button" class="btn btn-danger mb-2" onclick="delete_address(${address.id})">
          <ion-icon name="trash"></ion-icon></i></button>
      </div>
    </div>`
};
const softwareTemplate = (software) => {
    return `<div class="modal-body">
    <form id="software-form-${software.id}">
        <input type="hidden" name="id" value="${software.id}"/>
        <div class="form-group">
            <label for="software">Software</label>
            <input type="text" class="form-control" name="software"
                value="${software.software}" disabled>
        </div>
        <div class="form-group">
            <label for="notes">Notes</label>
            <textarea class="form-control" name="notes" rows="3">${software.notes}</textarea>
        </div>
        <div class="form-group">
            <label for="expiry_date">Expiry</label>
            <input type="date" class="form-control" name="expiry_date">
        </div>
    </form>
    </div>`
};
const softwareNewTemplate = `<div class="modal-body">
    <form id="software-form-0">
        <div class="form-group">
            <label for="software">Software</label>
            <select class="form-control" name="software" required></select>
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
    </div>`;
const modalActionsSoftware = `<div class="modal-footer">
    <button type="button" class="btn btn-secondary" data-dismiss="modal">Discard</button>
    <button type="button" class="btn btn-primary" onclick="update_software(this)">Save</button>
    <button type="button" class="btn btn-danger" onclick="delete_software(this)">Delete</button>
    </div>`;
function valid_photo_check() {
    var photo = $("input[type=file]")[0]
    if (photo.files.length == 0 && photo.checkValidity === false) {
        return false;
    }
    if (photo.files[0].size > 5000000) {
        $(photo).closest("form-group").find(".invalid-feedback")
        .removeClass("d-none")
        .text("File size must be less than 5MB");
        return false;
    }
    if (photo.files[0].type === 'image/jpeg') {
        return true;
    } else if (photo.files[0].type === 'image/png') {
        return true;
    } else {
        $(photo).closest("form").find(".invalid-feedback")
        .removeClass("d-none")
        .text("File type must be jpeg or png");
        return false;
    }
}
$('input[type=file]').on("change",function() {valid_photo_check()});
function is_num_key(e,f) {
    if (f.value.length === 10) {return false;}
    if (e.key.match("[0-9]")) {return true;}
    else {return false;}
}
function revert_field(e) {
    $('input[name="'+e+'"]').val(employee_import.e);
}
function add_phone() {
    $($('.phone-field', '#phones').last())
        .after(phoneNewTemplate);
    $('#addphone').remove();
}
function get_phones() {
    $.ajax({
        url: phones_url,
        type: 'GET',
        dataType: 'json'
    })
    .done(function(data) {
        if (Object.keys(data).length > 0) {
            Object.keys(data).forEach(function(k,i) {
                $("#phone-end").before(phoneTemplate(data[k]));
                if (data[k].primary) {
                    $('input[name="phone-primary"]', '#phone-'+data[k].id).prop('checked', true);
                }
            });
            $($('.btn-danger','#phones').last())
            .after('<button id="addphone" type="button" class="btn btn-primary" onclick="add_phone()"> \n\
                <ion-icon name="add"></ion-icon></button>');
            $('#phone-end').remove();
        }
    })
    .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
}
function delete_phone(id) {
    $.ajax({
        url: phones_update_url+'/'+id,
        type: 'DELETE',
        dataType: 'json'
    })
    .done(function(data) {
        $('#phone-'+id).remove();
    })
    .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
}
$('.phone-field input[type=text]').on("change",function(e) {
    console.log("Trigger phone change")
    f = $(e.currentTarget).closest('.phone-field');

    if (f.children('input[name=label]').val() == '') {
        f.children('input[name=label]').addClass('is-invalid');
        return false;
    } else {
        f.children('input[name=label]').removeClass('is-invalid');
    }
    if (f.children('button[name=update]').length === 0) {
        $('button',f).before(phoneUpdateButton(f.find('input[name=id]').val()));
    }
});
function update_phone(id) {
    f = $('#phone-'+id);
    var data = {}
    var url = phones_update_url+'/'+id;
    var method = 'PUT';
    f.children('input').not('input:radio').each(function(i,e) {
        data[e.name] = f.value;
    });
    if (id == 0) {
        delete data['id'];
        url = phones_url;
        method = 'POST';
    }
    $.ajax({
        method: method,
        url: url,
        data: data,
    })
    .done(function(r) {
        if (r["status"] == "success") {
            f.replaceWith(phoneTemplate(r));
            $($('.phone-actions').last())
            .after('<button id="addphone" type="button" class="btn btn-primary" onclick="add_phone()">\n\
                <ion-icon name="add"></ion-icon></button>\n');          
        } else {
            $(this).addClass('is-invalid');
            alert('Error' + r.message);
        }
    })
    .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
}
$('input[name=phone-primary]').on("change",function(e) {
    var f = $(e.currentTarget).closest('.phone-field');
    $.ajax({
        method: "PATCH",
        url: phones_update_url+'/'+f.find('input[name=id]').val(),
        data: JSON.parse({id: f.attr('id'), primary: true}),
        dataType: 'json'
    })
    .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
})
function get_addresses() {
    $.ajax({
        url: addresses_url,
        type: 'GET',
        dataType: 'json'
    })
    .done(function(data) {
        if (Object.keys(data).length > 0) {
            data.forEach(function(address) {
                $("#address-new").before(softwareTemplate(address));
                if (address.primary) {
                    $('input[name="address-primary"]', '#address-'+address.id).prop('checked', true);
                }
            });
        } else {
            add_phone();
        }
    })
    .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
};
function update_address(id) {
    var data = serialize_json($('address-' + id));
    $.ajax({
        method: "PUT",
        url: addresses_update_url +'/'+ data['id'],
        data: data,
        dataType: 'json'
    });
}
function delete_address(id) {
    $.ajax({
        url: addresses_update_url+'/'+id,
        type: 'DELETE',
        dataType: 'json'
    })
    .done(function(data) {
        $('#address-'+id).remove();
    })
    .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
}
$('#address-form-0').on('submit', function(e) {
    e.preventDefault();
    var data = serialize_json(this);
    delete data['id'];
    $.ajax({
        method: "POST",
        url: address_url,
        data: data,
        dataType: 'json'
    })
    .done(function(r) {
        doneProcess(r, this);
        if (r["status"] == "success") {
            $(this).children('input').reset();
        }
    })
    .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
});
$('input[name=address-primary]').on("change",function(e) {
    var f = $(e.currentTarget).closest('.form');
    $.ajax({
        method: "PATCH",
        url: address_update_url+'/'+f.find('input[name=id]').val(),
        data: JSON.parse({id: f.attr('id'), primary: true}),
        dataType: 'json'
    })
    .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
})
var software = {}
function get_software() {
    $.ajax({
        url: software_url,
        type: 'GET',
        dataType: 'json'
    })
    .done(function(data) {
        if (Object.keys(data).length > 0) {
            $('#software-end').html('<button id="delete-me" class="d-none"/>');
            data.forEach(function(i) {
                software[i.id] = i;
                $("#delete-me").before('<button id="software-${i.id}" type="button" ' +
                    'class="list-group-item list-group-item-action" '+
                    'onclick="edit_software(${i.id})">${i.name}</button>');
            });
            $('#delete-me').remove();
            $('#software-end').attr('class','list-group')
        } else {
            add_phone();
        }
    })
    .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
};
function edit_software(id) {
    $('.modal-header').after(softwareTemplate(software[id]));
    $('.modal-title').text('Edit Software');
    $('.modal-body').after(modalActionsSoftware);
    $("#modal-default").modal('show');
}
function add_software() {
    $('.modal-header').after(softwareNewTemplate);
    $('.modal-title').text('Add Software');
    $('.modal-body').after(modalActionsSoftware);
    $('#software-form-0 input[type=select]').select2({
      placeholder: 'Select a software',
      ajax: {
        url: select_software_url,
        dataType: 'json',
        delay: 250,
        data: function (params) {
          return {
            q: params.term, // search term
            page: params.page
          };
        },
        processResults: function (data, params) {
          params.page = params.page || 1;
          return {
            results: data.results,
            pagination: {
            more: (params.page * 30) < data.total_count
            }
          };
        },
        cache: true
      },
      escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
      minimumInputLength: 1,
      theme: 'bootstrap4'
    });
    $("#modal-default").modal('show');
}
function update_software(e) {
    var data = serialize_json($(e).closest('.modal-content').find('form')[0]);
    var url = software_update_url +'/'+ data['id'];
    var method = 'PUT';
    if (data['id'] == '0') {
        delete data['id'];
        url = software_url;
        method = 'POST';
    }
    $.ajax({
        method: method,
        url: url,
        data: data,
        dataType: 'json'
    })
    .done(function(r) {
        if (r["status"] == "success") {
            $(e).closest('.modal').modal('hide');
        }
        if (data['id'] == '0') {
            $('#software-end').last(softwareTemplate(r));
            software[r.id] = r;
        }
    })
    .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
}
function delete_software(e) {
    var id = $(e).closest('.modal-content').find('id')[0].val();
    $.ajax({
        method: 'DELETE',
        url: software_update_url +'/'+ id,
        dataType: 'json'
    })
}
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
$("form",'.container').on("submit",function(e) {
    e.preventDefault();
    form = $(this);
    data = serialize_form(form);
    data.push({name:'form',value:'override'});

    $.ajax({
        method: "POST",
        url: location.href,
        data: data,
    })
    .done(function(r) {doneProcess(r,form);})
    .fail(function(jqXHR,status,error) {errorProcess(jqXHR,status,error);});
});
$(document).on("ready",function () {
    ['location','primary_job','jobs'].forEach(function(e) {
        t = $("#" + field);
        t.select2({
        ajax: {
            url: $("select_" + field + "_url"),
            dataType: 'json',
            delay: 250,
            data: function (params) {
            return {
                q: params.term, // search term
                page: params.page
            };
            },
            processResults: function (data, params) {
            params.page = params.page || 1;
            return {
                results: data.results,
                pagination: {
                more: (params.page * 30) < data.total_count
                }
            };
            },
            cache: true
        },
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        minimumInputLength: 1,
        theme: 'bootstrap4'
        });
    });
    employee_import.forEach(function(e,i) {
       t = $('input[name=' + e + ']');
       if (t.val() != employee_import.e) {
           t.after('<div class="input-group-append"> \n\
                <button class="btn btn-outline-secondary" type="button" onclick="revert_field(' + e + ')"> \n\
                <i class="fa-solid fa-angles-down"></i></button></div>');
       }
    });
    get_phones();
    get_addresses();
    get_software();
});
