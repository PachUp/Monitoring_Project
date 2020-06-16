toastr.options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": true,
    "progressBar": true,
    "positionClass": "toast-top-right",
    "preventDuplicates": false,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "5000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
  }
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
              if ($('#autoSizingCheck').is(':checked')){
                  data = data + "&CheckBox=" + "True" // maybe change in the future(that's why I have the +), option is disabled for now
              }
              else{
                  data = data + "&CheckBox=" + "True" // maybe change in the future(that's why I have the +), option is disabled for now
              }
              console.log(data);
              $.ajax({
                  type: "POST",
                  url: 'login',
                  data: data,
                  success: function(res){
                      console.log(res)
                      if(res=="username"){
                          
                          toastr["error"]("This username is not in my database. Perhaps your mail toekn has ended and someone else took it.", "This username doesn't exist")
                          
                      } 
                      else if(res=="password"){
                          
                          toastr["error"]("Not the right password. Please try again.", "Wrong password")
                          
                      }
                      else{
                          if(res =="email"){
                              toastr["error"]("Check your primary mail box or junk. You will have to verify your email before you login. If the token has ended, you'll need to sign up again.", "Please verify your email")
                              
                          }
                          else if(res=="Great"){
                              $("#pass-wrong").html("great");
                              $("#user-wrong").html("great");
                              toastr["success"]("Login you in!", "Success!")
                              $(location).attr("href", "http://admin-monitor.herokuapp.com/")
                          }
                          else{
                              console.log("Else")
                              window.location = "http://admin-monitor.herokuapp.com/check-2fa?id=" + res;
                          }
                      }
                  }
              });
          });
      });