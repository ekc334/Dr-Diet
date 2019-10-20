const url  = "http://flask-env.tdxvsdn3ur.us-east-1.elasticbeanstalk.com/";

$("form").on('submit', function (e) {
  //ajax call here
  const dish = $('#first').val();
  const allergy = $('#second').val();
  fetch(url).then(function(response) {
    response.text().then(function(text) {
      alert(text);
    });
  });
  // $.ajax({    
  //   type: 'GET',
  //   url: url, //- action form
  //   data: {allergenName:allergy,dishName:dish},
  //   dataType: "jsonp",
  //   success: function(){
  //     alert('success');
  //   },
  //   failure: function() {
  //     alert('fail')
  //   }
  // });
  //stop form submission
  e.preventDefault();
});
