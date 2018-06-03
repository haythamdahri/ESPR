$(".form-delete-image").submit(function( event ) {
	event.preventDefault();
	var form = $(this);
    $.ajax({
		url: form.attr("data-submit-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
			if(data.message == "success") {
				console.log(data.tr);
			    $(data.tr).remove();
            }
		}
    });
});

$("#stock-modal-submit").click(function(){
    $("#stock-form-submit").click();
});
$("#specification-modal-submit").click(function(){
    $("#specification-form-submit").click();
});
$("#details-modal-submit").click(function(){
    $("#details-form-submit").click();
});
$("#tag-modal-submit").click(function(){
    $("#tag-form-submit").click();
});

$("#form-stock").submit(function( event ) {
	event.preventDefault();
	var form = $(this);
    $.ajax({
		url: form.attr("data-submit-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
			if(data.valid){
			    $("#stock-modal-success").show();
			    $("#id_quantity").val('');
			    $("#id_color").val("");
			    $("#id_price_sup").val("");
			    $("#stock_t").prepend("<tr><td class='text-center'>" + data.message + "</td></tr>");
			    setTimeout(function () {
			        $("#stock-modal-success").hide();
                }, 5000);
            } else {
			    $("#stock-modal-danger").show();
			    setTimeout(function () {
			        $("#stock-modal-danger").hide();
                }, 5000);
            }
		}
    });
});

$("#form-specification").submit(function( event ) {
	event.preventDefault();
	var form = $(this);
    $.ajax({
		url: form.attr("data-submit-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
			if(data.valid){
			    $("#specification-modal-success").show();
			    $("#form-specification .form-control").val('');
			    setTimeout(function () {
			        $("#specification-modal-success").hide();
                }, 5000);
            } else {
			    $("#specification-modal-danger").show();
			    setTimeout(function () {
			        $("#specification-modal-danger").hide();
                }, 5000);
            }
		}
    });
});

$("#form-details").submit(function( event ) {
	event.preventDefault();
	var form = $(this);
    $.ajax({
		url: form.attr("data-submit-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
			if(data.valid){
			    $("#details-modal-success").show();
			    $("#form-details .form-control").val('');
			    setTimeout(function () {
			        $("#details-modal-success").hide();
                }, 5000);
            } else {
			    $("#details-modal-danger").show();
			    setTimeout(function () {
			        $("#details-modal-danger").hide();
                }, 5000);
            }
		}
    });
});
$("#form-tag").submit(function( event ) {
	event.preventDefault();
	var form = $(this);
    $.ajax({
		url: form.attr("data-submit-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
			if(data.valid){
			    $("#tag-modal-success").show();
			    $("#form-tag .form-control").val('');
			    $("#id_tags").append($('<option>', {
                    value: data.id,
                    text: data.value
                }));
			    setTimeout(function () {
			        $("#tag-modal-success").hide();
                }, 5000);
            } else {
			    $("#tag-modal-danger").show();
			    setTimeout(function () {
			        $("#tag-modal-danger").hide();
                }, 5000);
            }
		}
    });
});

$("#stock-modal-success").hide();
$("#stock-modal-danger").hide();
$("#specification-modal-success").hide();
$("#specification-modal-danger").hide();
$("#details-modal-danger").hide();
$("#details-modal-success").hide();
$("#tag-modal-danger").hide();
$("#tag-modal-success").hide();
