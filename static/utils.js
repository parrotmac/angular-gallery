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

var smallSpinOpts = {
    lines: 9, // The number of lines to draw
      length: 0, // The length of each line
      width: 4, // The line thickness
      radius: 28, // The radius of the inner circle
      corners: 0, // Corner roundness (0..1)
      rotate: 0, // The rotation offset
      direction: 1, // 1: clockwise, -1: counterclockwise
      color: '#000', // #rgb or #rrggbb or array of colors
      speed: 1, // Rounds per second
      trail: 60, // Afterglow percentage
      shadow: false, // Whether to render a shadow
      hwaccel: false, // Whether to use hardware acceleration
      className: 'spinner', // The CSS class to assign to the spinner
      zIndex: 2e9, // The z-index (defaults to 2000000000)
      top: '50%', // Top position relative to parent
      left: '50%' // Left position relative to parent
};
function addModalLightboxOption(lightbox) {
    $('<button class="btn btn-default mts-button lightbox-select-item" data-lightbox-id="' + lightbox.id + '" onclick="lightboxDropdownSelected(this)">' + lightbox.name + '</button>').appendTo(".lightbox-modal-select");
}

function showUserMessage(message) {
    $("#userProgressMessage").text(message);
    $("#userProgressModal").modal('show');
}

function promptUser(message, confirmCallback, cancelCallback) {
    $("#promptMessage").text(message);
    $("#promptUserModal").modal('show');
    $("#promptConfirmButton").attr("onclick", "(" + confirmCallback + ")()");
    $("#promptCancelButton").attr("onclick", "(" + cancelCallback + ")()");
}

var tags = [];
$.ajax({
    url: URL_GET_ALL_TAGS
}).success(function (data) {
    tags = data.tags; //It's coming back as JSON, so no need to parse...weird.
}).error(function (data) {
    console.error(data);
});


function showSearchButton() {
    $('.searchbutton').show(200);
}

function hideSearchButton() {
    $('.searchbutton').delay(250).hide(200);
}

function loginSubmit(username, password) {
    var next = window.location.pathname;
    var loginUrl = URL_LOGIN; // add the 'next' parameter to the 'POST' as a 'GET' parameter
    var loginForm = document.createElement('form');
    loginForm.setAttribute("style", "display: none;");
    loginForm.method = "POST";
    loginForm.action = loginUrl + "?next=" + next;

    var formUsername = document.createElement('input');
    formUsername.setAttribute("type", "hidden");
    formUsername.name = "username";
    formUsername.value =  username;

    var formPassword = document.createElement('input');
    formPassword.setAttribute("type", "password");
    formPassword.name = "password";
    formPassword.value =  password;

    var formCSRF = document.createElement('input');
    formCSRF.setAttribute("type", "hidden");
    formCSRF.name = "csrfmiddlewaretoken";
    formCSRF.value =  csrftoken;

    document.getElementsByTagName('body')[0].appendChild(loginForm);
    loginForm.appendChild(formUsername);
    loginForm.appendChild(formPassword);
    loginForm.appendChild(formCSRF);

    console.log(username);
    console.log(formPassword.value);

    loginForm.submit();
}
function toggleCustomDropdown(sender, target) {
    var $target = $(target);
    if($target.is(":visible")) {
        $target.hide(200);
    } else {
        $(".dropdown-slider").not(sender).hide(200);
        $target.css("left", $(sender).position().left);
        $target.show(200);
    }
}

$(".dropdown-trigger").blur(function() {
    $("#" + $(this).attr("data-dw-trigger-target")).delay(200).hide(200);
});

function deleteLightbox(id) {
    if(confirm("Are you sure you want to delete the Lightbox \"" + $("[data-lightbox-button-for=" + id + "]").text() + "\"?")) {
        $.ajax({
            url: URL_USER_LIGHTBOX_AJAX,
            type: 'POST',
            data: {csrfmiddlewaretoken: csrftoken, transaction_type: 'delete', id: id}
        }).success(function(data) {
            console.log(data.success);
            $("[data-lightbox-button-for=" + id + "]").remove();
            $("[data-lightbox-id=" + id + "]").remove();
        }).error(function(data) {
        });
    }
}

function userLogout() {

    var next = window.location.pathname;

    var logoutForm = document.createElement('form');
    logoutForm.setAttribute("style", "display: none;");
    logoutForm.action = URL_LOGIN + "?next=" + next;
    logoutForm.method = "POST";

    var logoutInput = document.createElement("input");
    logoutInput.name = "logout";
    logoutInput.value = "";
    logoutInput.type = "hidden";

    var formCSRF = document.createElement('input');
    formCSRF.setAttribute("type", "hidden");
    formCSRF.name = "csrfmiddlewaretoken";
    formCSRF.value =  csrftoken;


    logoutForm.appendChild(logoutInput);
    logoutForm.appendChild(formCSRF);
    logoutForm.submit();
}