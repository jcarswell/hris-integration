function doneProcess(ret_data,focus) {
  $('.is-invalid',focus).removeClass("is-invalid");
  $('.alert').alert('close');
  createAlert();
  if (ret_data["status"] != "success") {
    $('button:submit',focus).removeClass('btn-primary').addClass('btn-danger');
    if (typeof ret_data['errors'] === 'string') {
      $('#alert-inner').html(ret_data['errors']);
    } else {
      $('#alert-inner').html(ret_data['errors'].join('<br>'));
    }
    $('.alert').addClass("alert-danger");
    ret_data.fields.forEach(e => {$('input[name="'+e+'"]').addClass('is-invalid');})
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

$('.alert').on('closed.bs.alert',function() {
  $('#alert-container').addClass('d-none');
  createAlert();
})
