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
    /* handle dropdown value */
  var timer = 5000;
  $(".computer-data-dropdown").click(function(){
    $(".computer-data-dropdown-item").fadeOut(1).fadeIn(2000); //animation
  });
  $("#dir-button").click(function(){
    var input_val = $("#dir-val").val();
    var currentLocation = window.location;
    var send_loc = currentLocation + "/ajax-dir"
    data = "DirVals=" + input_val
    console.log(send_loc)
    console.log("before data"  +data)
    $.ajax({
      type: "POST",
      url: send_loc,
      data: data,
      success: function(dir_items){
        dir_items = dir_items["dir items"]
        console.log(dir_items)
        $("br").remove(".dir-items")
        $(".dir-items").remove()
        $(".add-href").remove()
        for(var i = 0; i<dir_items.length; i++){
          var href_element = window.location + '/upload-file/' + dir_items[i];
          $("#list-dir").append("<a href='' class='add-href'><il class='dir-items'> " + dir_items[i] + " <br> </il></a>")
          $(".add-href").eq(i).attr("href", href_element);
        }
      }
    });
    
    /*
    setTimeout(function(){
      $.get("/computers/{{computer.id}}/ajax-dir", function(data){
      if(data !="Not found" && data["response" + "{{computer.id}}"] != "Not found"){
        console.log(data["response" + "{{computer.id}}"])
        $listSelector = $("#list-dir")
        $.each(data["response" + "{{computer.id}}"], function(i){
          $listSelector.append("<il>" + data["response" + "{{computer.id}}"][i] + "</il> <br>")
        });
      }
      else{
        console.log("Not found")
      }
    });
    }, 2500);
    */
  });
  
  $(".computer-data-dropdown-item").click(function(){ //make sure if I add another dropdown I need to change the class so they'll have diffrent ones if needed.
    var id = $(this).attr('id');
      if (id=="input"){
        $('#' + id).keypress(function (e) {
        var key = e.which;
        if(key == 13) 
          {
              timer = $('#' + id).val();
              timer = timer * 1000;
              console.log(timer);
              if(isNaN(timer) || timer < 5000){
                timer = 5000;
              }
              $('.dropdown-menu').click();
          }
        });   
      }
    else{
      timer = $('#' + id).html()
      timer = timer * 1000;
      if(isNaN(timer)|| timer < 5000){
        timer = 5000;
      }
    }
  });
  function change_progress_bar_color(cpu_after_change, memory_after_change){
    if (cpu_after_change <= 25){
      $('#cpu-progress').attr('aria-valuenow', cpu_after_change).attr('class', 'progress-bar bg-success').css('width', cpu_after_change + "%").text(cpu_after_change);
    }
    else if(cpu_after_change >= 25 && cpu_after_change <= 75){
      $('#cpu-progress').attr('aria-valuenow', cpu_after_change).attr('class', 'progress-bar bg-warning').css('width', cpu_after_change + "%").text(cpu_after_change);
    }
    else{
      $('#cpu-progress').attr('aria-valuenow', cpu_after_change).attr('class', 'progress-bar bg-danger').css('width', cpu_after_change + "%").text(cpu_after_change);
    }
    if (memory_after_change <= 25){
      $('#memory-progress').attr('aria-valuenow', memory_after_change).attr('class', 'progress-bar bg-success').css('width', memory_after_change + "%").text(memory_after_change);
      }
      else if(memory_after_change >= 25 && memory_after_change <= 75){
        $('#memory-progress').attr('aria-valuenow', memory_after_change).attr('class', 'progress-bar bg-warning').css('width', memory_after_change + "%").text(memory_after_change);
      }
    else{
      $('#memory-progress').attr('aria-valuenow', memory_after_change).attr('class', 'progress-bar bg-danger').css('width', memory_after_change + "%").text(memory_after_change);
    }
  }
    var get_new_data = function(){
    $.get("/computers/{{computer.id}}/live" ,function(data){
      var before_change = $("#cpu").html();
      var current_cpu_procentage = data['CPU usage procentage']
      var last_cpu_procentage = $("#cpu").text();
      var current_memory_procentage = data["Memory usage procentage"]
      var last_memory_procentage = $("#memory").html();
      $("#cpu").text(current_cpu_procentage);
      $("#memory").html(current_memory_procentage);
      if(parseInt(current_cpu_procentage) - parseInt(last_cpu_procentage) >= 50){
        toastr["error"]("CPU procentage raised by more than 50% than last time!", "CPU procentage:")
      }
      if(parseInt(current_memory_procentage) - parseInt(last_memory_procentage) >= 50){
        toastr["error"]("Memory procentage raised by more than 50% than last time!", "Memory procentage:")
      }
      if( parseInt(last_cpu_procentage) -parseInt(current_cpu_procentage) >= 50){
        toastr["success"]("CPU procentage reduced by more than 50% than last time!", "CPU procentage:")
      }
      if( parseInt(last_memory_procentage) - parseInt(current_memory_procentage) >= 50){
        toastr["success"]("Memory procentage reduced by more than 50% than last time!", "Memory procentage:")
      }
      var task_status_pid = data['pid'];
      var task_status_name = data['name'];
      var task_status_cpu_percent = data['cpu_percent'];
      var task_status_memory_percent = data['memory_percent'];
  
      const $task_pid = $(".task-pid");
      const $task_name = $(".task-name");
      const $task_cpu_percent = $(".task-cpu-percent");
      const $task_memory_percent = $(".task-memory-percent");
      var task_pid_arr = new Array($task_pid.length);
      for(var i = 0; i< $task_pid.length; i++){ // same length
          task_pid_arr[i] = $task_pid.eq(i).text();
      }
      big_cpu_amount = Math.round(current_cpu_procentage/4);
      var pid_found = true;
      for(var i = 0; i< $task_pid.length; i++){
        if(!task_status_pid.includes($task_pid.eq(i).text())){ // only checks for closed pids
          var msg = "PID number: " + $task_pid.eq(i).text() + " Name: " + $task_name.eq(i).text() + " Has ended!"
          toastr["error"](msg, "Running Processes:")
        }
      }
      for(var i = 0; i< task_status_pid.length; i++){
        if(!task_pid_arr.includes(task_status_pid[i])){ // only checks for new pids
          var msg = "PID number: " + task_status_pid[i] + " Name: " + task_status_name[i] + " Has added!"
          toastr["success"](msg, "Running Processes:")
        }
      }
      for(var i = 0; i< task_status_pid.length; i++){
        $task_pid.eq(i).text(task_status_pid[i]);
        $task_name.eq(i).text(task_status_name[i]);
        $task_cpu_percent.eq(i).text(task_status_cpu_percent[i]);
        $task_memory_percent.eq(i).text(task_status_memory_percent[i]);
      }
      //var jso = JSON.parse(json);
      var cpu_after_change = $("#cpu").html();
      var memory_after_change = $("#memory").html();
      var running_programes = $("#processes").html();
      if(before_change != cpu_after_change){
          $(".live").fadeOut(200).fadeIn(200);
          cpu_after_change = parseInt(cpu_after_change);
          memory_after_change = parseInt(memory_after_change);
          change_progress_bar_color(cpu_after_change,memory_after_change);
        }
        setTimeout(get_new_data, timer);
    });
  }
  
  function download_the_file(){
  
  }
  /*
  function check_download(){
    $.post("/computers/{{computer.id}}/live", function(data){
  
    });
  }
  */
  /* handle automatic update computer info without refresh */
  
  $(document).ready(function(){
    $(".add-href").on("click", function(e){
      e.preventDefault()
      console.log("d")
  
    });
    $(".dir-items").on("click", function(e){
      e.preventDefault()
      console.log("f")
    });
    download_the_file();
    setInterval(function(){
      $('#list-dir').on('change', function() {
    alert( this.value );
  });
    },1000);
    change_progress_bar_color(cpu_usage,memory_usage);
    $("span").fadeOut(500).fadeIn(800); //animation
      var cpu_usage = $("#cpu").text();
      var memory_usage = $("#memory").text();
        setTimeout(function(){
            get_new_data(); // creating an interval with settimeout because the timer won't change with a normal interval
        }, timer);
    });