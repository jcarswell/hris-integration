function doneProcess(ret_data) {
  if (ret_data["status"] != "success") {
    $('.alert').text(ret_data["message"]);
    $('.alert').alert();
    $('.alert').addClass("alert-danger");
    ret_data["fields"].forEach(i => {$("input[name="+i+"]").addClass('is-invalid');})

  } else {
    $('.alert').text("Success");
    $('.alert').alert();
    $('.alert').addClass("alert-sucess");
    $('.is-invalid').removeClass("is-invalid");
  }
}
function errorProcess(jqXHR,status,error) {
  $('.alert').text("A Server error occured: " + status);
  $('.alert').alert();
  $('.alert').addClass("alert-danger");
}