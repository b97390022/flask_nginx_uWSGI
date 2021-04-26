(function () {

  var clockElement = document.getElementById( "clock" );
  // set default
  clock.innerHTML = new Date().toLocaleTimeString();

  function updateClock ( clock ) {
    clock.innerHTML = new Date().toLocaleTimeString();
  }

  setInterval(function () {
      updateClock( clockElement );
  }, 1000);

  //enter for submit input
  $("#input1").keypress(function (e) {
    var code = (e.keyCode ? e.keyCode : e.which);
    // alert(code);
    if (e.keyCode == 13 && !e.shiftKey ) {
        $("#btn1").trigger('click');
        return false;
    };
  });

  //toggle
  $("th.toggle").click(function (e){
    $("div.toggled").slideToggle(300);
  });
  
}());

$("#signup :submit").click(function (event) { 
  event.preventDefault();
  if (confirm('確定要註冊嗎?')) {

    $.ajax({
      url: '/auth/signup',
      type: 'POST',
      data : $('#signup').serialize(),

      success: function(response){
        if(response == 'repead_user'){
          alert("使用者重複，請再試一次。"); 
        } else if (response == 'password_not_match') {
          alert("兩次密碼輸入不相同，請再試一次。"); 
        } else {
          alert("註冊成功，請至信箱啟用你的帳號!"); 
          window.location = '/auth/login';
        }
      },

      error: function(jqXHR) {
        alert("error: " + jqXHR.responseText);
        console.log(jqXHR);
      },

    })
    // .done(function(response) {
    //   window.location = '/auth/login';
    // });

  } else {
    return false;
  }
});

function input(){
  var text = "EGFR p.Leu90Arg\nEGFR T790M\nKRAS,K12D\nPRKCA 775C>A";
  document.forms.frm1.textbox.value = text;
}    

$("input[class='checkbox']").click(function () { 
  checkedState = $(this).prop('checked');
   $(this).parent('td').children('.checkbox:checked').each(function () {
       $(this).prop('checked', false);
   });
   $(this).prop('checked', checkedState);
});

// $('#frm2').on('submit', function(event){
$('#frm2 :submit').click(function(event){
  event.preventDefault();
  dataArray = {}
  $('#frm2 input:checkbox, #frm2 input:text').each(function(i, field){
    // console.log(parseInt(i/3))
    // console.log(field)
    if (i % 3 == 0) {
      dataArray[parseInt(i/3)] = [field.name,field.checked ? field.value : "None"];
    } else if (i % 3 == 2){
      dataArray[parseInt(i/3)].push(field.name);
      dataArray[parseInt(i/3)].push(field.value ? $(this).val() : "None");
    } else {
      dataArray[parseInt(i/3)].push(field.name);
      dataArray[parseInt(i/3)].push(field.checked ? field.value : "None");
    }
  });
  var sp = $('#batchid').text();
  dataArray['batchid'] = sp;

  console.log(dataArray);
  
  $.ajax({
    type : 'POST',
    url : '/submit',
    contentType: "application/json",
    dataType: "json",
    data : JSON.stringify(dataArray, null, 4)

    // success: function(data) { 
    //   alert("Submit success!");                    
    // },
    // error: function(jqXHR) {
    //     alert("error: " + jqXHR.status);
    //     console.log(jqXHR);
    // }
  })
  .done(function(data) {
    alert("Submit success!")
    // $('#successAlert').text(JSON.stringify(dataArray, null, 4)).show();
  });
});

// button
// RIPPLES EFFECT
function ripplesEffect(e) {
  var waves, d, x, y;
  
  if($(this).find('.waves').length === 0) {
      $(this).prepend('<span class="waves"></span>');
  }
   
  waves = $(this).find('.waves');
  waves.removeClass('ripple');
   
  if(!waves.height() && !waves.width()) {
      d = Math.max($(this).outerWidth(), $(this).outerHeight());
      waves.css({height: d, width: d});
  }
  
  x = e.pageX - $(this).offset().left - waves.width()/2;
  y = e.pageY - $(this).offset().top - waves.height()/2;
   
  waves.css({top: y+'px', left: x+'px'}).addClass('ripple');
};

$(document).ready(function(){
  $('.btn, .ripples').on('click', ripplesEffect);
});



