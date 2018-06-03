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
                    "</td></tr>"
                )
            }
        }
    });
});