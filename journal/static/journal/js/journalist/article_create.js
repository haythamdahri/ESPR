
$( "#form-create-article" ).submit(function( event ) {

    var errors = 0;
    var form = $(this);

    var has_image = $("#has-image").val();
    if(has_image == "0") {
        errors += 1;
        $("#image-alert").removeClass('hidden');
    }

    var category = $("#article_category").val();
    if(category == ""){
        errors += 1;
        $("#comment-alert").removeClass('hidden');
    } else {
        $("#id_category").val(category);
    }

    var comment = $("input[name='comment']:checked" ).val();
    $("#id_comment_enable").val(comment);

    var share = $("input[name='share']:checked" ).val();
    $("#id_share_enable").val(share);

    if (errors == 0){
        form.submit();
    } else {
        event.preventDefault();
    }

});

$("#modal-submit").click(function(){
    $("#modal-form-submit").click();
});

function success_hide() {
    $("#modal-success").hide();
}
function danger_hide() {
    $("#modal-danger").hide();
}

$("#form-tag").submit(function( event ) {
	event.preventDefault();
	var form = $(this);
    $.ajax({
		url: form.attr("data-submit-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
			if(data.valid){
			    $("#tags").append($('<option>', {
                    value: data.id,
                    text: data.name
                }));
			    $("#tags").selectpicker('refresh');
			    $("#modal-success").show();
			    $("#id_name").val('');
			    $("#id_color").val("");
			    $("#id_description").val("");
			    setTimeout(success_hide, 5000);
            } else {
			    $("#modal-danger").show();
			    setTimeout(danger_hide, 5000);
            }
		}
    });
});

$(".form-delete-image").submit(function( event ) {
	event.preventDefault();
	var form = $(this);
    $.ajax({
		url: form.attr("data-submit-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
			if(data.message == "success") {
			    $(data.tr).remove();
            }
		}
    });
});

success_hide();
danger_hide();

$(".django-ckeditor-widget").css('display', 'block');
