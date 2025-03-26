// get query arg from page
function get_query_arg(arg) {
    value = undefined;
    value_start = location.search.split(arg + '=')[1];
    if (value_start != undefined) {
        value = value_start.split('&')[0];
    }

    return value;
}

// get redirect URL with new query arg
// this will preserve any other query args
// for example the margin arg
function get_redirect_url(arg, value) {
    url = new URL(window.location);
    console.log("get_redirect_url()");
    const params = new URLSearchParams(url.search);
    params.set(arg, value);
    redirect_url = "/?" + params.toString();
    console.log("redirect url: " + redirect_url);
    return redirect_url;
}

// Google charts
google.charts.load('current', {'packages': ['corechart']});
google.charts.load('current', {'packages':['gauge']});

// data dict as taken from the /data GET
var data_dict = {
    year: [],
    month: [],
    day: []
};

// refresh timer 
// initalised with a short initial value for the first load
var refresh_interval = 1000
var refresh_timer = setInterval(refresh_data, refresh_interval);

// metric cycle timer also initialised with a short
// timer
var metric_cycle_interval = 1000;
var metric_cycle_timer = setInterval(cycle_metric_index, metric_cycle_interval);

// global string for selected layout
var layout;

// document load
$( document ).ready(function() {
    console.log("ready()");
    // hide the dashboard and splash initially
    $("#dashboard").hide();
    $("#splash").show();

    // set dash to blank text
    // layout will over-ride this
    $("#dashboard").html("");

    set_layout();
    refresh_data();
    display_data();
});

// Window focus changes activates/deactivates 
// the timers to avoid background activity when not in focus
$(window).focus(function() {

    // instant update
    refresh_data();
    display_data();

    // restart timers
    clearInterval(refresh_timer);
    refresh_timer = setInterval(refresh_data, refresh_interval);

    clearInterval(metric_cycle_timer);
    metric_cycle_timer = setInterval(cycle_metric_index, metric_cycle_interval);

}).blur(function() {

    clearInterval(refresh_timer);
    clearInterval(metric_cycle_timer);

});

// forced redraw of everything on resize
$(window).resize(function () { 
    set_layout();
    display_data();
});

