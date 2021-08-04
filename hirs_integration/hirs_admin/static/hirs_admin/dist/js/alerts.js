function doneProcess(data) {
  if (data["status"] != "success") {
    $('.alert').text(data["message"]);
    $('.alert').alert();
    $('.alert').addClass("alert-danger");
    for(f in data["feilds"]){$('#'+f).addClass("is-invalid");}
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