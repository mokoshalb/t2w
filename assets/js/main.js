$(window).on("load", function(){
    $("#submit").prop("disabled", true);
    $('[data-loader="circle-side"]').fadeOut();
    $("#preloader").delay(350).fadeOut("slow");
    $("body").delay(350);
    $(".background-image").each(function(){$(this).css("background-image", $(this).attr("data-background"));});
    var request;
    var tip = document.querySelector("#tip");
    $("#link").submit(function(event){
        event.preventDefault();
        $("#submit").html('<i class="fa fa-spinner fa-spin"></i> Connecting...');
        if(request){
            request.abort();
        }
        var $form = $(this);
        var $inputs = $form.find("input, select, button, textarea");
        var serializedData = $form.serialize();
        $inputs.prop("disabled", true);
        request = $.ajax({
            url: "includes/whatsapp.php",
            type: "post",
            data: serializedData
        }).done(function (response, textStatus, jqXHR){
            $("#submit").css("background", "#25D366");
            $("#submit").html('<i class="fa fa-check"></i> Connected!');
            tip.classList.remove("hide");
        }).fail(function (jqXHR, textStatus, errorThrown){
            $("#submit").css("background", "#FF0000");
            $("#submit").html('<i class="fa fa-exclamation-triangle"></i> Error Occured.');
            console.error("The following error occurred: "+textStatus, errorThrown);
            $inputs.prop("disabled", false);
        }).always(function (){});
    });
    
    var errorMap = ["Invalid number", "Invalid country code", "Too short", "Too long", "Invalid number"];
    var input = document.querySelector("#phone"), errorMsg = document.querySelector("#error-msg"), validMsg = document.querySelector("#valid-msg");
    var iti = window.intlTelInput(input, {
        utilsScript: "https://cdn.jsdelivr.net/npm/intl-tel-input@17.0.3/build/js/utils.js",
        preferredCountries: ['us', 'uk', 'ng'],
        initialCountry: "auto",
        geoIpLookup: function(success, failure) {
            $.get("https://ipinfo.io", function() {}, "jsonp").always(function(resp) {
                var countryCode = (resp && resp.country) ? resp.country : "us";
                success(countryCode);
            });
        },
    });
    window.iti = iti;
    var reset = function(){
        input.classList.remove("error");
        errorMsg.innerHTML = "";
        errorMsg.classList.add("hide");
        validMsg.classList.add("hide");
    };
    input.addEventListener('keyup', function() {
        reset();
        if(input.value.trim()){
            if(iti.isValidNumber()){
                validMsg.classList.remove("hide");
                $("#realphone").val(iti.getNumber(intlTelInputUtils.numberFormat.E164));
                $("#submit").prop("disabled", false);
            }else{
                input.classList.add("error");
                var errorCode = iti.getValidationError();
                errorMsg.innerHTML = "&cross; "+errorMap[errorCode];
                errorMsg.classList.remove("hide");
            }
        }
    });
});