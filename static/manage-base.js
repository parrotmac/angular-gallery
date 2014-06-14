/**
 * Created by isaac on 6/13/14.
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
document.getElementById('csrf_input').value = csrftoken;

function galleryActiveToggle(sender) {
    var galleryToToggle = sender.value;
    console.log("Gallery " + galleryToToggle + " is now:" + (sender.checked?"active":"inactive"));
    $.ajax({
        type: "POST",
        url: URL_MANAGE_GALLERY,
        data: {csrfmiddlewaretoken: csrftoken, toggle_active: galleryToToggle, active_state: sender.checked}
    }).done(function(data) {
        console.log(data);
        console.log(JSON.parse(data));
    })
}

function showUserProgressMessage(showMessage, message) {
    if(showMessage) {
        $(".message-modal-header").text(message)
        $('#messageModal').modal('show');
    } else {
        $('#messageModal').delay(500).modal('hide');
    }
}
function showUserErrorMessage(message) {
    $(".error-message-modal-header").text(message);
    $("#errorMessageModal").modal('show');
}