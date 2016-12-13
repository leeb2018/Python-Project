$(document).ready(function() {
	$('.restaurant_review_container').click(function() {
  		var newReview = "No review available. :(";
        $.ajax({
            url: '/getReview',
            type: 'POST',
            success: function(response) {
            	var kvPair = response["review"];
            	newReview = kvPair[1];
            	console.log(newReview);
                $('.restaurant_review_container').html(newReview);
            },
            error: function(error) {
                console.log(error);
            }
        });

    });
})