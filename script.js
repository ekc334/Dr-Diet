const url  = "http://flask-env.tdxvsdn3ur.us-east-1.elasticbeanstalk.com/";

$("form").on('submit', function (e) {
  //ajax call here
  const dish = $('#first').val();
  const allergen = $('#second').val();

  $("#output").text();
  $("#output").text(`Loading allergen data for ${dish}...`);

  $.ajax({
    url: url,
    data: {allergenName:allergen, dishName:dish},
    dataType: "html",
    // dataType: "jsonp",
    success: function(response) {
      $("#output").text(`I found that ${response}% of ${dish} recipes had ${allergen}.`);
    }
  });
  //stop form submission
  e.preventDefault();
});
