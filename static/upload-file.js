send_url = "/computers/{{computer.id}}/file-ready"
let flag = true;
var counter = 0;
var inter = setInterval(() => {
    counter = counter + 1;
    if(flag == true){
        $.ajax({
        type: "POST",
        url: send_url,
        beforeSend: function(){
            flag = false;
        },
        success: function(data){
            flag = true;
            if (data == "Ready"){
                console.log("sec")
                clearInterval(inter);
                window.location.href = send_url;
                }
            },
        error: function(){
            flag = true;
            console.log("err")
            }
        });  
    }
}, 7000);