// determines the window dimensions and sets the 
// appropriate layout template
function set_layout() {
    var window_height = window.innerHeight;
    var window_width = window.innerWidth;

    console.log("set_layout()");
    console.log("Window dims.. w:" + window_width + " h:" + window_height);

    donut_html_tmpl = ` 
            <div class="card-transparent text-white text-center mt-0">
                <div class="card-body text-center">
                    <center>
                        <a href="/admin"><div id="<DONUT-ID>_title" class="title"></div></a>
                        <div onclick="ui_cycle_layout()" id="<DONUT-ID>_chart"></div>
                    </center>
                </div>
            </div>
            `;

    metrics_html_tmpl = `
                <div onclick="ui_cycle_metric_index()" id="<METRICS-ID>" class="container text-white text-center">
                    <div id="<METRICS-ID>_title" class="row row-cols-1 mt-5">
                        <div class="col">
                            <center>
                                <div onclick="ui_cycle_layout()" id="<METRICS-ID>_titletext" class="title text-white text-center"></div>
                            </center>
                        </div>
                    </div>
                    <div class="row row-cols-2">
                        <div class="col">
                            <div class="card-transparent text-center mt-0">
                                <div class="card-body">
                                    <table border="0" align="center">
                                        <tr>
                                            <td style="vertical-align: middle;">
                                                <span id="<METRICS-ID>_import" style="metric metric-white">0</span>
                                            </td>
                                            <td style="vertical-align: middle;" align="center">
                                                <div id="<METRICS-ID>_import_icon" class="material-icons metric">login</div>
                                                <div id="<METRICS-ID>_import_unit" class="metric-unit metric-white">kWh</div>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div class="col">
                            <div class="card-transparent text-center mt-0">
                                <div class="card-body">
                                    <table border="0" align="center">
                                        <tr>
                                            <td style="vertical-align: middle;">
                                                <span id="<METRICS-ID>_consumed" style="metric metric-white">0</span>
                                            </td>
                                            <td style="vertical-align: middle;" align="center">
                                                <div id="<METRICS-ID>_consumed_icon" class="material-icons metric">home</div>
                                                <div id="<METRICS-ID>_consumed_unit" class="metric-unit metric-white">kWh</div>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div class="col">
                            <div class="card-transparent text-center mt-0">
                                <div class="card-body">
                                    <table border="0" align="center">
                                        <tr>
                                            <td style="vertical-align: middle;">
                                                <span id="<METRICS-ID>_solar" style="metric metric-white">0</span>
                                            </td>
                                            <td style="vertical-align: middle;" align="center">
                                                <div id="<METRICS-ID>_solar_icon" class="material-icons metric">solar_power</div>
                                                <div id="<METRICS-ID>_solar_unit" class="metric-unit metric-white">kWh</div>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div class="col">
                            <div class="card-transparent text-center mt-0">
                                <div class="card-body">
                                    <table border="0" align="center">
                                        <tr>
                                            <td style="vertical-align: middle;">
                                                <span id="<METRICS-ID>_export" style="metric metric-white">0</span>
                                            </td>
                                            <td style="vertical-align: middle;" align="center">
                                                <div id="<METRICS-ID>_export_icon" class="material-icons metric">logout</div>
                                                <div id="<METRICS-ID>_export_unit" class="metric-unit metric-white">kWh</div>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div id="<METRICS-ID>_battery_charge_col" class="col">
                            <div class="card-transparent text-center mt-0">
                                <div class="card-body">
                                    <table border="0" align="center">
                                        <tr>
                                            <td style="vertical-align: middle;">
                                                <span id="<METRICS-ID>_battery_charge" style="metric metric-white">0</span>
                                            </td>
                                            <td style="vertical-align: middle;" align="center">
                                                <div id="<METRICS-ID>_battery_charge_icon" class="material-icons metric">battery_charging_full</div>
                                                <div id="<METRICS-ID>_battery_charge_unit" class="metric-unit metric-white">kWh</div>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div id="<METRICS-ID>_battery_discharge_col" class="col">
                            <div class="card-transparent text-center mt-0">
                                <div class="card-body">
                                    <table border="0" align="center">
                                        <tr>
                                            <td style="vertical-align: middle;">
                                                <span id="<METRICS-ID>_battery_discharge" style="metric metric-white">0</span>
                                            </td>
                                            <td style="vertical-align: middle;" align="center">
                                                <div id="<METRICS-ID>_battery_discharge_icon" class="material-icons metric">battery_4_bar</div>
                                                <div id="<METRICS-ID>_battery_discharge_unit" class="metric-unit metric-white">kWh</div>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div id="<METRICS-ID>_battery_soc_col" class="col">
                            <div class="card-transparent text-center mt-0">
                                <div class="card-body">
                                    <table border="0" align="center">
                                        <tr>
                                            <td style="vertical-align: middle;">
                                                <span id="<METRICS-ID>_battery_soc" style="metric metric-white">0</span>
                                            </td>
                                            <td style="vertical-align: middle;" align="center">
                                                <div id="<METRICS-ID>_battery_soc_icon" class="material-icons metric"></div>
                                                <div id="<METRICS-ID>_battery_soc_unit" class="metric-unit metric-white">%</div>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div class="col">
                            <div class="card-transparent text-center mt-0">
                                <div class="card-body">
                                    <table border="0" align="center">
                                        <tr>
                                            <td style="vertical-align: middle;">
                                                <span id="<METRICS-ID>_co2" style="metric metric-white">0</span>
                                            </td>
                                            <td style="vertical-align: middle;" align="center">
                                                <div id="<METRICS-ID>_co2_icon" class="material-icons metric">co2</div>
                                                <div id="<METRICS-ID>_co2_unit" class="metric-unit metric-white">kg</div>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <div class="col">
                            <div class="card-transparent text-center mt-0">
                                <div class="card-body">
                                    <table border="0" align="center">
                                        <tr>
                                            <td style="vertical-align: middle;">
                                                <span id="<METRICS-ID>_trees" style="metric metric-white">0</span>
                                            </td>
                                            <td style="vertical-align: middle;" align="center">
                                                <div id="<METRICS-ID>_trees_icon" class="material-icons metric">forest</div>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                        </div>

                    </div>

                </div>
            `;

    day_column_chart_html = `
                <div id="day_column_chart" class="col mt-0">
                    <center><div id="day_chart_title" class="title"></div></center>
                    <div id="day_google_chart"></div>
                </div>
            `;

    month_column_chart_html = `
                <div id="month_column_chart"class="col mt-0">
                    <center><div id="month_chart_title" class="title"></div></center>
                    <div id="month_google_chart"></div>
                </div>
            `;

    year_column_chart_html = `
                <div id="year_column_chart"class="col mt-0">
                    <center><div id="year_chart_title" class="title"></div></center>
                    <div id="year_google_chart"></div>
                </div>
            `

    // layout templates
    // these will be substituted into the top-level 
    // body to complete re-arrange the screen according to the 
    // selected screen size
    // it was too complex to try and dynamically change various bootstrap
    // class values etc to try and tweak a common layout to obey

    // default screen model
    // two columns, split 5:7 on bootstrap 12 breakpoints
    // left column has the donut and metrics and right
    // has the three column charts
    default_layout = `
                <div id="master" class="container-fluid" data-bs-theme="dark">
                    <div class="row">
                        <div class="col col-5 mt-0">
                            <div id="donut_a_insert" class="row">
                            </div>
                            <div id="metrics_a_insert" class="row">
                            </div>
                        </div>

                        <div class="col col-7 mt-0">
                            <div id="day_column_chart_insert" class="row">
                            </div>

                            <div id="month_column_chart_insert" class="row">
                            </div>

                            <div id="year_column_chart_insert" class="row">
                            </div>

                        </div>
                    </div>
                </div>
            `;

    // dual-donut layout
    // two columns, split 6:6 on bootstrap 12 breakpoints
    // left column has the live donut and live metrics 
    // right has the other cycled metrics rendered as a donut and metric values
    dual_metrics_layout = `
                <div id="master" class="container-fluid" data-bs-theme="dark">
                    <div class="row">
                        <div class="col col-6 mt-0">
                            <div id="donut_a_insert" class="row">
                            </div>
                            <div id="metrics_a_insert" class="row">
                            </div>
                        </div>

                        <div class="col col-6 mt-0">
                            <div id="donut_b_insert" class="row">
                            </div>
                            <div id="metrics_b_insert" class="row">
                            </div>
                        </div>

                    </div>
                </div>
            `;

    // small screen model
    // 5:7 split columns
    // donut on  left, metrics stack on right
    small_layout = `
                <div id="master" class="container-fluid" data-bs-theme="dark">
                    <div class="row align-items-center">
                        <div id="donut_a_insert" class="col col-5 mt-2">
                        </div>
                        <div id="metrics_a_insert" class="col col-7 mt-2">
                        </div>
                    </div>
                </div>
            `;

    // portrait screen model
    // vertical stack of everything
    // in a series of rows, one column
    // each. Works for phones and portrait
    // tablets or monitors
    portrait_layout = `
                <div class="container-fluid" data-bs-theme="dark">
                    <div id="donut_a_insert" class="row">
                    </div>

                    <div id="metrics_a_insert" class="row">
                    </div>

                    <div id="day_column_chart_insert" class="row">
                    </div>

                    <div id="month_column_chart_insert" class="row">
                    </div>

                    <div id="year_column_chart_insert" class="row">
                    </div>

                    </div>
                </div>
            `;

    // default metrics-only screen model
    // two columns, split 6:6 on bootstrap 12 breakpoints
    // left column has the live and today metrics fixed
    // right rotates the remaining metrics between the two
    metrics_screen_layout = `
                <div id="master" class="container-fluid" data-bs-theme="dark">
                    <div class="row align-items-center">
                        <div class="col col-6 mt-0">
                            <div id="metrics_a_insert" class="row">
                            </div>
                            <div id="metrics_b_insert" class="row">
                            </div>
                        </div>

                        <div class="col col-6 mt-0">
                            <div id="metrics_c_insert" class="row">
                            </div>
                            <div id="metrics_d_insert" class="row">
                            </div>
                        </div>
                    </div>
                </div>
            `;

    // layout checks
    layout = undefined;

    // layout query arg
    layout_arg = get_query_arg("layout");
    if (layout_arg != undefined &&
        ["small", "default", "dual-metrics", "portrait", "metrics"].includes(layout_arg)) {
        layout = layout_arg;
    }

    // auto-calculated layout
    if (layout == undefined) {
        if (window_width <= window_height) {
            layout = "portrait";
        }
        else if (window_width < 1600 || 
                 window_height < 1080) {
            layout = "small";
        }
        else {
            layout = "default";
        }
    }

    // metrics a-d layouts from common template
    metrics_a_html = metrics_html_tmpl.replaceAll("<METRICS-ID>", "metrics_a");
    metrics_b_html = metrics_html_tmpl.replaceAll("<METRICS-ID>", "metrics_b");
    metrics_c_html = metrics_html_tmpl.replaceAll("<METRICS-ID>", "metrics_c");
    metrics_d_html = metrics_html_tmpl.replaceAll("<METRICS-ID>", "metrics_d");

    // donut a and b layouts from common template
    metric_donut_a_html = donut_html_tmpl.replaceAll("<DONUT-ID>", "donut_a");
    metric_donut_b_html = donut_html_tmpl.replaceAll("<DONUT-ID>", "donut_b");

    // populate layout HTML
    switch(layout) {
      case "default":
      // default screen landscape
      $("#dashboard").html(default_layout);
      $("#donut_a_insert").html(metric_donut_a_html);
      $("#metrics_a_insert").html(metrics_a_html);
      $("#day_column_chart_insert").html(day_column_chart_html);
      $("#month_column_chart_insert").html(month_column_chart_html);
      $("#year_column_chart_insert").html(year_column_chart_html);
      break;

      case "small":
      // small screen landscape
      $("#dashboard").html(small_layout);
      $("#donut_a_insert").html(metric_donut_a_html);
      $("#metrics_a_insert").html(metrics_a_html);
      break;

      case "portrait":
      // portrait view
      $("#dashboard").html(portrait_layout);
      $("#donut_a_insert").html(metric_donut_a_html);
      $("#metrics_a_insert").html(metrics_a_html);
      $("#day_column_chart_insert").html(day_column_chart_html);
      $("#month_column_chart_insert").html(month_column_chart_html);
      $("#year_column_chart_insert").html(year_column_chart_html);
      break;

      case "metrics":
      // metrics screen landscape
      $("#dashboard").html(metrics_screen_layout);
      $("#metrics_a_insert").html(metrics_a_html);
      $("#metrics_b_insert").html(metrics_b_html);
      $("#metrics_c_insert").html(metrics_c_html);
      $("#metrics_d_insert").html(metrics_d_html);
      break;

      case "dual-metrics":
      // dual metrics landscape
      $("#dashboard").html(dual_metrics_layout);
      $("#donut_a_insert").html(metric_donut_a_html);
      $("#donut_b_insert").html(metric_donut_b_html);
      $("#metrics_a_insert").html(metrics_a_html);
      $("#metrics_b_insert").html(metrics_b_html);
      break;
    }

    // Adjust CSS
    switch(layout) {

      case "small":
      // set the small screen font sizes
      document.body.style.setProperty("--metric-font-size", 'var(--metric-font-size-small)');
      document.body.style.setProperty("--icon-font-size", 'var(--icon-font-size-small)');
      document.body.style.setProperty("--metric-unit-font-size", 'var(--metric-unit-font-size-small)');
      document.body.style.setProperty("--title-font-size", 'var(--title-font-size-small)');
      document.body.style.setProperty("--legend-font-size", 'var(--legend-font-size-small)');
      document.body.style.setProperty("--slice-font-size", 'var(--slice-font-size-small)');
      break;

      case "portrait":
      // set the portrait screen font sizes
      document.body.style.setProperty("--metric-font-size", 'var(--metric-font-size-portrait)');
      document.body.style.setProperty("--icon-font-size", 'var(--icon-font-size-portrait)');
      document.body.style.setProperty("--metric-unit-font-size", 'var(--metric-unit-font-size-portrait)');
      document.body.style.setProperty("--title-font-size", 'var(--title-font-size-portrait)');
      document.body.style.setProperty("--legend-font-size", 'var(--legend-font-size-portrait)');
      document.body.style.setProperty("--slice-font-size", 'var(--slice-font-size-portrait)');
      break;

      default:
      // set the default screen font sizes
      document.body.style.setProperty("--metric-font-size", 'var(--metric-font-size-default)');
      document.body.style.setProperty("--icon-font-size", 'var(--icon-font-size-default)');
      document.body.style.setProperty("--metric-unit-font-size", 'var(--metric-unit-font-size-default)');
      document.body.style.setProperty("--title-font-size", 'var(--title-font-size-default)');
      document.body.style.setProperty("--legend-font-size", 'var(--legend-font-size-default)');
      document.body.style.setProperty("--slice-font-size", 'var(--slice-font-size-default)');
      break;
    }

    console.log("Set layout to " + layout);

    // margin for overscan scenarios
    margin_arg = get_query_arg("margin");
    if (margin_arg != undefined) {
        $("#master").removeClass().addClass(`container-fluid mt-${margin_arg} mb-${margin_arg} mx-${margin_arg}`);
    }

    // reset timestamps on bar charts to force redraw
    day_chart_ts = 0;
    month_chart_ts = 0;
    year_chart_ts = 0;
}

