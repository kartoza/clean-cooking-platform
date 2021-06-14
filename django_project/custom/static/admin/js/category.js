$ = django.jQuery
$(document).ready(function(){
    const $mainModule = $('.main-module');
    const $indexContainer = $('<fieldset class="module grp-module" id="index-fieldset" style="width: 100%; height: 100%; background-color: #ffffff; display: flex">');
    $mainModule.after($indexContainer);
    $('.eap-fieldset').detach().appendTo('#index-fieldset').show().css('min-width', '24%').css('margin-right', '0.5em');
    $('.demand-fieldset').detach().appendTo('#index-fieldset').show().css('min-width', '24%').css('margin-right', '0.5em');
    $('.supply-fieldset').detach().appendTo('#index-fieldset').show().css('min-width', '24%').css('margin-right', '0.5em');
    $('.ani-fieldset').detach().appendTo('#index-fieldset').show().css('min-width', '25%');
});