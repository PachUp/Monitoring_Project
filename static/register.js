function myFunction() {
    var x = document.getElementById("password");
    if(document.getElementById("eye").className == "fa fa-eye-slash icon"){
      document.getElementById("eye").className = "fa fa-eye icon";
    }
    else{
      document.getElementById("eye").className = "fa fa-eye-slash icon";
    }
    if (x.type === "password") {
      x.type = "text";
    } else {
      x.type = "password";
    }
  }
$(document).ready(function(){
    $("#button-id").click(function(){
        var data = $("form").serialize();
        console.log(data);
        $.ajax({
            type: "POST",
            url: 'register',
            data: data,
            success: function(res){
                if(res == "all"){
                    $("#user-exist").css("color", "red");
                    $("#email-exist").css("color", "red");
                    $("#email-contain").css("color", "red");
                }
                else if(res == "email contain"){
                    $("#user-exist").css("color", "green");
                    $("#email-exist").css("color", "green");
                    $("#email-contain").css("color", "red");
                }
                else if(res == "email exist"){
                    $("#user-exist").css("color", "green");
                    $("#email-exist").css("color", "red");
                    $("#email-contain").css("color", "green");
                }
                else if(res=="username exist"){
                    $("#user-exist").css("color", "red");
                    $("#email-exist").css("color", "green");
                    $("#email-contain").css("color", "green");
                } 
                else if(res=="email"){
                    $("#user-exist").css("color", "green");
                    $("#email-exist").css("color", "green");
                    $("#email-contain").css("color", "red");
                }
                else if(res == "username exist email contain"){
                    $("#user-exist").css("color", "red");
                    $("#email-exist").css("color", "green");
                    $("#email-contain").css("color", "red");
                }
                else if(res == "username exist email exist"){
                    $("#user-exist").css("color", "red");
                    $("#email-exist").css("color", "red");
                    $("#email-contain").css("color", "green");
                }
                else{
                    $("#user-exist").css("color", "green");
                    $("#email-exist").css("color", "green");
                    $("#email-contain").css("color", "green");
                    $(location).attr("href", "http://admin-monitor.herokuapp.com/login");
                }
            }
        });
    });
});