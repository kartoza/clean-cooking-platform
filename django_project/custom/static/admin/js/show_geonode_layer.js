hide_page=false;
hide_containers = {}
$ = django.jQuery
$(document).ready(function(){
    const use_geonode_layer = $('.use_geonode_layer');
    const use_geonode_layer_checkbox = use_geonode_layer.find('input[type="checkbox"]');
    $.each(use_geonode_layer_checkbox, function (index, checkbox) {
        let $checkbox = $(checkbox);
        let id = $checkbox.attr('id');
        if (!id in hide_containers) {
            hide_containers[id] = false
        }
        if ($checkbox.is(':checked')) {
            $checkbox.parent().parent().parent().parent().find('.geonode_layer').show();
            $checkbox.parent().parent().parent().parent().find('.endpoint').hide();
            hide_containers[id]=true;
        } else {
            $checkbox.parent().parent().parent().parent().find('.geonode_layer').hide();
            $checkbox.parent().parent().parent().parent().find('.endpoint').show();
            hide_containers[id]=false;
        }
    })

    use_geonode_layer_checkbox.click(function(e){
        let target = $(e.target);
        let id = target.attr('id');
        if (!id in hide_containers) {
            hide_containers[id] = false
        }
        hide_containers[id]=!hide_containers[id];
        const _geonode_layer_container = target.parent().parent().parent().parent().find('.geonode_layer')
        const _endpoint_container = target.parent().parent().parent().parent().find('.endpoint')
        if (hide_containers[id]) {
            _geonode_layer_container.show();
            _endpoint_container.hide();
        } else {
            _geonode_layer_container.hide();
            _endpoint_container.show();
        }
    })
})