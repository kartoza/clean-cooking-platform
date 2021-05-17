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
            $checkbox.parent().parent().parent().parent().find('.configuration').hide();
            $checkbox.parent().parent().parent().parent().find('.endpoint').hide();
            hide_containers[id]=true;
        } else {
            $checkbox.parent().parent().parent().parent().find('.geonode_layer').hide();
            $checkbox.parent().parent().parent().parent().find('.configuration').show();
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
        const _configuration_container = target.parent().parent().parent().parent().find('.configuration')
        const _endpoint_container = target.parent().parent().parent().parent().find('.endpoint')
        if (hide_containers[id]) {
            _geonode_layer_container.show();
            _endpoint_container.hide();
            _configuration_container.hide();
        } else {
            _geonode_layer_container.hide();
            _endpoint_container.show();
            _configuration_container.show();
        }
    })

    // On dataset file changed
    const func = $('.func');
    const vectorConfigurationDefault = {
      "fill": "#ffffff",
      "width": 3,
      "stroke": "#000000",
      "opacity": 1,
      "dasharray": "0",
      "shape_type": "lines",
      "stroke-width": 2
    }
    const csvConfigurationDefault = {
        "enabled": true
    }
    const rasterConfigurationDefault = {
      "init": {
        "max": 100000,
        "min": 0
      },
      "scale": "intervals",
      "domain": {
        "max": 100000,
        "min": 0
      },
      "factor": 1,
      "intervals": [
        0,
        1,
        150,
        500,
        1500,
        5000,
        100000
      ],
      "precision": 0,
      "color_stops": [
        "#32095d",
        "#781c6d",
        "#ba3655",
        "#ed6825",
        "#fbb318",
        "#fcfea4"
      ]
    }
    func.find('select').change(function(e) {
        const $target = $(e.target);
        const $parent = $target.parent().parent().parent().parent();
        let container = $parent.find("*[id*='-configuration']")[0];
        let textarea = $parent.find("*[id*='-configuration_textarea']")[0];
        $(container).children().remove();

        let options = {"modes": ["text", "code", "tree", "form", "view"], "mode": "code", "search": true};
        options.onChange = function () {
            let json = editor.get();
            textarea.value=JSON.stringify(json);
        }
        const editor = new JSONEditor(container, options)
        switch ($target.val()) {
            case 'vectors':
                editor.set(vectorConfigurationDefault);
                textarea.value=JSON.stringify(vectorConfigurationDefault);
                break;
            case 'raster':
                editor.set(rasterConfigurationDefault);
                textarea.value=JSON.stringify(rasterConfigurationDefault);
                break;
            case 'csv':
                editor.set(csvConfigurationDefault);
                textarea.value=JSON.stringify(csvConfigurationDefault);
                break;
            default:
                editor.set({})
        }
    });
})