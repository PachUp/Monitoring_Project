toastr.options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": true,
    "progressBar": true,
    "positionClass": "toast-top-right",
    "preventDuplicates": false,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "10000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
  }
var current_code = "{{fa2}}"
var inter = setInterval(function(){
    let check_status = "{{code.verify(" + fa2 + ")}}";
    console.log(check_status)
    console.log(typeof(check_status))
    if(check_status == "False"){
        console.log("SEnding")
        $.ajax({
            type: "POST",
            url: "/get-the-new-code",
            data: "{{user.id}}",
            success: function(res){
            console.log(res)
            current_code = res;
            $(location).attr("href", "http://admin-monitor.herokuapp.com/login")
            }
        });
    }
}, 30000);
$(".btn").click(function(){
    var input = $("#2fa").val()
    var data = false;
    if(current_code == input){
        toastr["success"]("Corrent code, I'll redirect you to the main page in a few seconds!", "Corrent code!")
        data = true
        $.ajax({
            type: "POST",
            url: "/check-2fa",
            data: "{{user.id}}",
            success: function(res){
                $(location).attr("href", "http://admin-monitor.herokuapp.com/")
            }
        });
    }
    else{
        data = false;
        toastr["error"]("Wrong code, Please try again.", "Wrong code")
    }
});