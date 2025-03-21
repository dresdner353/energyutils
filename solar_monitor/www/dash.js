// get query arg from page
function get_query_arg(arg) {
    value = undefined;
    value_start = location.search.split(arg + '=')[1];
    if (value_start != undefined) {
        value = value_start.split('&')[0];
    }

    return value;
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
// and forced layout from query args
var layout;
var forced_layout = undefined;
var forced_margin = undefined;

// document load
$( document ).ready(function() {
    console.log("ready()");
    // hide the dashboard and splash initially
    $("#dashboard").hide();
    $("#splash").show();

    // set dash to blank text
    // layout will over-ride this
    $("#dashboard").html("");

    // try to determine optional forced layout
    forced_layout = get_query_arg("layout");
    forced_margin = get_query_arg("margin");

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

    metric_donut_html = ` 
            <div id="metric_donut_chart" class="card-transparent text-white text-center mt-0">
                <div class="card-body text-center">
                    <center>
                        <a href="/admin"><div id="metric_donut_title" class="title"></div></a>
                        <div onclick="ui_cycle_forced_layout()" id="donut_chart"></div>
                    </center>
                </div>
            </div>
            `;

    metrics_html_tmpl = `
                <div onclick="ui_cycle_metric_index()" id="<METRICS-ID>" class="container text-white text-center">
                    <div id="<METRICS-ID>_title" class="row row-cols-1 mt-5">
                        <div class="col">
                            <center>
                                <div onclick="ui_cycle_forced_layout()" id="<METRICS-ID>_titletext" class="title text-white text-center"></div>
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

    // large screen model
    // two columns, split 5:7 on bootstrap 12 breakpoints
    // left column has the donut and metrics and right
    // has the three column charts
    large_screen_layout = `
                <div id="master" class="container-fluid" data-bs-theme="dark">
                    <div class="row">
                        <div class="col col-5 mt-0">
                            <div id="metric_donut_insert" class="row">
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

    // small screen model
    // 5:7 split columns
    // donut on  left, metrics stack on right
    small_screen_layout = `
                <div id="master" class="container-fluid" data-bs-theme="dark">
                    <div class="row align-items-center">
                        <div id="metric_donut_insert" class="col col-5 mt-2">
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
    portrait_screen_layout = `
                <div class="container-fluid" data-bs-theme="dark">
                    <div id="metric_donut_insert" class="row">
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

    // large metrics-only screen model
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

    // forced layout
    if (forced_layout != undefined) {
        if (["small", "large", "portrait", "metrics"].includes(forced_layout)) {
            layout = forced_layout;
        }
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
            layout = "large";
        }
    }

    // metric a-d layouts from common template
    metrics_a_html = metrics_html_tmpl.replaceAll("<METRICS-ID>", "metrics_a");
    metrics_b_html = metrics_html_tmpl.replaceAll("<METRICS-ID>", "metrics_b");
    metrics_c_html = metrics_html_tmpl.replaceAll("<METRICS-ID>", "metrics_c");
    metrics_d_html = metrics_html_tmpl.replaceAll("<METRICS-ID>", "metrics_d");

    if (layout == "portrait") {
        // portrait view
        $("#dashboard").html(portrait_screen_layout);
        $("#metric_donut_insert").html(metric_donut_html);
        $("#metrics_a_insert").html(metrics_a_html);
        $("#day_column_chart_insert").html(day_column_chart_html);
        $("#month_column_chart_insert").html(month_column_chart_html);
        $("#year_column_chart_insert").html(year_column_chart_html);

        // set the portrait screen font sizes
        document.body.style.setProperty("--metric-font-size", 'var(--metric-font-size-portrait-screen)');
        document.body.style.setProperty("--icon-font-size", 'var(--icon-font-size-portrait-screen)');
        document.body.style.setProperty("--metric-unit-font-size", 'var(--metric-unit-font-size-portrait-screen)');
        document.body.style.setProperty("--title-font-size", 'var(--title-font-size-portrait-screen)');
        document.body.style.setProperty("--legend-font-size", 'var(--legend-font-size-portrait-screen)');
        document.body.style.setProperty("--slice-font-size", 'var(--slice-font-size-portrait-screen)');
    }

    if (layout == "small") {
        // small screen landscape
        layout = "small";
        $("#dashboard").html(small_screen_layout);
        $("#metric_donut_insert").html(metric_donut_html);
        $("#metrics_a_insert").html(metrics_a_html);

        // set the small screen font sizes
        document.body.style.setProperty("--metric-font-size", 'var(--metric-font-size-small-screen)');
        document.body.style.setProperty("--icon-font-size", 'var(--icon-font-size-small-screen)');
        document.body.style.setProperty("--metric-unit-font-size", 'var(--metric-unit-font-size-small-screen)');
        document.body.style.setProperty("--title-font-size", 'var(--title-font-size-small-screen)');
        document.body.style.setProperty("--legend-font-size", 'var(--legend-font-size-small-screen)');
        document.body.style.setProperty("--slice-font-size", 'var(--slice-font-size-small-screen)');
    }

    if (layout == "large") {
        // large screen landscape
        $("#dashboard").html(large_screen_layout);
        $("#metric_donut_insert").html(metric_donut_html);
        $("#metrics_a_insert").html(metrics_a_html);
        $("#day_column_chart_insert").html(day_column_chart_html);
        $("#month_column_chart_insert").html(month_column_chart_html);
        $("#year_column_chart_insert").html(year_column_chart_html);

        // set the large screen smaller font sizes
        document.body.style.setProperty("--metric-font-size", 'var(--metric-font-size-large-screen)');
        document.body.style.setProperty("--icon-font-size", 'var(--icon-font-size-large-screen)');
        document.body.style.setProperty("--metric-unit-font-size", 'var(--metric-unit-font-size-large-screen)');
        document.body.style.setProperty("--title-font-size", 'var(--title-font-size-large-screen)');
        document.body.style.setProperty("--legend-font-size", 'var(--legend-font-size-large-screen)');
        document.body.style.setProperty("--slice-font-size", 'var(--slice-font-size-large-screen)');
    }

    if (layout == "metrics") {
        // large screen landscape
        $("#dashboard").html(metrics_screen_layout);
        $("#metrics_a_insert").html(metrics_a_html);
        $("#metrics_b_insert").html(metrics_b_html);
        $("#metrics_c_insert").html(metrics_c_html);
        $("#metrics_d_insert").html(metrics_d_html);

        // set the large screen smaller font sizes
        document.body.style.setProperty("--metric-font-size", 'var(--metric-font-size-large-screen)');
        document.body.style.setProperty("--icon-font-size", 'var(--icon-font-size-large-screen)');
        document.body.style.setProperty("--metric-unit-font-size", 'var(--metric-unit-font-size-large-screen)');
        document.body.style.setProperty("--title-font-size", 'var(--title-font-size-large-screen)');
        document.body.style.setProperty("--legend-font-size", 'var(--legend-font-size-large-screen)');
        document.body.style.setProperty("--slice-font-size", 'var(--slice-font-size-large-screen)');
    }

    console.log("Set layout to " + layout);

    if (forced_margin != undefined) {
        $("#master").removeClass().addClass(`container-fluid mt-${forced_margin} mb-${forced_margin} mx-${forced_margin}`);
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
var refresh_error_count = 0;
var first_refresh = 1;

// refreshes API data for 
// constructing the dashboard
function refresh_data() {
    console.log("refresh_data()");

    // get the latest data
    var data_request = $.get('/data');

    // display the get error
    data_request.fail(function() {
        refresh_error_count += 1;
        $("#metric_donut_title").html(`Data Refresh Failure #${refresh_error_count}`);
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
var metrics_a_metric_index = -1; // init only
var metrics_a_metric_key = 'live';

// rotates the current metric index as 
// part of the timed cycling
function cycle_metric_index() {
    console.log("cycle_metric_index()");

    if ('metrics' in data_dict) {
        metric_list = Object.keys(data_dict.metrics);
        for (i = 0; i < metric_list.length; i++) {
            metrics_a_metric_index = (metrics_a_metric_index + 1) % metric_list.length;

            // check its enabled in the config
            if (data_dict.dashboard.metrics[metric_list[metrics_a_metric_index]]) {
                metrics_a_metric_key = metric_list[metrics_a_metric_index];
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

// forced layout cycling index
var forced_layout_index = -1; // init only

// manual cycle of forced layout
// used for UI-based tap cycling
// only cycles between small and large
function ui_cycle_forced_layout() {
    console.log("ui_cycle_forced_layout()");
    forced_layout_list = ['small', 'large', 'metrics'];
    forced_layout_index = (forced_layout_index + 1) % forced_layout_list.length;
    forced_layout = forced_layout_list[forced_layout_index];
    console.log("forced layout to:" + forced_layout);
    set_layout();
    display_data();
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
        'metrics' in data_dict && 
        data_dict.last_updated > 0) {
        $("#splash").hide();
    }
    else {
        // display message based on configured state
        if (data_dict['configured'] == false) {
            $("#splash_text").html('Please click setup icon above to continue');
        }
        else {
            $("#splash_text").html('Waiting for data...');
        }
        return;
    }

    // reset error count
    refresh_error_count = 0;

    // Aggregate metrics
    if (layout == "metrics") {
        populate_metrics("metrics_a", "live");
        populate_metrics("metrics_b", "today");
        populate_metrics("metrics_c", "this_month");
        populate_metrics("metrics_d", "last_12_months");
    }
    else {
        // typical layout of using a donut and one set of metrics
        metrics_a_source = data_dict.metrics[metrics_a_metric_key];
        $("#metric_donut_title").html(metrics_a_source['title']);

        populate_metrics("metrics_a", metrics_a_metric_key);
        $("#metrics_a_title").hide();
    }

    // show the dashboard
    $("#dashboard").show();

    // onto charts
    render_charts();
}

// chart globals to avoid memory growth
var donut_chart;
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

      case "large":
      donut_chart_height = (window.innerHeight) * 0.40;
      break;

      default:
      // unknown layout, do not render
      return;
      break;
    }

    // legend font size
    // this is a bit of work
    // we parse layout and determine the CSS ref variable to 
    // use for legend font. Google does not allow us pass that CSS
    // in for the font size. So it needs to rendered in pixels
    switch(layout) {
      case "large":
      legend_font_size_var = "--legend-font-size-large-screen";
      slice_font_size_var = "--slice-font-size-large-screen";
      break;
      case "small":
      legend_font_size_var = "--legend-font-size-small-screen";
      slice_font_size_var = "--slice-font-size-small-screen";
      break;
      case "portrait":
      legend_font_size_var = "--legend-font-size-portrait-screen";
      slice_font_size_var = "--slice-font-size-portrait-screen";
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
    const series_fields = ["import", "consumed", "solar", "solar_consumed", "export", "battery_charge", "battery_discharge"];

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

    // live power distribution 

    if (donut_chart != undefined) {
        donut_chart.clearChart();
    }
    console.log("rendering donut chart");
    donut_chart = new google.visualization.PieChart(document.getElementById('donut_chart'));

    // donut options (shared)

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

    // agg
    metrics_a_source = data_dict.metrics[metrics_a_metric_key];
    var metrics_a_data = new google.visualization.DataTable();
    metrics_a_data.addColumn('string', 'Source');
    metrics_a_data.addColumn('number', 'kWh');

    // calculate total series value
    var total_series_value = 0;
    for (series_field of donut_series_list) {
        series_value = metrics_a_source[series_field];
        if (series_value == undefined) {
            // FIXME need to investigate why this can be undefined
            series_value = 0;
        }
        total_series_value += series_value;
    }

    for (series_field of donut_series_list) {
        // calculate percentage of total
        // for the small screen donut label
        series_value = metrics_a_source[series_field];
        if (series_value == undefined) {
            // FIXME need to investigate why this can be undefined
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
        metrics_a_data.addRows([
            // graph value times 1000 for issues with small values
            [series_label, series_value * 1000]
        ]);
    }

    // draw donut
    donut_chart.draw(metrics_a_data, donut_options);

    // bar charts
    // only applies to portrait or large layouts
    if (layout == "portrait" || layout == "large") {

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

            console.log("rendering day chart");

            if (day_chart != undefined) {
                day_chart.clearChart();
            }
            day_chart = new google.visualization.ColumnChart(document.getElementById('day_google_chart'));

            var day_data = new google.visualization.DataTable();

            // hour is actually a number (int)
            // but we chart it as a string
            day_data.addColumn('string', 'Hour');

            for (series_field of bar_chart_series_list) {
                day_data.addColumn('number', series_labels[series_field]);
            }

            day_data.addRows(data_dict.day.length);
            row = 0
            for (const item of data_dict.day) {
                // format as hh:00
                time_str = item.hour.toString().padStart(2, '0') 
                day_data.setCell(row, 0, time_str);
                col = 1
                for (series_field of bar_chart_series_list) {
                    if (series_field in item) {
                        day_data.setCell(row, col, item[series_field].toFixed(2));
                    }
                    col += 1;
                }
                row += 1;
            }

            bar_chart_options.hAxis.title = 'Hour';
            day_chart.draw(day_data, bar_chart_options);

            chart_title = `Last ${data_dict.day.length} Hours`;
            $("#day_chart_title").html(chart_title);
        }

        // month 
        if (data_dict.month.length > 0 && 
            month_chart_ts != data_dict.month_last_updated) {
            month_chart_ts = data_dict.month_last_updated;

            console.log("rendering month chart");

            if (month_chart != undefined) {
                month_chart.clearChart();
            }
            month_chart = new google.visualization.ColumnChart(document.getElementById('month_google_chart'));

            var month_data = new google.visualization.DataTable();
            // present int day number as string
            month_data.addColumn('string', 'Day');

            for (series_field of bar_chart_series_list) {
                month_data.addColumn('number', series_labels[series_field]);
            }

            month_data.addRows(data_dict.month.length);
            row = 0
            for (const item of data_dict.month) {
                // Format as 'MMM dd'
                time_str = item.month + ' ' + item.day.toString().padStart(2, '0') 
                //time_str = item.day.toString().padStart(2, '0') 
                month_data.setCell(row, 0, time_str);
                col = 1
                for (series_field of bar_chart_series_list) {
                    if (series_field in item) {
                        month_data.setCell(row, col, item[series_field].toFixed(2));
                    }
                    col += 1;
                }
                row += 1;
            }

            bar_chart_options.hAxis.title = 'Day';
            bar_chart_options.legend = 'none';
            bar_chart_options.chartArea.top = 10;
            month_chart.draw(month_data, bar_chart_options);

            chart_title = `Last ${data_dict.month.length} Days`;
            $("#month_chart_title").html(chart_title);
        }

        // year
        if (data_dict.year.length > 0 && 
            year_chart_ts != data_dict.year_last_updated) {
            year_chart_ts = data_dict.year_last_updated;

            console.log("rendering year chart");

            if (year_chart != undefined) {
                year_chart.clearChart();
            }
            year_chart = new google.visualization.ColumnChart(document.getElementById('year_google_chart'));

            var year_data = new google.visualization.DataTable();
            year_data.addColumn('string', 'Month');

            for (series_field of bar_chart_series_list) {
                year_data.addColumn('number', series_labels[series_field]);
            }

            year_data.addRows(data_dict.year.length);
            row = 0
            for (const item of data_dict.year) {
                //time_str = item.year + ' ' + item.month
                time_str = item.month
                year_data.setCell(row, 0, time_str);
                col = 1
                for (series_field of bar_chart_series_list) {
                    if (series_field in item) {
                        year_data.setCell(row, col, item[series_field].toFixed(2));
                    }
                    col += 1;
                }
                row += 1;
            }

            bar_chart_options.hAxis.title = 'Month';
            bar_chart_options.legend = 'none';
            bar_chart_options.chartArea.top = 10;
            year_chart.draw(year_data, bar_chart_options);

            chart_title = `Last ${data_dict.year.length} Months`;
            $("#year_chart_title").html(chart_title);
        }
    }
}