// formats an energy value into 
// standard, mega or milli format with 
// unit changes and decimal point adjustments
function format_energy_value(value, std_unit, mega_unit, milli_unit) {
    value_dict = {};

    if (value >= 10000) {
        // mega unit 1dp
        value_dict['value'] = (value / 1000).toFixed(1);
        value_dict['unit'] = mega_unit;
    }
    if (value >= 1000) {
        // mega unit 2dp
        value_dict['value'] = (value / 1000).toFixed(2);
        value_dict['unit'] = mega_unit;
    }
    else if (value >= 100) {
        // standard >= 100 0dp
        value_dict['value'] = value.toFixed(0);
        value_dict['unit'] = std_unit;
    }
    else if (value >= 1) {
        // standard 2dp
        value_dict['value'] = value.toFixed(2);
        value_dict['unit'] = std_unit;
    }
    else {
        // milli unit
        value_dict['value'] = Math.floor(value * 1000);
        value_dict['unit'] = milli_unit;
    }

    return value_dict;
}

// formats the number of trees value based on value
function format_trees(value) {
    value_dict = {};

    if (value >= 100) {
        // no dp
        value_dict['value'] = value.toFixed(0);
        value_dict['unit'] = 'trees';
    }
    else if (value >= 1) {
        // 2 dp
        value_dict['value'] = value.toFixed(2);
        value_dict['unit'] = 'trees';
    }
    else if (value >= 0.001) {
        // 3dp
        value_dict['value'] = value.toFixed(3);
        value_dict['unit'] = 'trees';
    }
    else {
        // 0/neglible value, 0dp
        value_dict['value'] = 0;
        value_dict['unit'] = 'trees';
    }

    return value_dict;
}

