function addToLightboxClicked() {
    if(user_logged_in) {
        $('#addToLightboxModal').modal('show');
    } else {
        $('#loginModal').modal('show');
    }
}

$(document).ready(function() {
    if(originalLightboxes.length == 0) {
    } else {
        for (var i = 0; i < originalLightboxes.length; i++) {
            addModalLightboxOption(originalLightboxes[i]);
        }
    }
});

function lightboxDropdownSelected(sender) {
    var lightboxId = $(sender).attr("data-lightbox-id");
    var imageId = $("#image-preview").attr("data-image-id");
    console.log("Add image " + imageId + " to lightbox " + lightboxId);
    $("#addToLightboxModal").modal('hide');
    var $userProgressModal = $("#userProgressModal");
    $userProgressModal.modal('show');
    $.ajax({
        url: URL_USER_LIGHTBOX_AJAX,
        type: "POST",
        data: {csrfmiddlewaretoken: csrftoken, transaction_type: 'add_photo', lightbox_id: lightboxId, image_id: imageId}
    }).success(function(data) {
        if(data.success== true) {
            showUserMessage("Successfully Added Image To Lightbox");
        }
    }).error(function(data) {

    });
}