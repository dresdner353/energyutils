$(document ).ready(function() {
    // form setup prevent default POST/GET
    $("form").submit(function(e){
        e.preventDefault();
    });

    // hide all config sections
    $("#shelly_config").hide();
    $("#solis_config").hide();
    $("#shelly_config_3em2").hide();

    // custom handler function for apply button 
    $("#apply_button").click(function() {
        apply_config();
    }); 

    // get the config
    var config_request = $.get('/config');
    config_request.done(function(data) {
        // JSON parse response
        config_dict = JSON.parse(data);

        // populate and toggle 
        populate_config(config_dict);
        toggle_config();

    });
});

function populate_config(config_dict) {
    console.log("populate_config()");
    // assert configured data source
    $('#data_source').val(config_dict['data_source']);
    $('#grid_source').val(config_dict['grid_source']);

    if ('shelly' in config_dict){
        $('#shelly_api_host').val(config_dict['shelly']['api_host']);
        $('#shelly_auth_key').val(config_dict['shelly']['auth_key']);

        $('#shelly_device_id').val(config_dict['shelly']['device_id']);
        $('#shelly_pv_kwh_discard').val(config_dict['shelly']['pv_kwh_discard']);
        $('#shelly_time_slot').val(config_dict['shelly']['time_slot']);

        $('#shelly_device_id_pv').val(config_dict['shelly']['device_id_pv']);
    }

    if ('solis' in config_dict){
        $('#solis_inverter_sn').val(config_dict['solis']['inverter_sn']);
        $('#solis_api_host').val(config_dict['solis']['api_host']);
        $('#solis_key_id').val(config_dict['solis']['key_id']);
        $('#solis_key_secret').val(config_dict['solis']['key_secret']);
    }

    // metrics
    $("#metrics_live").prop("checked", config_dict['dashboard']['metrics']['live']);
    $("#metrics_today").prop("checked", config_dict['dashboard']['metrics']['today']);
    $("#metrics_yesterday").prop("checked", config_dict['dashboard']['metrics']['yesterday']);
    $("#metrics_this_month").prop("checked", config_dict['dashboard']['metrics']['this_month']);
    $("#metrics_last_month").prop("checked", config_dict['dashboard']['metrics']['last_month']);
    $("#metrics_last_12_months").prop("checked", config_dict['dashboard']['metrics']['last_12_months']);
    $('#metric_cycle_interval').val(config_dict['dashboard']['cycle_interval']);

    // donut
    $("#donut_import").prop("checked", config_dict['dashboard']['donut']['import']);
    $("#donut_consumed").prop("checked", config_dict['dashboard']['donut']['consumed']);
    $("#donut_solar").prop("checked", config_dict['dashboard']['donut']['solar']);
    $("#donut_export").prop("checked", config_dict['dashboard']['donut']['export']);
    $("#donut_solar_consumed").prop( "checked", config_dict['dashboard']['donut']['solar_consumed']);
    $("#donut_battery_charge").prop("checked", config_dict['dashboard']['donut']['battery_charge']);
    $("#donut_battery_discharge").prop("checked", config_dict['dashboard']['donut']['battery_discharge']);

    // bar charts
    $("#bar_chart_import").prop("checked", config_dict['dashboard']['bar_chart']['import']);
    $("#bar_chart_consumed").prop("checked", config_dict['dashboard']['bar_chart']['consumed']);
    $("#bar_chart_solar").prop("checked", config_dict['dashboard']['bar_chart']['solar']);
    $("#bar_chart_export").prop("checked", config_dict['dashboard']['bar_chart']['export']);
    $("#bar_chart_solar_consumed").prop( "checked", config_dict['dashboard']['bar_chart']['solar_consumed']);
    $("#bar_chart_battery_charge").prop("checked", config_dict['dashboard']['bar_chart']['battery_charge']);
    $("#bar_chart_battery_discharge").prop("checked", config_dict['dashboard']['bar_chart']['battery_discharge']);

    if ('environment' in config_dict){
        $('#env_gco2_kwh').val(config_dict['environment']['gco2_kwh']);
        $('#env_trees_kwh').val(config_dict['environment']['trees_kwh']);
    }

}

function toggle_passwords() {
    console.log("toggle_passwords()");
    if ($('#show_passwords').prop('checked')) {
        $("input[type='password']").prop('type', 'text');
    }
    else {
        $("input[type='text']").prop('type', 'password');
    }
}

function toggle_config() {
    console.log("toggle_config()");
    var data_source = $('#data_source').find(":selected").val();
    var grid_source = $('#grid_source').find(":selected").val();

    // hide all data source sections
    $("#shelly_config").hide();
    $("#solis_config").hide();
    $("#shelly_config_3em2").hide();

    // Display Inverter config
    switch(data_source) {
      case "shelly-em":
      $("#shelly_config").show();
      $("#shelly_config_3em2").hide();
      $("#grid_source_config").hide();
      break;

      case "shelly-3em-pro":
      $("#shelly_config").show();
      $("#shelly_config_3em2").show();
      $("#grid_source_config").hide();
      break;

      case "solis":
      $("#solis_config").show();
      $("#grid_source_config").show();
      break;
    }

    // Display alternative Grid source config
    switch(grid_source) {
      case "shelly-em":
      $("#shelly_config").show();
      break;

    }
}