// selects a battery capacity unit based on the soc (percentage)
function format_battery_icon(battery_soc) {

    battery_icons = [
        'battery_0_bar',
        'battery_1_bar',
        'battery_2_bar',
        'battery_3_bar',
        'battery_4_bar',
        'battery_5_bar',
        'battery_6_bar',
        'battery_full',
    ];

    percent_per_band = 100 / battery_icons.length;

    i = -1;
    ref_soc = 0;

    while (ref_soc < battery_soc) {
        ref_soc += percent_per_band;
        i++;
    }

    return(battery_icons[i]);
}

// data refresh globals
var first_refresh = 1;

// refreshes API data for 
// constructing the dashboard
function refresh_data() {
    console.log("refresh_data()");

    // get the latest data
    var data_request = $.get('/data');

    // display the get error
    data_request.fail(function() {
        $("#splash_text").html(`Data Refresh Failure`);
        data_dict.last_updated = 0;
    });           

    // valid retrieval of data
    data_request.done(function(data) {
        data_dict = JSON.parse(data);

        // on the first retrieval
        // do not react to interval changes
        // seems to cause a delay if we do
        if (first_refresh) {
            first_refresh = 0;
            return;
        }

        // check data dict refresh and update if required
        // Note: shown as second and JS operates on msecs
        if ('refresh_interval' in data_dict['dashboard']) {
            data_dict_refresh = data_dict.dashboard.refresh_interval * 1000;
            if (refresh_interval != data_dict_refresh) {
                refresh_interval = data_dict_refresh;

                // protection of min 1 sec refresh
                if (refresh_interval < 1000) {
                    refresh_interval = 1000;
                }

                // reset timer
                clearInterval(refresh_timer);
                refresh_timer = setInterval(refresh_data, refresh_interval);
                console.log('new refresh interval:' + refresh_interval);
            }
        }

        if ('cycle_interval' in data_dict['dashboard']) {
            data_dict_metric_cycle_interval = data_dict.dashboard.cycle_interval * 1000;
            if (data_dict_metric_cycle_interval != metric_cycle_interval) {
                metric_cycle_interval = data_dict_metric_cycle_interval;

                // protection of min 1 sec cycle
                if (metric_cycle_interval < 1000) {
                    metric_cycle_interval = 1000;
                }

                // reset timer
                clearInterval(metric_cycle_timer);
                metric_cycle_timer = setInterval(cycle_metric_index, metric_cycle_interval);
                console.log('new metric cycle interval:' + metric_cycle_interval);
            }
        }
    });
}

// metric series rotation globals
var metric_cycle_index = -1; // init only
var metric_key = 'live';

// rotates the current metric index as 
// part of the timed cycling
function cycle_metric_index() {
    console.log("cycle_metric_index()");

    if ('metrics' in data_dict) {
        metric_list = Object.keys(data_dict.metrics);
        for (i = 0; i < metric_list.length; i++) {
            metric_cycle_index = (metric_cycle_index + 1) % metric_list.length;

            // skip live metric in dual-donut layout
            // as live is fixed on left
            if (layout == "dual-metrics" && 
                metric_list[metric_cycle_index] == "live") {
                continue;
            }

            // check its enabled in the config
            if (data_dict.dashboard.metrics[metric_list[metric_cycle_index]]) {
                metric_key = metric_list[metric_cycle_index];
                break;
            }
        }

    }
    else {
        console.log("No metrics in data dict");
        console.log(data_dict);
    }

    display_data();
}                                               

// manual cycle of metric index
// and restart of timer
// used for UI-based tap cycling
function ui_cycle_metric_index() {
    console.log("ui_cycle_metric_index()");
    clearInterval(metric_cycle_timer);
    cycle_metric_index();
    metric_cycle_timer = setInterval(cycle_metric_index, metric_cycle_interval);
}

// manual cycle of layout
// used for UI-based tap cycling
// ignores cycling to portrait layout
function ui_cycle_layout() {
    console.log("ui_cycle_layout()");
    ui_layout_list = ['small', 'default', 'dual-metrics', 'metrics'];
    layout = get_query_arg("layout");
    if (layout == undefined) {
        // pick a dummy value
        // the find will return a -1 and then the 
        // modulo will moved that to the 0 and select
        // the first layout
        layout = 'bogus';
    }
    layout_index = ui_layout_list.indexOf(layout)
    layout_index = (layout_index + 1) % ui_layout_list.length;
    layout = ui_layout_list[layout_index];
    console.log("forced layout to:" + layout);
    window.location.replace(get_redirect_url("layout", layout));
}


