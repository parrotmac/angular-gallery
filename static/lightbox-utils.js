var responseData;
function createLightboxServerside(lightboxName, successCallback, failureCallback) {
    $.ajax({
        url: URL_USER_LIGHTBOX_AJAX,
        type: 'POST',
        data: {csrfmiddlewaretoken: csrftoken, transaction_type: 'create', userId: USER_ID, lightboxName: lightboxName}
    }).success(function(data) {
        if (data.success == true) {
            successCallback(data);
        } else {
            failureCallback();
        }
    }).error(function () {
        failureCallback();
    });
}


function createNewLightbox(sender, parentModal, nameSource) {
    var $parentModal = $(parentModal);
    var $nameSource = $(nameSource);
    var newLightboxName;
    if($nameSource.val().trim() != "") {
        newLightboxName = $nameSource.val().trim();
        createLightboxServerside(newLightboxName, function(serverResponse) {
            $parentModal.modal('hide');
            $('<a class="btn btn-default mts-button dropdown-button" data-lightbox-button-for="' + serverResponse.id + '" href="/lightbox/' + serverResponse.id + '">' + serverResponse.name + '<span class="lightbox-remove-icon" onclick="$(this).parent().click(function(e) {e.preventDefault();}); deleteLightbox(' + serverResponse.id + ')"><span class="glyphicon glyphicon-remove"></span></span></a>').insertBefore("#create-lightbox-button");
            $nameSource.val('');
            addModalLightboxOption({name: serverResponse.name, id: serverResponse.id});
        }, function() {
            //Unable to create lightbox
        });
    }
}