// format action handler
function apply_config() {
    console.log("apply_config()");
    config_dict = {};

    config_dict['data_source'] = $('#data_source').val();
    config_dict['grid_source'] = $('#grid_source').val();

    if (config_dict['data_source'] == 'shelly-em' || 
        config_dict['data_source'] == 'shelly-3em-pro' ||
        config_dict['grid_source'] == 'shelly-em') {
        config_dict['shelly'] = {};
        config_dict['shelly']['api_host'] = $('#shelly_api_host').val();
        config_dict['shelly']['auth_key'] = $('#shelly_auth_key').val();

        config_dict['shelly']['device_id'] = $('#shelly_device_id').val();
        config_dict['shelly']['pv_kwh_discard'] = Number($('#shelly_pv_kwh_discard').val());
        config_dict['shelly']['time_slot'] = Number($('#shelly_time_slot').val());

        config_dict['shelly']['device_id_pv'] = $('#shelly_device_id_pv').val();
    }

    if (config_dict['data_source'] == 'solis') {
        config_dict['solis'] = {};
        config_dict['solis']['inverter_sn'] = $('#solis_inverter_sn').val();
        config_dict['solis']['api_host'] = $('#solis_api_host').val();
        config_dict['solis']['key_id'] = $('#solis_key_id').val();
        config_dict['solis']['key_secret'] = $('#solis_key_secret').val();
    }

    config_dict['dashboard'] = {}

    config_dict['dashboard']['metrics'] = {};
    config_dict['dashboard']['metrics']['live'] =  $('#metrics_live').prop('checked');
    config_dict['dashboard']['metrics']['today'] = $('#metrics_today').prop('checked');
    config_dict['dashboard']['metrics']['yesterday'] = $('#metrics_yesterday').prop('checked');
    config_dict['dashboard']['metrics']['this_month'] = $('#metrics_this_month').prop('checked');
    config_dict['dashboard']['metrics']['last_month'] = $('#metrics_last_month').prop('checked');
    config_dict['dashboard']['metrics']['last_12_months'] = $('#metrics_last_12_months').prop('checked');
    config_dict['dashboard']['cycle_interval'] = $('#metric_cycle_interval').val();

    config_dict['dashboard']['donut'] = {};
    config_dict['dashboard']['donut']['import'] = $('#donut_import').prop('checked');
    config_dict['dashboard']['donut']['consumed'] = $('#donut_consumed').prop('checked');
    config_dict['dashboard']['donut']['solar'] = $('#donut_solar').prop('checked');
    config_dict['dashboard']['donut']['export'] = $('#donut_export').prop('checked');
    config_dict['dashboard']['donut']['solar_consumed'] = $('#donut_solar_consumed').prop('checked');
    config_dict['dashboard']['donut']['battery_charge'] = $('#donut_battery_charge').prop('checked');
    config_dict['dashboard']['donut']['battery_discharge'] = $('#donut_battery_discharge').prop('checked');

    config_dict['dashboard']['bar_chart'] = {};
    config_dict['dashboard']['bar_chart']['import'] = $('#bar_chart_import').prop('checked');
    config_dict['dashboard']['bar_chart']['consumed'] = $('#bar_chart_consumed').prop('checked');
    config_dict['dashboard']['bar_chart']['solar'] = $('#bar_chart_solar').prop('checked');
    config_dict['dashboard']['bar_chart']['export'] = $('#bar_chart_export').prop('checked');
    config_dict['dashboard']['bar_chart']['solar_consumed'] = $('#bar_chart_solar_consumed').prop('checked');
    config_dict['dashboard']['bar_chart']['battery_charge'] = $('#bar_chart_battery_charge').prop('checked');
    config_dict['dashboard']['bar_chart']['battery_discharge'] = $('#bar_chart_battery_discharge').prop('checked');

    config_dict['environment'] = {};
    config_dict['environment']['gco2_kwh'] = Number($('#env_gco2_kwh').val());
    config_dict['environment']['trees_kwh'] = Number($('#env_trees_kwh').val());

    // JSON POST to /config
    post_body = JSON.stringify(config_dict);
    request = new XMLHttpRequest();
    request.open('POST', '/config', true);
    request.setRequestHeader('Content-type', 'application/json; charset=UTF-8');
    request.send(post_body);
    request.onload = function () {
        if(request.status == 200) {
            console.log("config update success");
        }
    }
}

function download_config() {
    // get the config
    // invoke file download
    console.log("download_config()");
    config_request = $.get('/config');
    config_request.done(function(data) {
        config_dict = JSON.parse(data);
        blob = new Blob(
                        [JSON.stringify(config_dict, null, 4)], 
                        { type : 'application/json' }
        );
        file = new File(
                        [blob], 
                        'config.json', 
                        {
                            type: 'text/json;charset=utf-8',
                        }
        );
        const link = document.createElement('a');
        const url = URL.createObjectURL(file);

        link.href = url;
        link.download = file.name;
        document.body.appendChild(link);
        link.click();

        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    });
}

function import_config() {
    console.log("import_config()");
    $('#import_file').click();
}

async function load_import_file(event) {
    file = event.target.files.item(0)
    text = await file.text();
    config_dict = JSON.parse(text);
    populate_config(config_dict);
    toggle_config();

    // force display of pasword fields
    $('#show_passwords').prop('checked', true);
    toggle_passwords();
}

function show_dashboard() {
    console.log("show_dashboard()");
    if (document.referrer != document.URL) {
        // back to referring URL
        target = document.referrer;
    }
    else {
        // default to root
        target = '/';
    }
    window.location.replace(target);
}