function populate_metrics(metrics_id, metric_key) {
    metrics_a_source = data_dict.metrics[metric_key];

    $("#" + metrics_id + "_titletext").html(metrics_a_source['title']);

    // select units
    if (metric_key == 'live'){
        std_energy_unit = 'kW';
        mega_energy_unit = 'mW';
        milli_energy_unit = 'W';
    }
    else {
        std_energy_unit = 'kWh';
        mega_energy_unit = 'mWh';
        milli_energy_unit = 'Wh';
    }

    value_dict = format_energy_value(metrics_a_source.import, 
                                     std_energy_unit, 
                                     mega_energy_unit, 
                                     milli_energy_unit);
    $("#" + metrics_id + "_import").html(value_dict['value']);
    $("#" + metrics_id + "_import_unit").html(value_dict['unit']);

    if (metrics_a_source.import > 0) {
        $("#" + metrics_id + "_import").removeClass().addClass("metric metric-red");
        $("#" + metrics_id + "_import_icon").removeClass().addClass("material-icons metric metric-red");
        $("#" + metrics_id + "_import_unit").removeClass().addClass("metric-unit metric-red");
    }
    else {
        $("#" + metrics_id + "_import").removeClass().addClass("metric metric-green");
        $("#" + metrics_id + "_import_icon").removeClass().addClass("material-icons metric metric-green");
        $("#" + metrics_id + "_import_unit").removeClass().addClass("metric-unit metric-green");
    }

    value_dict = format_energy_value(metrics_a_source.solar, 
                                     std_energy_unit, 
                                     mega_energy_unit, 
                                     milli_energy_unit);
    $("#" + metrics_id + "_solar").html(value_dict['value']);
    $("#" + metrics_id + "_solar_unit").html(value_dict['unit']);

    if (metrics_a_source.solar > 0) {
        $("#" + metrics_id + "_solar").removeClass().addClass("metric metric-yellow");
        $("#" + metrics_id + "_solar_icon").removeClass().addClass("material-icons metric metric-yellow");
        $("#" + metrics_id + "_solar_unit").removeClass().addClass("metric-unit metric-yellow");
    }
    else {
        $("#" + metrics_id + "_solar").removeClass().addClass("metric metric-grey");
        $("#" + metrics_id + "_solar_icon").removeClass().addClass("material-icons metric metric-grey");
        $("#" + metrics_id + "_solar_unit").removeClass().addClass("metric-unit metric-grey");
    }

    value_dict = format_energy_value(metrics_a_source.export, 
                                     std_energy_unit, 
                                     mega_energy_unit, 
                                     milli_energy_unit);
    $("#" + metrics_id + "_export").html(value_dict['value']);
    $("#" + metrics_id + "_export_unit").html(value_dict['unit']);

    if (metrics_a_source.export > 0) {
        $("#" + metrics_id + "_export").removeClass().addClass("metric metric-blue");
        $("#" + metrics_id + "_export_icon").removeClass().addClass("material-icons metric metric-blue");
        $("#" + metrics_id + "_export_unit").removeClass().addClass("metric-unit metric-blue");
    }
    else {
        $("#" + metrics_id + "_export").removeClass().addClass("metric metric-grey");
        $("#" + metrics_id + "_export_icon").removeClass().addClass("material-icons metric metric-grey");
        $("#" + metrics_id + "_export_unit").removeClass().addClass("metric-unit metric-grey");
    }

    value_dict = format_energy_value(metrics_a_source.consumed, 
                                     std_energy_unit, 
                                     mega_energy_unit, 
                                     milli_energy_unit);
    $("#" + metrics_id + "_consumed").html(value_dict['value']);
    $("#" + metrics_id + "_consumed_unit").html(value_dict['unit']);

    if (metrics_a_source.import <= 0) {
        $("#" + metrics_id + "_consumed").removeClass().addClass("metric metric-green");
        $("#" + metrics_id + "_consumed_icon").removeClass().addClass("material-icons metric metric-green");
        $("#" + metrics_id + "_consumed_unit").removeClass().addClass("metric-unit metric-green");
    }
    else if (metrics_a_source.solar > 0) {
        $("#" + metrics_id + "_consumed").removeClass().addClass("metric metric-orange");
        $("#" + metrics_id + "_consumed_icon").removeClass().addClass("material-icons metric metric-orange");
        $("#" + metrics_id + "_consumed_unit").removeClass().addClass("metric-unit metric-orange");
    }
    else {
        $("#" + metrics_id + "_consumed").removeClass().addClass("metric metric-red");
        $("#" + metrics_id + "_consumed_icon").removeClass().addClass("material-icons metric metric-red");
        $("#" + metrics_id + "_consumed_unit").removeClass().addClass("metric-unit metric-red");
    }

    if ('battery_charge' in metrics_a_source) {
        $("#" + metrics_id + "_battery_charge_col").show();
        value_dict = format_energy_value(metrics_a_source.battery_charge, 
                                         std_energy_unit, 
                                         mega_energy_unit, 
                                         milli_energy_unit);
        $("#" + metrics_id + "_battery_charge").html(value_dict['value']);
        $("#" + metrics_id + "_battery_charge_unit").html(value_dict['unit']);

        if (metrics_a_source.battery_charge > 0) {
            $("#" + metrics_id + "_battery_charge").removeClass().addClass("metric metric-charge");
            $("#" + metrics_id + "_battery_charge_icon").removeClass().addClass("material-icons metric metric-charge");
            $("#" + metrics_id + "_battery_charge_unit").removeClass().addClass("metric-unit metric-charge");
        }
        else {
            $("#" + metrics_id + "_battery_charge").removeClass().addClass("metric metric-grey");
            $("#" + metrics_id + "_battery_charge_icon").removeClass().addClass("material-icons metric metric-grey");
            $("#" + metrics_id + "_battery_charge_unit").removeClass().addClass("metric-unit metric-grey");
        }
    }
    else {
        $("#" + metrics_id + "_battery_charge_col").hide();
    }

    if ('battery_discharge' in metrics_a_source) {
        $("#" + metrics_id + "_battery_discharge_col").show();
        value_dict = format_energy_value(metrics_a_source.battery_discharge, 
                                         std_energy_unit, 
                                         mega_energy_unit, 
                                         milli_energy_unit);
        $("#" + metrics_id + "_battery_discharge").html(value_dict['value']);
        $("#" + metrics_id + "_battery_discharge_unit").html(value_dict['unit']);

        if (metrics_a_source.battery_discharge > 0) {
            $("#" + metrics_id + "_battery_discharge").removeClass().addClass("metric metric-discharge");
            $("#" + metrics_id + "_battery_discharge_icon").removeClass().addClass("material-icons metric metric-discharge");
            $("#" + metrics_id + "_battery_discharge_unit").removeClass().addClass("metric-unit metric-discharge");
        }
        else {
            $("#" + metrics_id + "_battery_discharge").removeClass().addClass("metric metric-grey");
            $("#" + metrics_id + "_battery_discharge_icon").removeClass().addClass("material-icons metric metric-grey");
            $("#" + metrics_id + "_battery_discharge_unit").removeClass().addClass("metric-unit metric-grey");
        }
    }
    else {
        $("#" + metrics_id + "_battery_discharge_col").hide();
    }

    if ('battery_soc' in metrics_a_source) {
        $("#" + metrics_id + "_battery_soc_col").show();
        battery_soc_icon = format_battery_icon(metrics_a_source.battery_soc);
        $("#" + metrics_id + "_battery_soc").html(metrics_a_source.battery_soc);
        $("#" + metrics_id + "_battery_soc_unit").html('%');
        $("#" + metrics_id + "_battery_soc_icon").html(battery_soc_icon);

        if (metrics_a_source.battery_soc >= 50) {
            $("#" + metrics_id + "_battery_soc").removeClass().addClass("metric metric-green");
            $("#" + metrics_id + "_battery_soc_icon").removeClass().addClass("material-icons metric metric-green");
            $("#" + metrics_id + "_battery_soc_unit").removeClass().addClass("metric-unit metric-green");
        }
        else if (metrics_a_source.battery_soc >= 30) {
            $("#" + metrics_id + "_battery_soc").removeClass().addClass("metric metric-orange");
            $("#" + metrics_id + "_battery_soc_icon").removeClass().addClass("material-icons metric metric-orange");
            $("#" + metrics_id + "_battery_soc_unit").removeClass().addClass("metric-unit metric-orange");
        }
        else {
            $("#" + metrics_id + "_battery_soc").removeClass().addClass("metric metric-red");
            $("#" + metrics_id + "_battery_soc_icon").removeClass().addClass("material-icons metric metric-red");
            $("#" + metrics_id + "_battery_soc_unit").removeClass().addClass("metric-unit metric-red");
        }
    }
    else {
        $("#" + metrics_id + "_battery_soc_col").hide();
    }

    value_dict = format_energy_value(metrics_a_source.co2, 'kg', 'mt', 'g');
    $("#" + metrics_id + "_co2").html(value_dict['value']);
    $("#" + metrics_id + "_co2_unit").html(value_dict['unit']);

    if (metrics_a_source.co2 > 0) {
        $("#" + metrics_id + "_co2").removeClass().addClass("metric metric-green");
        $("#" + metrics_id + "_co2_icon").removeClass().addClass("material-icons metric metric-green");
        $("#" + metrics_id + "_co2_unit").removeClass().addClass("metric-unit metric-green");
    }
    else {
        $("#" + metrics_id + "_co2").removeClass().addClass("metric metric-grey");
        $("#" + metrics_id + "_co2_icon").removeClass().addClass("material-icons metric metric-grey");
        $("#" + metrics_id + "_co2_unit").removeClass().addClass("metric-unit metric-grey");
    }

    value_dict = format_trees(metrics_a_source.trees);
    $("#" + metrics_id + "_trees").html(value_dict['value']);

    if (metrics_a_source.trees > 0) {
        $("#" + metrics_id + "_trees").removeClass().addClass("metric metric-green");
        $("#" + metrics_id + "_trees_icon").removeClass().addClass("material-icons metric metric-green");
        $("#" + metrics_id + "_trees_unit").removeClass().addClass("metric-unit metric-green");
    }
    else {
        $("#" + metrics_id + "_trees").removeClass().addClass("metric metric-grey");
        $("#" + metrics_id + "_trees_icon").removeClass().addClass("material-icons metric metric-grey");
        $("#" + metrics_id + "_trees_unit").removeClass().addClass("metric-unit metric-grey");
    }

}

