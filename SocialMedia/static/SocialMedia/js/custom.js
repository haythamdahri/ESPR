var toggle = document.getElementById('container');
var toggleContainer = document.getElementById('toggle-container');
var toggleNumber;



jQuery.each(jQuery('textarea[data-statut]'), function() {
    var offset = this.offsetHeight - this.clientHeight;

    var resizeTextarea = function(el) {
        jQuery(el).css('height', 'auto').css('height', el.scrollHeight + offset);
    };
    jQuery(this).on('keyup input', function() { resizeTextarea(this); }).removeAttr('data-autoresize');
});

function resizeBox(el, st) {
    var offset = el.offsetHeight - el.clientHeight;

    var resizeTextarea = function(el) {
        jQuery(".textareaComment"+st).css('height', 'auto').css('height', el.scrollHeight + offset);
    };
    jQuery(el).on('keyup input', function() { resizeTextarea(el); }).removeAttr('data-autoresize');
}

function resizeBoxReply(el, st) {
    var offset = el.offsetHeight - el.clientHeight;

    var resizeTextarea = function(el) {
        jQuery(".textareaReply"+st).css('height', 'auto').css('height', el.scrollHeight + offset);
    };
    jQuery(el).on('keyup input', function() { resizeTextarea(el); }).removeAttr('data-autoresize');
}

function displayStatut(bt){
	$('#statut').show(300);
	$('#statut').focus();
	$(bt).hide(300);
}

function hideStatut(txtbox){
	if( $(txtbox).val().length === 0 ) {
		$(txtbox).slideUp(350);
		$(".btstatutHIDESHOW").slideDown(350);
    }
}

var $menu = $('.feed-shared-update-control-menu-trigger, .comment-options-trigger', '.BTOPENMENUPROFIL');


$(document).mouseup(function (e) {
   if (!$menu.is(e.target) // if the target of the click isn't the container...
   && $menu.has(e.target).length === 0) // ... nor a descendant of the container
   {
     $(".DRPDW, .artdeco-dropdown-menu").hide();
  }
 });


$(document).ready( function() {


$('textarea[data-statut]').focus(function () {
        $(this).animate({ height: "0" }, 50);
});


	$(".StatutFileSelect").mouseover(function(){
		$(this).find('i, li-icon').css('color', '#0077b5');
	}).mouseout(function(){
		$(this).find('i').css('color', '#999999');
		$(this).find('li-icon').css('color', '#333');
	});


$('#photoform .input-group, #photoprofilform .input-group, #photoformgroupe .input-group, #photoprofilformgroupe .input-group').find(':text').val('');




	$("#btcoverchange, #btprofilchange").click(function() {
        $(".modal-footer").show();
        $("#photo, #photo1").hide();
        $(".uploadp, .uploadprogress").addClass('hidden');
        $("#photoform input[type=text], #photoprofilform input[type=text], #photoformgroupe input[type=text], #photoprofilformgroupe input[type=text]").val('');
    });


    	$(document).on('change', '.btn-file :file', function() {
		var input = $(this),
			label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
		input.trigger('fileselect', [label]);
		});

    	$(document).on('change', '.btn-file1 :file', function() {
		var input = $(this),
			label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
		input.trigger('fileselect', [label]);
		});

		$('.btn-file :file').on('fileselect', function(event, label) {

		    var input = $(this).parents('.input-group').find(':text'),
		        log = label;

		    if( input.length ) {
		        input.val(log);
		    } else {
		        if( log ) console.log(log);
		    }

		});

		$('.btn-file1 :file').on('fileselect', function(event, label) {

		    var input = $(this).parents('.input-group').find(':text'),
		        log = label;

		    if( input.length ) {
		        input.val(log);
		    } else {
		        if( log ) console.log(log);
		    }

		});

		function readURL(input) {
		    if (input.files && input.files[0]) {
		        var reader = new FileReader();

		        reader.onload = function (e) {
		            $('#img-upload').attr('class', 'img-thumbnail');
		            $('#img-upload').attr('src', e.target.result);
		            $('#photo').fadeIn(1500);
		        }

		        reader.readAsDataURL(input.files[0]);
		    }
		}

		function readURL1(input) {
		    if (input.files && input.files[0]) {
		        var reader = new FileReader();

		        reader.onload = function (e) {
		            $('#img-upload1').attr('class', 'img-thumbnail');
		            $('#img-upload1').attr('src', e.target.result);
		            $('#photo1').fadeIn(1500);
		        }

		        reader.readAsDataURL(input.files[0]);
		    }
		}

		function readURLPOSTIMG(input) {
		    if (input.files && input.files[0]) {
		        var reader = new FileReader();

		        reader.onload = function (e) {
		            $('#IMAGESTATUT').attr('class', 'img-thumbnail');
		            $('#IMAGESTATUT').attr('src', e.target.result);
		            $('#PHOTOPOST').fadeIn(1500);
		        }

		        reader.readAsDataURL(input.files[0]);
		    }
		}



		function readURLPOSTVID(input) {
				    var fileInput = input;
				    var fileUrl = window.URL.createObjectURL(fileInput.files[0]);
				    $("#VIDEOSTATUT").attr("src", fileUrl);
		            $('#VIDEOPOST').fadeIn(1500);
		}

		$("#IMGST").change(function(){
		    readURLPOSTIMG(this);
            $("#CLEARINTUSER").fadeIn();
		});



		$("#VIDST").change(function(){
		    readURLPOSTVID(this);
            $("#CLEARINTUSER").fadeIn();
		});

		$("#DOCST").change(function(e){
			var fileName = e.target.files[0].name;
		    $("#DOCSTATUT").html(fileName);
		    $("#DOCPOST").fadeIn(1500);
            $("#CLEARINTUSER").fadeIn();
		});



		$("#imgInp").change(function(){
		    readURL(this);
		});

		$("#imgInp1").change(function(){
		    readURL1(this);
		});

		$(".blue").hover(function(){
			$(".blue").css('opacity','1');
		},function(){
			$(".blue").css('opacity','0.3');
		});

		$(".green").hover(function(){
			$(".green").css('padding','20');
		},function(){
			$(".green").css('padding','');
		});



	});

toggle.addEventListener('click', function() {
	toggleNumber = !toggleNumber;
	if (toggleNumber) {
		toggleContainer.style.clipPath = 'inset(0 0 0 50%)';
		toggleContainer.style.backgroundColor = '#D74046';
		$(".signup").slideToggle(1000);
    	$('.signin').slideToggle(1000);
    	$(document).prop("title", "S'inscrire");
	} else {
		toggleContainer.style.clipPath = 'inset(0 50% 0 0)';
		toggleContainer.style.backgroundColor = 'dodgerblue';
		$(".signup").slideToggle(1000);
    	$('.signin').slideToggle(1000);
    	$(document).prop('title', 'Se Connecter');
	}
	console.log(toggleNumber)
});

$("#resetpassword").click(function(){
	$("#resetpasswordmodal").fadeIn(750);
});




