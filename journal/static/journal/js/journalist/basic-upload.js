$(function () {

    $(".js-upload-photos").click(function () {
        $("#fileupload").click();
    });

    $("#fileupload").fileupload({
        dataType: 'json',
        dropZone: $('#drop-zone-multiple'),
        sequentialUploads: true,  /* 1. SEND THE FILES ONE BY ONE */
        start: function (e) {  /* 2. WHEN THE UPLOADING PROCESS STARTS, SHOW THE MODAL */
            $("#modal-progress").modal("show");
        },
        stop: function (e) {  /* 3. WHEN THE UPLOADING PROCESS FINALIZE, HIDE THE MODAL */
            $("#modal-progress").modal("hide");
        },
        progressall: function (e, data) {  /* 4. UPDATE THE PROGRESS BAR */
            var progress = parseInt(data.loaded / data.total * 100, 10);
            var strProgress = progress + "%";
            $(".progress-bar").css({"width": strProgress});
            $(".progress-bar").text(strProgress);
        },
        done: function (e, data) {
            if (data.result.is_valid) {
                $("#gallery tbody").prepend(
                    "<tr id='tr" + data.result.id + "'><td><a href='" + data.result.url + "'>" + data.result.name + "</a>" +
                    "<form class=\"pull-right form-delete-image\" " +
                    "data-submit-url=\"/journal/journalist/delete_image/" + data.result.id + "/\"> " +
                    "<button class=\"btn btn-danger\" type=\"submit\"> " +
                    "<i class=\"fa fa-trash-o\"></i> </button> </form>" +
                    "</td></tr>"
                )
            }
        }
    });
});


$(function () {
    /* 1. OPEN THE FILE EXPLORER WINDOW */
    $(".js-upload-primary_image").click(function () {
        $("#file_upload_primary").click();
    });

    /* 2. INITIALIZE THE FILE UPLOAD COMPONENT */
    $("#file_upload_primary").fileupload({
        dataType: 'json',
        dropZone: $('#drop-zone'),
        done: function (e, data) {  /* 3. PROCESS THE RESPONSE FROM THE SERVER */
            if (data.result.is_valid) {
                $("#drop-zone").html("<span class=\"glyphicon glyphicon-cloud-upload\"></span> Modifier image principale");
                $("#primary_image_url").html(
                    "<a href='" + data.result.url + "'>" + data.result.name + "</a>"
                );
                $("#has-image").val("1");
            }
        }
    });
});
