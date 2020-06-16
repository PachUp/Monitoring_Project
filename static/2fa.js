toastr.options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": true,
    "progressBar": true,
    "positionClass": "toast-top-right",
    "preventDuplicates": false,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "3000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
  }
$("#cancel-button").click(function(){
    $.ajax({
        type: "POST",
        url: "/2fa",
        data: "cancel",
        success: function(data){
        if(data == "True"){ // data can not be boolean (unable to send boolean res type)
            $("#cancel-msg").html("<div class = 'alert-success align-middle'></div>");
            
            toastr["success"]("You have disabled 2FA.", "2FA Disabled!")
        }
        else{
            $("#cancel-msg").html("<div class = 'alert-danger align-middle'></div>");
            toastr["error"]("2FA is not enabled. You can't cancel 2FA if it's not enabled.", "2FA is not enabled!")
            
        }
        }
    });
});
$("#enable-button").click(function(){
    $.post("/2fa", function(data){
    if(data=="enabled"){
        $("#barcode").html("<div class = 'alert-danger align-middle'>You already enabled 2FA</div>");
    }
    else{
        console.log("Clicked")
        var qrcode = new QRCode(document.querySelector("#barcode"), { // have to select a query like this
        text: data,
        width: 128,
        height: 128,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
        });
    }
    });
});