// renders and displays the current dashboard
function display_data() {
    console.log("display_data()");

    // switch from splash to dashboard 
    // only when we have data to show
    // this is a once-off occurrence at the start
    if ('last_updated' in data_dict && 
        data_dict.last_updated > 0) {
        $("#splash").hide();
    }
    else {
        $("#splash").show();
        $("#dashboard").hide();
        // display message based on configured state
        if (data_dict['configured'] == false) {
            $("#splash_text").html('Please click setup icon or visit: ' + data_dict['setup_url']);
        }
        else {
            $("#splash_text").html('Waiting for data...');
        }
        return;
    }

    // populate metrics
    switch(layout) {
      case "metrics":
      // 4 fixed metric sets
      populate_metrics("metrics_a", "live");
      populate_metrics("metrics_b", "today");
      populate_metrics("metrics_c", "this_month");
      populate_metrics("metrics_d", "last_12_months");
      break;

      case "dual-metrics":
      // dual-donut + dual metrics layout
      metrics_a_source = data_dict.metrics["live"];
      metrics_b_source = data_dict.metrics[metric_key];
      $("#donut_a_title").html(metrics_a_source['title']);
      $("#donut_b_title").html(metrics_b_source['title']);

      populate_metrics("metrics_a", "live");
      $("#metrics_a_title").hide();

      populate_metrics("metrics_b", metric_key);
      $("#metrics_b_title").hide();
      break;

      default:
      // typical layout of using a single donut and one set of metrics
      metrics_a_source = data_dict.metrics[metric_key];
      $("#donut_a_title").html(metrics_a_source['title']);

      populate_metrics("metrics_a", metric_key);
      $("#metrics_a_title").hide();
      break;
    }

    // show the dashboard
    $("#dashboard").show();

    // onto charts
    render_charts();
}

