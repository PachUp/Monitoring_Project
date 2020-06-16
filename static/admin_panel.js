$(document).ready(function(){
    for(var i = 0; i<$('.level-number').length; i++){
                if (parseInt($('.level-number').eq(i).val()) != 2){
                    $(".check-level").eq(i).hide()// if attacker unhides it - check if it's still level 2 and just in case in backend, check if the level is 2
                }
            } // hiding users that are under the level 2
        $(".button-class").click(function(){
            var currentIndex = $('.button-class').index(this);
            console.log(currentIndex)
            var computer_number = $('.computer-number').eq(currentIndex).val()
            var level_number = $('.level-number').eq(currentIndex).val()
            var allow_to_view = $("select.multiple-choice").eq(currentIndex).val()
            var username = $('.computer-number').eq(currentIndex).attr("name")
            for(var i = 0; i<$('.level-number').length; i++){
                if (parseInt($('.level-number').eq(i).val()) != 2){
                    //$(".filter-option-inner-inner").eq(currentIndex).text("Nothing selected");
                    $(".check-level").eq(i).hide()// if attacker unhides it - check if it's still level 2 and just in case in backend, check if the level is 2
                }
            } // hiding users that are under the level 2
            if(allow_to_view != null && allow_to_view!="" && allow_to_view != "undefined" && level_number == 2){
                var data = username + "=" + computer_number + "&" + level_number + "&";
                for(var i =0; i<allow_to_view.length; i++){
                    if(i==allow_to_view.length - 1){
                        data = data + allow_to_view[i];
                    }
                    else{
                        data = data + allow_to_view[i] + ',';
                    }
                }
            } 
            else{
                var data = username + "=" + computer_number + "&" + level_number + "&None";
            }
            console.log(data)
            $.ajax({
                type: "POST",
                url: 'admin-panel/data',
                data: data,
                beforeSend: function(){
                    $(".status").eq(currentIndex).html("<div class = 'alert-info'>Loading...</div>");
                },
                success: function(res){
                    user_computer_id = res["computer id"]
                    user_computer_level = res["computer level"]
                    level_2_allowed_vals = res["level 2"]
                    failed = res["Values"]
                    for(var i = 0; i<$('.level-number').length; i++){
                        if (parseInt($('.level-number').eq(i).val()) == 2){
                            console.log("HHGHIDFGIDFGIDFG")
                            $(".check-level").eq(i).show()// if attacker unhides it - check if it's still level 2 and just in case in backend, check if the level is 2
                        }
                    } // hiding users that are under the level 2
                    if(failed != "failed"){
                        const $assigned_values = $(".assigned_values");
                        const $assigned_levels = $(".assigned_levels");
                        const $assigned_level_2_values = $(".assigned-level-2-values")
                        $(".status").eq(currentIndex).html("<div class = 'alert-success'>Success</div>");
                        setTimeout(function(){
                            $(".status").eq(currentIndex).html("");
                        }, 1500);
                        $assigned_values.eq(currentIndex).text(user_computer_id)
                        $assigned_levels.eq(currentIndex).text(user_computer_level)
                        $assigned_level_2_values.eq(currentIndex).text(level_2_allowed_vals)
                        /*
                        for(var i = 0; i< user_computer_id.length; i++){
                            $assigned_values.eq(i).text(user_computer_id[i]);
                            $assigned_levels.eq(i).text(user_computer_level[i]);
                            $assigned_level_2_values.eq(i).text(level_2_allowed_vals[i])
                        }
                        */
                        if($('.level-number').eq(currentIndex).val() == 2){
                            //$(".level-2-none").eq(currentIndex).html("<select class='selectpicker multiple-choice' multiple data-live-search='true'>{% for client_id in  computer_client_id%}<option>{{client_id}}</option>{% endfor %}</select>")
                            console.log("level2")
                        }
                    }
                    else{
                        console.log(res)
                        $(".status").eq(currentIndex).html("<div class = 'alert-danger'>Failed</div>");
                    }
                },
                error: function(err, status){   
                    alert("err" + err);
                }
            });
        });
    });