function render_donut(donut_id,
                      metric_key,
                      donut_options,
                      series_labels,
                      donut_series_list) {
    console.log(`rendering donut ${donut_id} with ${metric_key} metrics`);

    metrics_source = data_dict.metrics[metric_key];

    var metrics_data = new google.visualization.DataTable();
    metrics_data.addColumn('string', 'Source');
    metrics_data.addColumn('number', 'kWh');

    // calculate total series value
    var total_series_value = 0;
    for (series_field of donut_series_list) {
        series_value = metrics_source[series_field];
        if (series_value == undefined) {
            series_value = 0;
        }
        total_series_value += series_value;
    }

    for (series_field of donut_series_list) {
        // calculate percentage of total
        // for the small screen donut label
        series_value = metrics_source[series_field];
        if (series_value == undefined) {
            series_value = 0;
        }
        series_percentage = series_value / total_series_value * 100;
        if (layout == "small") {
            // label + percentage
            series_label = `${series_labels[series_field]} ${series_percentage.toFixed(1)}%`;
        }
        else {
            // label only for legend
            // displayed value will be the percentage
            series_label = series_labels[series_field];
        }
        metrics_data.addRows([
            // graph value times 1000 for issues with small values
            [series_label, series_value * 1000]
        ]);
    }

    // draw donut 
    donut_chart = new google.visualization.PieChart(document.getElementById(donut_id));
    donut_chart.draw(metrics_data, donut_options);

    return donut_chart;
}

function render_column_chart(chart_id,
                             data_key,
                             chart_options,
                             series_labels,
                             time_unit,
                             chart_series_list) {

    console.log(`rendering column chart ${chart_id} with ${data_key} data`);
    column_chart = new google.visualization.ColumnChart(document.getElementById(chart_id));

    var chart_data = new google.visualization.DataTable();

    // time unit is actually a number (int)
    // but we chart it as a string
    chart_data.addColumn('string', time_unit);

    for (series_field of chart_series_list) {
        chart_data.addColumn('number', series_labels[series_field]);
    }

    chart_data.addRows(data_dict[data_key].length);
    row = 0
    for (const item of data_dict[data_key]) {
        // format as hh:00
        time_str = item.hour.toString().padStart(2, '0') 
        chart_data.setCell(row, 0, time_str);
        col = 1
        for (series_field of chart_series_list) {
            if (series_field in item) {
                chart_data.setCell(row, col, item[series_field].toFixed(2));
            }
            col += 1;
        }
        row += 1;
    }

    chart_options.hAxis.title = time_unit;
    column_chart.draw(chart_data, chart_options);

    return column_chart;
}


// chart globals to avoid memory growth
var donut_a_chart;
var donut_b_chart;
var day_chart;
var month_chart;
var year_chart;
var day_chart_ts = 0;
var month_chart_ts = 0;
var year_chart_ts = 0;

// render the Google charts
function render_charts() {
    console.log("render_charts()");

    column_chart_height = (window.innerHeight) * 0.3;

    switch(layout) {
      case "small":
      donut_chart_height = (window.innerHeight) * 0.9;
      break;

      case "portrait":
      donut_chart_height = (window.innerHeight) * 0.4;
      break;

      case "default":
      case "dual-metrics":
      donut_chart_height = (window.innerHeight) * 0.40;
      break;
    }

    // legend font size
    // this is a bit of work
    // we parse layout and determine the CSS ref variable to 
    // use for legend font. Google does not allow us pass that CSS
    // in for the font size. So it needs to rendered in pixels
    switch(layout) {
      case "default":
      case "dual-metrics":
      legend_font_size_var = "--legend-font-size-default";
      slice_font_size_var = "--slice-font-size-default";
      break;

      case "small":
      legend_font_size_var = "--legend-font-size-small";
      slice_font_size_var = "--slice-font-size-small";
      break;

      case "portrait":
      legend_font_size_var = "--legend-font-size-portrait";
      slice_font_size_var = "--slice-font-size-portrait";
      break;
    }

    // expand that variable into the computed size (which will be x.xxvw)
    legend_font_vw_size = getComputedStyle(document.documentElement).getPropertyValue(legend_font_size_var);
    slice_font_vw_size = getComputedStyle(document.documentElement).getPropertyValue(slice_font_size_var);

    // strip the trailing "vw" text
    // and get the numerical value
    legend_font_vw_number = Number(legend_font_vw_size.replace('vw', ''));
    slice_font_vw_number = Number(slice_font_vw_size.replace('vw', ''));

    // Convert into raw pixels using screen width
    legend_font_px_size = (legend_font_vw_number * window.innerWidth) / 100;
    slice_font_px_size = (slice_font_vw_number * window.innerWidth) / 100;

    // series fields and colour assignments
    const series_fields = [
        "import", 
        "consumed", 
        "solar", 
        "solar_consumed", 
        "export", 
        "battery_charge", 
        "battery_discharge"
    ];

    const series_labels = {
        "import": "Grid",
        "consumed": "Consumed",
        "solar": "PV",
        "solar_consumed": "PV Consumed",
        "export": "PV Export",
        "battery_charge": "Battery (+)",
        "battery_discharge": "Battery (-)",
    };

    const series_colours = {
        "import": "#990000",
        "consumed": "#4B0082",
        "solar": "#AAAA00",
        "solar_consumed": "#006600",
        "export": "#00487F",
        "battery_charge": "#5C985C",
        "battery_discharge": "#925EAE",
    };

    // construct donut series and colour lists
    donut_series_list = []
    donut_colour_list = []

    for (series_field of series_fields) {
        if (data_dict.dashboard.donut[series_field]) {
            donut_series_list.push(series_field)
            donut_colour_list.push(series_colours[series_field])
        }
    }

    var donut_options = {
        colors: donut_colour_list,
        pieHole: 0.4,
        height: donut_chart_height,
        chartArea:{
            top:10,
            bottom:40,
            left:0,
            right:0,
        },
        legend: { 
            alignment: 'center', 
            position: 'bottom', 
            maxLines: 3,
            textStyle: {
                fontSize: legend_font_px_size * 0.9,
                color: 'gray'
            },
        },
        pieSliceText: 'percentage',
        pieSliceTextStyle: {
            fontSize: slice_font_px_size,
        },
        backgroundColor: { 
            fill:'transparent' 
        },
        pieSliceBorderColor: 'transparent',
        tooltip: { 
            showColorCode: true,
            textStyle: {
                fontSize: legend_font_px_size
            }
        }
    };

    if (layout == "small") {
        // hide legend and display label instead of percentage
        donut_options.legend.position = 'none';
        donut_options.pieSliceText = 'label';
        donut_options.pieSliceTextStyle.fontSize = legend_font_px_size * 0.9;
    }

    // donuts are drawn on all layouts except metrics
    if (layout != "metrics") {

        // donut a
        // standard left-side donut used for cycled metrics

        // clear existing data
        // prevents a memory leak
        if (donut_a_chart != undefined) {
            donut_a_chart.clearChart();
        }

        // metrics data source
        // dual-donut layout uses the live metric on the left side
        if (layout == "dual-metrics") {
            // dual-donut layout
            // donut a is fixed to live metric
            donut_metric_key = "live";
        }
        else {
            // cycled metric
            donut_metric_key = metric_key
        }

        donut_a_chart = render_donut("donut_a_chart", 
                                     metric_key, 
                                     donut_options, 
                                     series_labels,
                                     donut_series_list);
    }

    if (layout == "dual-metrics") {
        // donut b
        // right-side donut used for cycled metrics

        // clear existing data
        // prevents a memory leak
        if (donut_b_chart != undefined) {
            donut_b_chart.clearChart();
        }
        donut_b_chart = render_donut("donut_b_chart", 
                                     metric_key, 
                                     donut_options, 
                                     series_labels,
                                     donut_series_list);
    }

    // bar charts
    // only applies to portrait or default layouts
    if (layout == "portrait" || layout == "default") {

        // construct bar_chart series and colour lists
        bar_chart_series_list = []
        bar_chart_colour_list = []

        for (series_field of series_fields) {
            if (data_dict.dashboard.bar_chart[series_field]) {
                bar_chart_series_list.push(series_field)
                bar_chart_colour_list.push(series_colours[series_field])
            }
        }

        // common options
        // but the hAxis title will be tweaked
        var bar_chart_options = {
            colors: bar_chart_colour_list,
            hAxis: {
                title: 'Hour',
                titleTextStyle: {
                    color: 'white',
                    fontSize: legend_font_px_size,
                },
                textStyle: {
                    color: 'gray',
                    fontSize: legend_font_px_size * 1.0,
                },
            },
            vAxis: {
                title: 'kwH',
                titleTextStyle: {
                    color: 'white',
                    fontSize: legend_font_px_size,
                },
                textStyle: {
                    color: 'gray',
                    fontSize: legend_font_px_size * 0.75,
                },
                gridlines: {
                    color: '#404040', 
                },
                minorGridlines: {
                    color: '#404040', 
                },
            },
            chartArea:{
                left:70, // needed for the kWh counts to fit
                right:70, // matched for centered look
                backgroundColor: {
                    // chart border
                    stroke: 'gray',
                    strokeWidth: 0
                }
            },
            axisTitlesPosition: 'in',
            isStacked: true,
            height: column_chart_height,
            legend: { 
                position: 'top', 
                alignment: 'center', 
                maxLines: 3,
                textStyle: {
                    fontSize: legend_font_px_size * 0.9,
                    color: 'gray'
                },
            },
            backgroundColor: { 
                fill:'transparent' 
            },
            focusTarget: 'category',
            tooltip: { 
                showColorCode: true,
                textStyle: {
                    fontSize: legend_font_px_size
                }
            }
        };

        // day
        if (data_dict.day.length > 0 && 
            day_chart_ts != data_dict.day_last_updated) {
            day_chart_ts = data_dict.day_last_updated;

            if (day_chart != undefined) {
                day_chart.clearChart();
            }
            day_chart = render_column_chart("day_google_chart",
                                            'day',
                                            bar_chart_options,
                                            series_labels,
                                            'Hour',
                                            bar_chart_series_list);

            chart_title = `Last ${data_dict.day.length} Hours`;
            $("#day_chart_title").html(chart_title);
        }

        // month 
        if (data_dict.month.length > 0 && 
            month_chart_ts != data_dict.month_last_updated) {
            month_chart_ts = data_dict.month_last_updated;

            if (month_chart != undefined) {
                month_chart.clearChart();
            }

            month_chart = render_column_chart("month_google_chart",
                                            'month',
                                            bar_chart_options,
                                            series_labels,
                                            'Day',
                                            bar_chart_series_list);

            chart_title = `Last ${data_dict.month.length} Days`;
            $("#month_chart_title").html(chart_title);
        }

        // year
        if (data_dict.year.length > 0 && 
            year_chart_ts != data_dict.year_last_updated) {
            year_chart_ts = data_dict.year_last_updated;

            if (year_chart != undefined) {
                year_chart.clearChart();
            }
            year_chart = render_column_chart("year_google_chart",
                                            'year',
                                            bar_chart_options,
                                            series_labels,
                                            'Month',
                                            bar_chart_series_list);

            chart_title = `Last ${data_dict.year.length} Months`;
            $("#year_chart_title").html(chart_title);
        }
    }
}
