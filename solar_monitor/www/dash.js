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
var refresh_interval = 1000;
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
    $("#about").hide();
    $("#splash").show();

    // set dash to blank text
    // layout will over-ride this
    $("#dashboard").html("");
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

// config timestamp
// used to detect config changes
// for layout updating
var config_ts = 0;

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

        // set layout when a config change is detected
        if (data_dict['config_ts'] != config_ts) {
            set_layout();
            cycle_metric_index();
            display_data();
            config_ts = data_dict['config_ts'];
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

    metric_card_tmpl = `
            <div onclick="ui_cycle_metric_index()" class="col" id="<METRICS-ID>_<CARD-ID>_card">
                <div class="card-transparent text-center mt-3">
                    <div class="card-body">
                        <table border="0" align="center">
                            <tr>
                                <td style="vertical-align: middle;">
                                    <span id="<METRICS-ID>_<CARD-ID>_value" style="metric metric-white"></span>&nbsp;
                                </td>
                                <td style="vertical-align: middle;" align="center">
                                    <div id="<METRICS-ID>_<CARD-ID>_icon" class="metric-icon"><i class="bi <ICON-ID>"></i></div>
                                    <div id="<METRICS-ID>_<CARD-ID>_unit" class="metric-unit metric-white"></div>
                                </td>
                            </tr>
                        </table>
                        <span id="<METRICS-ID>_<CARD-ID>_caption" class="metric-caption metric-white"></span>
                    </div>
                </div>
            </div>
            `;

    image_card_tmpl = `
            <div onclick="ui_cycle_metric_index()" class="col" id="<METRICS-ID>_<CARD-ID>_card">
                <div class="card-transparent text-center mt-3 h-100">
                    <div class="card-body align-middle h-100">
                        <br>
                        <br>
                        <br>
                        <img src="<IMAGE>" class="img-thumbnail" alt="...">
                    </div>
                </div>
            </div>
            `;

    metrics_page_html_tmpl = `
                    <div id="<METRICS-ID>_title" class="row mt-0">
                        <div class="col-12 text-center">
                                <a href="/admin">
                                <span class="title text-white text-left"></span>
                                <span id="<METRICS-ID>_titletext" class="title text-white text-left"></span>
                                </a>
                        </div>
                    </div>
                <div id="<METRICS-ID>" class="container text-white text-center">
                    <div class="row row-cols-2">
                    <CARDS>
                    </div>
                </div>

                <div id="<METRICS-ID>_installer_logo" class="row mt-2 fixed-bottom">
                    <div class="col col-11"></div>
                    <div class="col col-1 text-right">
                        <right>
                            <img src="/images/installer.png" class="img-thumbnail" alt="...">
                        </right>
                        <br>
                        <br>
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
            `;


    about_html = `
                    <div id="about_title" class="row mt-0">
                        <div class="col-12 text-center">
                                <a href="/admin">
                                <span class="about-title text-white text-center">About This Dashboard</span>
                                </a>
                        </div>
                    </div>

                    <div onclick="ui_cycle_metric_index()" class="row mt-3 text-center">

                        <div class="col col-1"></div>

                        <div class="col col-7">
                            <div class="card-transparent text-start mt-3">
                                <div class="card-body">
                                <span id="about_caption" class="about-caption metric-white"></span>
                                </div>
                            </div>
                        </div>

                        <div class="col col-1"></div>

                        <div class="col col-2">
                            <div class="card text-center mt-3">
                                <div class="card-body">
                                    <center>
                                        <img src="/images/installer.png" class="img-thumbnail" alt="...">
                                    </center>
                                </div>
                            </div>
                        </div>

                        <div class="col col-1"></div>
                    </div>

                    <div class="row mt-2 text-center fixed-bottom">
                        <center>
                            <span class="about-footer metric-yellow">Powered by SolarMon (github.com/dresdner353)</span>
                            <br>
                            <br>
                            <br>
                        </center>
                    </div>
            `;

    // layout templates
    // these will be substituted into the top-level 
    // body to completely re-arrange the screen according to the 
    // selected layout

    // default layout
    // two columns, split 5:7 on bootstrap 12 breakpoints
    // left column has the donut and metrics below and right
    // has the three stacked column charts
    default_layout = `
                <div id="master" class="container-fluid" data-bs-theme="dark">
                    <div class="row">
                        <div class="col col-5 mt-0">
                            <div id="donut_a_insert" class="row"></div>
                            <div id="metrics_a_insert" class="row"></div>
                        </div>

                        <div class="col col-7 mt-0">
                            <div id="day_column_chart_insert" class="row"></div>
                            <div id="month_column_chart_insert" class="row"></div>
                            <div id="year_column_chart_insert" class="row"></div>
                        </div>
                    </div>
                </div>
            `;

    // dual-donut layout
    // two columns, split 6:6 on bootstrap 12 breakpoints
    // left column has the live donut + live metrics 
    // right has the other cycled metrics in the same donut+metrics layout
    dual_metrics_layout = `
                <div id="master" class="container-fluid" data-bs-theme="dark">
                    <div class="row">
                        <div class="col col-6 mt-0">
                            <div id="donut_a_insert" class="row"></div>
                            <div id="metrics_a_insert" class="row"></div>
                        </div>

                        <div class="col col-6 mt-0">
                            <div id="donut_b_insert" class="row"></div>
                            <div id="metrics_b_insert" class="row"></div>
                        </div>

                    </div>
                </div>
            `;

    // single set of metrics
    single_metric_layout = `
                <div id="master" class="container-fluid" data-bs-theme="dark">
                    <div id="metrics_a_insert" class="row"></div>
                </div>
            `;

    // portrait screen model
    // vertical stack of donut, metrics and charts
    // Works for phones and portrait tablets or monitors
    portrait_layout = `
                <div class="container-fluid" data-bs-theme="dark">
                    <div id="donut_a_insert" class="row"></div>
                    <div id="metrics_a_insert" class="row"></div>
                    <div id="day_column_chart_insert" class="row"></div>
                    <div id="month_column_chart_insert" class="row"></div>
                    <div id="year_column_chart_insert" class="row"></div>
                </div>
            `;
    
    // about screen
    about_layout = `
                <div id="master" class="container-fluid " data-bs-theme="dark">
                    <div id="about_insert" class="row"></div>
                </div>
            `;

    // layout checks
    layout = undefined;

    // layout query arg (forces the layout)
    layout_arg = get_query_arg("layout");
    if (layout_arg != undefined &&
        ["default", "dual-metrics", "single-metric", "portrait"].includes(layout_arg)) {
        layout = layout_arg;
        console.log("Layout query arg:" + layout);
    }
    else {
        // auto-calculated display size and layout
        // and using configured defaults
        if (window_width <= window_height) {
            layout = "portrait";
            console.log("Auto-calculated display layout:" + layout);
        }
        else {
            layout = data_dict['dashboard']['layout'];
            console.log("configured display layout:" + layout);
        }
    }

    // last gasp protection for sanity
    if (layout == undefined) {
        layout = 'single-metric';
        console.log("Forced default display layout:" + layout);
    }

    // card definitions
    import_card_html = metric_card_tmpl.replaceAll("<CARD-ID>", "import");
    import_card_html = import_card_html.replaceAll("<ICON-ID>", "bi-plug-fill");

    consumed_card_html = metric_card_tmpl.replaceAll("<CARD-ID>", "consumed");
    consumed_card_html = consumed_card_html.replaceAll("<ICON-ID>", "bi-buildings-fill");
    
    solar_card_live_html = metric_card_tmpl.replaceAll("<CARD-ID>", "solar_live");
    solar_card_live_html = solar_card_live_html.replaceAll("<ICON-ID>", "bi-sun-fill");
    
    solar_card_today_html = metric_card_tmpl.replaceAll("<CARD-ID>", "solar_today");
    solar_card_today_html = solar_card_today_html.replaceAll("<ICON-ID>", "bi-sun-fill");
    
    solar_card_html = metric_card_tmpl.replaceAll("<CARD-ID>", "solar");
    solar_card_html = solar_card_html.replaceAll("<ICON-ID>", "bi-sun-fill");
    
    export_card_html = metric_card_tmpl.replaceAll("<CARD-ID>", "export");
    export_card_html = export_card_html.replaceAll("<ICON-ID>", "bi-box-arrow-right");
    
    battery_charge_card_html = metric_card_tmpl.replaceAll("<CARD-ID>", "battery_charge");
    battery_charge_card_html = battery_charge_card_html.replaceAll("<ICON-ID>", "bi-battery-charging");
    
    battery_discharge_card_html = metric_card_tmpl.replaceAll("<CARD-ID>", "battery_discharge");
    battery_discharge_card_html = battery_discharge_card_html.replaceAll("<ICON-ID>", "bi-battery-half");
    
    battery_soc_card_html = metric_card_tmpl.replaceAll("<CARD-ID>", "battery_soc");
    battery_soc_card_html = battery_soc_card_html.replaceAll("<ICON-ID>", "bi-battery-half");
    
    co2_card_html = metric_card_tmpl.replaceAll("<CARD-ID>", "co2");
    co2_card_html = co2_card_html.replaceAll("<ICON-ID>", "bi-fire");
    
    trees_card_html = metric_card_tmpl.replaceAll("<CARD-ID>", "trees");
    trees_card_html = trees_card_html.replaceAll("<ICON-ID>", "bi-tree-fill");

    installer_card_html = image_card_tmpl.replaceAll("<CARD-ID>", "installer");
    installer_card_html = installer_card_html.replaceAll("<IMAGE>", "/images/installer.png");

    // metric page definitions
    cards_html = import_card_html + 
        consumed_card_html + 
        solar_card_live_html +
        solar_card_today_html +
        solar_card_html +  
        export_card_html + 
        battery_charge_card_html +  
        battery_discharge_card_html + 
        battery_soc_card_html + 
        co2_card_html + 
        trees_card_html + 
        installer_card_html;
    
    // metrics a-d layouts from common template
    metrics_a_html = metrics_page_html_tmpl;
    metrics_a_html = metrics_a_html.replaceAll("<CARDS>", cards_html);
    metrics_a_html = metrics_a_html.replaceAll("<METRICS-ID>", "metrics_a");

    metrics_b_html = metrics_page_html_tmpl;
    metrics_b_html = metrics_b_html.replaceAll("<CARDS>", cards_html);
    metrics_b_html = metrics_b_html.replaceAll("<METRICS-ID>", "metrics_b");

    // donut a and b layouts from common template
    metric_donut_a_html = donut_html_tmpl.replaceAll("<DONUT-ID>", "donut_a");
    metric_donut_b_html = donut_html_tmpl.replaceAll("<DONUT-ID>", "donut_b");

    // fixed about screen
    $("#about").html(about_layout);
    $("#about_insert").html(about_html);

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

      case "single-metric":
      // single metric landscape
      $("#dashboard").html(single_metric_layout);
      $("#metrics_a_insert").html(metrics_a_html);

      // set to layout cycle to be a solar card click 
      document.getElementById("metrics_a_solar_card").onclick = ui_cycle_layout;
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
    if ('bg_colour' in data_dict['dashboard']) {
        document.body.style.setProperty("--bg-colour", data_dict['dashboard']['bg_colour']);
    }
    else {
        document.body.style.setProperty("--bg-colour", 'black');
    }

    switch(layout) {

      case "single-metric":
      // set the single metric screen font sizes
      document.body.style.setProperty("--metric-font-size", 'var(--metric-font-size-single)');
      document.body.style.setProperty("--icon-font-size", 'var(--icon-font-size-single)');
      document.body.style.setProperty("--metric-unit-font-size", 'var(--metric-unit-font-size-single)');
      document.body.style.setProperty("--metric-caption-font-size", 'var(--metric-caption-font-size-single)');
      document.body.style.setProperty("--title-font-size", 'var(--title-font-size-single)');
      document.body.style.setProperty("--legend-font-size", 'var(--legend-font-size-single)');
      document.body.style.setProperty("--slice-font-size", 'var(--slice-font-size-single)');
      break;

      case "dual-metrics":
      // set the single metric screen font sizes
      document.body.style.setProperty("--metric-font-size", 'var(--metric-font-size-dual)');
      document.body.style.setProperty("--icon-font-size", 'var(--icon-font-size-dual)');
      document.body.style.setProperty("--metric-unit-font-size", 'var(--metric-unit-font-size-dual)');
      document.body.style.setProperty("--metric-caption-font-size", 'var(--metric-caption-font-size-dual)');
      document.body.style.setProperty("--title-font-size", 'var(--title-font-size-dual)');
      document.body.style.setProperty("--legend-font-size", 'var(--legend-font-size-dual)');
      document.body.style.setProperty("--slice-font-size", 'var(--slice-font-size-dual)');
      break;

      case "portrait":
      // set the portrait screen font sizes
      document.body.style.setProperty("--metric-font-size", 'var(--metric-font-size-portrait)');
      document.body.style.setProperty("--icon-font-size", 'var(--icon-font-size-portrait)');
      document.body.style.setProperty("--metric-unit-font-size", 'var(--metric-unit-font-size-portrait)');
      document.body.style.setProperty("--metric-caption-font-size", 'var(--metric-caption-font-size-portrait)');
      document.body.style.setProperty("--title-font-size", 'var(--title-font-size-portrait)');
      document.body.style.setProperty("--legend-font-size", 'var(--legend-font-size-portrait)');
      document.body.style.setProperty("--slice-font-size", 'var(--slice-font-size-portrait)');
      break;

      default:
      // set the default screen font sizes
      document.body.style.setProperty("--metric-font-size", 'var(--metric-font-size-default)');
      document.body.style.setProperty("--icon-font-size", 'var(--icon-font-size-default)');
      document.body.style.setProperty("--metric-unit-font-size", 'var(--metric-unit-font-size-default)');
      document.body.style.setProperty("--metric-caption-font-size", 'var(--metric-caption-font-size-default)');
      document.body.style.setProperty("--title-font-size", 'var(--title-font-size-default)');
      document.body.style.setProperty("--legend-font-size", 'var(--legend-font-size-default)');
      document.body.style.setProperty("--slice-font-size", 'var(--slice-font-size-default)');
      break;
    }

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
function format_battery_class(battery_soc) {

    battery_icons = [
        'bi bi-battery',
        'bi bi-battery',
        'bi bi-battery',
        'bi bi-battery',
        'bi bi-battery-half',
        'bi bi-battery-half',
        'bi bi-battery-half',
        'bi bi-battery-full',
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


// metric series rotation globals
// initially set to live
var metric_key = 'live';
var cycle_count = 0;
var about_screen_ts = 0;

// rotates the current metric index as 
// part of the timed cycling
function cycle_metric_index() {
    console.log(`cycle_metric_index(metric_key:${metric_key})`);

    // predetermined cycle order
    metric_list = [
        'live',
        'today',
        'yesterday',
        'this_month',
        'last_month',
        'total',
        'pv_total',
        'about',
    ];

    // no dashboard, can't do anything
    if (!( 'dashboard' in data_dict)) {
        console.log('no dashboard metrics available');
        return;
    }

    // current epoch timestamp
    d = new Date();
    now_ts = Math.round(d.getTime() / 1000);

    // locate current index in list
    metric_index = metric_list.indexOf(metric_key);
    for (i = 0; i < metric_list.length; i++) {
        // about screen display in progress
        // we break out if the interval not yet been reached
        // but we will break out early if it has been disabled
        if (metric_key == "about" &&
            data_dict.dashboard.metrics[next_metric_key] &&
            now_ts - about_screen_ts < data_dict.dashboard.about_screen_display_interval) {
            break;
        }

        // cycle metric
        metric_index = (metric_index + 1) % metric_list.length;
        next_metric_key = metric_list[metric_index];
        console.log(`next_metric_key:${metric_key}`);

        // detect full cycle on return to 
        // first item in list
        if (metric_index == 0) {
            // increment cycle count
            cycle_count++;
        }

        // check for the about screen in the cycle
        // this includs checking in 
        if (next_metric_key == "about") {
            if (data_dict.dashboard.metrics[next_metric_key] &&
                cycle_count >= data_dict.dashboard.about_screen_cycle_interval &&
                (now_ts - about_screen_ts) >= data_dict.dashboard.about_screen_display_interval) {

                // set the metric to the about screen
                // mark the timestamp and we're all set
                // also reset the cycle count for the next time
                cycle_count = 0;
                metric_key = next_metric_key
                about_screen_ts = now_ts
                break;
            }
            else {
                // skip the about screen
                // and continue the cycle
                continue;
            }
        }

        // skip live metric in dual-donut layout
        // as live is fixed on left
        if (layout == "dual-metrics" && 
            next_metric_key == "live") {
            continue;
        }
         
        // skip pv_total metric for any layout
        // other than single-metric
        // just not suite for anything else
        if (layout != "single-metric" && 
            next_metric_key == "pv_total") {
            continue;
        }

        // check if present in the data dict
        // and enabled in the config
        if (next_metric_key in data_dict.dashboard.metrics &&
            data_dict.dashboard.metrics[next_metric_key]) {
            metric_key = next_metric_key
            break;
        }

        // safety net
        // we get here if nothing is found
        // more than likely nothing configured
        // so we fall back on live
        if (i == metric_list.length - 1) {
            metric_key = "live";
            break;
        }
    }

    console.log(`final metric_key:${metric_key}`);
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
    ui_layout_list = ['default', 'dual-metrics', 'single-metric'];
    layout_index = ui_layout_list.indexOf(layout);
    layout_index = (layout_index + 1) % ui_layout_list.length;
    layout = ui_layout_list[layout_index];
    console.log("cycled layout to:" + layout);
    window.location.replace(get_redirect_url("layout", layout));
}


function get_metric_title(metric_key) {
    metrics_source = get_metrics(metric_key);

    metric_title = '';
    switch(metric_key) {
      case 'live':
      hour_str = String(metrics_source['hour']).padStart(2, '0'); 
      min_str = String(metrics_source['minute']).padStart(2, '0'); 
      sec_str = String(metrics_source['second']).padStart(2, '0'); 
      metric_title = `Real-time @${hour_str}:${min_str}:${sec_str}`;
      break;

      case 'today':
      metric_title = `Today (${metrics_source['month']} ${metrics_source['day']} ${metrics_source['year']})`;
      break;

      case 'yesterday':
      metric_title = `Yesterday (${metrics_source['month']} ${metrics_source['day']} ${metrics_source['year']})`;
      break;

      case 'this_month':
      metric_title = `This Month (${metrics_source['month']} ${metrics_source['year']})`;
      break;

      case 'last_month':
      metric_title = `Last Month (${metrics_source['month']} ${metrics_source['year']})`;
      break;

      case 'total':
      metric_title = 'Overall Performance';
      break;

      case 'pv_total':
      metric_title = 'Solar PV Performance';
      break;

    }

    return metric_title;
}


function populate_metrics(metrics_id, metric_key, layout) {
    console.log(`populate_metrics(id:${metrics_id}, key:${metric_key}, layout:${layout})`);
    metrics_source = get_metrics(metric_key);
    if (metrics_source == undefined) {
        console.log(`No metric source available for ${metric_key}`);
        return;
    }

    metric_title = get_metric_title(metric_key);
    $("#" + metrics_id + "_titletext").html(metric_title);

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

    // layout tweaks
    switch(layout) {
      case 'single-metric':
      $("#" + metrics_id + "_title").show();
      $("#" + metrics_id + "_installer_logo").hide();
      $("#" + metrics_id + "_import_caption").show();
      $("#" + metrics_id + "_solar_caption").show();
      $("#" + metrics_id + "_export_caption").show();
      $("#" + metrics_id + "_consumed_caption").show();
      $("#" + metrics_id + "_battery_charge_caption").show();
      $("#" + metrics_id + "_battery_discharge_caption").show();
      $("#" + metrics_id + "_battery_soc_caption").show();
      $("#" + metrics_id + "_co2_caption").show();
      $("#" + metrics_id + "_trees_caption").show();
      break;

      default:
      $("#" + metrics_id + "_title").hide();
      $("#" + metrics_id + "_installer_logo").hide();
      $("#" + metrics_id + "_import_caption").hide();
      $("#" + metrics_id + "_solar_caption").hide();
      $("#" + metrics_id + "_export_caption").hide();
      $("#" + metrics_id + "_consumed_caption").hide();
      $("#" + metrics_id + "_battery_charge_caption").hide();
      $("#" + metrics_id + "_battery_discharge_caption").hide();
      $("#" + metrics_id + "_battery_soc_caption").hide();
      $("#" + metrics_id + "_co2_caption").hide();
      $("#" + metrics_id + "_trees_caption").hide();
      break;
    }

    // Enviromental data hidden by default, but shown 
    // for the total
    switch(metric_key) {
      case 'total':
      $("#" + metrics_id + "_co2_card").show();
      $("#" + metrics_id + "_trees_card").show();
      $("#" + metrics_id + "_export_card").show();
      $("#" + metrics_id + "_import_card").hide();
      $("#" + metrics_id + "_consumed_card").hide();
      $("#" + metrics_id + "_solar_live_card").hide();
      $("#" + metrics_id + "_solar_today_card").hide();
      $("#" + metrics_id + "_installer_logo").hide();
      $("#" + metrics_id + "_installer_card").hide();
      break;

      case 'pv_total':
      $("#" + metrics_id + "_co2_card").show();
      $("#" + metrics_id + "_trees_card").show();
      $("#" + metrics_id + "_solar_live_card").show();
      $("#" + metrics_id + "_solar_today_card").show();
      $("#" + metrics_id + "_import_card").hide();
      $("#" + metrics_id + "_export_card").hide();
      $("#" + metrics_id + "_consumed_card").hide();
      //$("#" + metrics_id + "_installer_logo").show();
      $("#" + metrics_id + "_installer_card").show();
      break;

      default:
      $("#" + metrics_id + "_co2_card").hide();
      $("#" + metrics_id + "_trees_card").hide();
      $("#" + metrics_id + "_export_card").show();
      $("#" + metrics_id + "_solar_live_card").hide();
      $("#" + metrics_id + "_solar_today_card").hide();
      $("#" + metrics_id + "_import_card").show();
      $("#" + metrics_id + "_consumed_card").show();
      $("#" + metrics_id + "_installer_logo").hide();
      $("#" + metrics_id + "_installer_card").hide();
      break;
    }

    value_dict = format_energy_value(metrics_source.import, 
                                     std_energy_unit, 
                                     mega_energy_unit, 
                                     milli_energy_unit);
    $("#" + metrics_id + "_import_caption").html('Grid Power Purchased');
    $("#" + metrics_id + "_import_value").html(value_dict['value']);
    $("#" + metrics_id + "_import_unit").html(value_dict['unit']);

    if (metrics_source.import > 0) {
        $("#" + metrics_id + "_import_value").removeClass().addClass("metric metric-red");
        $("#" + metrics_id + "_import_icon").removeClass().addClass("metric-icon metric-red");
        $("#" + metrics_id + "_import_unit").removeClass().addClass("metric-unit metric-red");
        $("#" + metrics_id + "_import_caption").removeClass().addClass("metric-caption metric-white");
    }
    else {
        $("#" + metrics_id + "_import_value").removeClass().addClass("metric metric-green");
        $("#" + metrics_id + "_import_icon").removeClass().addClass("metric-icon metric-green");
        $("#" + metrics_id + "_import_unit").removeClass().addClass("metric-unit metric-green");
        $("#" + metrics_id + "_import_caption").removeClass().addClass("metric-caption metric-green");
    }

    value_dict = format_energy_value(metrics_source.solar, 
                                     std_energy_unit, 
                                     mega_energy_unit, 
                                     milli_energy_unit);
    if (metric_key == 'pv_total') {
        $("#" + metrics_id + "_solar_caption").html('Total Solar Power Generation');
    }
    else {
        $("#" + metrics_id + "_solar_caption").html('Solar Power Generation');
    }

    $("#" + metrics_id + "_solar_value").html(value_dict['value']);
    $("#" + metrics_id + "_solar_unit").html(value_dict['unit']);

    if (metrics_source.solar > 0) {
        $("#" + metrics_id + "_solar_value").removeClass().addClass("metric metric-yellow");
        $("#" + metrics_id + "_solar_icon").removeClass().addClass("metric-icon metric-yellow");
        $("#" + metrics_id + "_solar_unit").removeClass().addClass("metric-unit metric-yellow");
        $("#" + metrics_id + "_solar_caption").removeClass().addClass("metric-caption metric-white");
    }
    else {
        $("#" + metrics_id + "_solar_value").removeClass().addClass("metric metric-grey");
        $("#" + metrics_id + "_solar_icon").removeClass().addClass("metric-icon metric-grey");
        $("#" + metrics_id + "_solar_unit").removeClass().addClass("metric-unit metric-grey");
        $("#" + metrics_id + "_solar_caption").removeClass().addClass("metric-caption metric-grey");
    }

    if (metric_key == 'pv_total') {

        value_dict = format_energy_value(metrics_source.solar_live, 
                                         'kW', 
                                         'mW', 
                                         'W');
        $("#" + metrics_id + "_solar_live_caption").html('Real-time Solar Power');
        $("#" + metrics_id + "_solar_live_value").html(value_dict['value']);
        $("#" + metrics_id + "_solar_live_unit").html(value_dict['unit']);

        if (metrics_source.solar > 0) {
            $("#" + metrics_id + "_solar_live_value").removeClass().addClass("metric metric-yellow");
            $("#" + metrics_id + "_solar_live_icon").removeClass().addClass("metric-icon metric-yellow");
            $("#" + metrics_id + "_solar_live_unit").removeClass().addClass("metric-unit metric-yellow");
            $("#" + metrics_id + "_solar_live_caption").removeClass().addClass("metric-caption metric-white");
        }
        else {
            $("#" + metrics_id + "_solar_live_value").removeClass().addClass("metric metric-grey");
            $("#" + metrics_id + "_solar_live_icon").removeClass().addClass("metric-icon metric-grey");
            $("#" + metrics_id + "_solar_live_unit").removeClass().addClass("metric-unit metric-grey");
            $("#" + metrics_id + "_solar_live_caption").removeClass().addClass("metric-caption metric-grey");
        }

        value_dict = format_energy_value(metrics_source.solar_today, 
                                         std_energy_unit, 
                                         mega_energy_unit, 
                                         milli_energy_unit);
        $("#" + metrics_id + "_solar_today_caption").html('Solar Power Generation Today');
        $("#" + metrics_id + "_solar_today_value").html(value_dict['value']);
        $("#" + metrics_id + "_solar_today_unit").html(value_dict['unit']);

        if (metrics_source.solar > 0) {
            $("#" + metrics_id + "_solar_today_value").removeClass().addClass("metric metric-yellow");
            $("#" + metrics_id + "_solar_today_icon").removeClass().addClass("metric-icon metric-yellow");
            $("#" + metrics_id + "_solar_today_unit").removeClass().addClass("metric-unit metric-yellow");
            $("#" + metrics_id + "_solar_today_caption").removeClass().addClass("metric-caption metric-white");
        }
        else {
            $("#" + metrics_id + "_solar_today_value").removeClass().addClass("metric metric-grey");
            $("#" + metrics_id + "_solar_today_icon").removeClass().addClass("metric-icon metric-grey");
            $("#" + metrics_id + "_solar_today_unit").removeClass().addClass("metric-unit metric-grey");
            $("#" + metrics_id + "_solar_today_caption").removeClass().addClass("metric-caption metric-grey");
        }
    }

    value_dict = format_energy_value(metrics_source.export, 
                                     std_energy_unit, 
                                     mega_energy_unit, 
                                     milli_energy_unit);
    $("#" + metrics_id + "_export_caption").html('Surplus Power Exported');
    $("#" + metrics_id + "_export_value").html(value_dict['value']);
    $("#" + metrics_id + "_export_unit").html(value_dict['unit']);

    if (metrics_source.export > 0) {
        $("#" + metrics_id + "_export_value").removeClass().addClass("metric metric-blue");
        $("#" + metrics_id + "_export_icon").removeClass().addClass("metric-icon metric-blue");
        $("#" + metrics_id + "_export_unit").removeClass().addClass("metric-unit metric-blue");
        $("#" + metrics_id + "_export_caption").removeClass().addClass("metric-caption metric-white");
    }
    else {
        $("#" + metrics_id + "_export_value").removeClass().addClass("metric metric-grey");
        $("#" + metrics_id + "_export_icon").removeClass().addClass("metric-icon metric-grey");
        $("#" + metrics_id + "_export_unit").removeClass().addClass("metric-unit metric-grey");
        $("#" + metrics_id + "_export_caption").removeClass().addClass("metric-caption metric-grey");
    }

    value_dict = format_energy_value(metrics_source.consumed, 
                                     std_energy_unit, 
                                     mega_energy_unit, 
                                     milli_energy_unit);
    $("#" + metrics_id + "_consumed_caption").html('Consumed Power');
    $("#" + metrics_id + "_consumed_value").html(value_dict['value']);
    $("#" + metrics_id + "_consumed_unit").html(value_dict['unit']);

    if (metrics_source.import <= 0) {
        $("#" + metrics_id + "_consumed_value").removeClass().addClass("metric metric-green");
        $("#" + metrics_id + "_consumed_icon").removeClass().addClass("metric-icon metric-green");
        $("#" + metrics_id + "_consumed_unit").removeClass().addClass("metric-unit metric-green");
        $("#" + metrics_id + "_consumed_caption").removeClass().addClass("metric-caption metric-white");
    }
    else if (metrics_source.solar > 0) {
        $("#" + metrics_id + "_consumed_value").removeClass().addClass("metric metric-orange");
        $("#" + metrics_id + "_consumed_icon").removeClass().addClass("metric-icon metric-orange");
        $("#" + metrics_id + "_consumed_unit").removeClass().addClass("metric-unit metric-orange");
        $("#" + metrics_id + "_consumed_caption").removeClass().addClass("metric-caption metric-white");
    }
    else {
        $("#" + metrics_id + "_consumed_value").removeClass().addClass("metric metric-red");
        $("#" + metrics_id + "_consumed_icon").removeClass().addClass("metric-icon metric-red");
        $("#" + metrics_id + "_consumed_unit").removeClass().addClass("metric-unit metric-red");
        $("#" + metrics_id + "_consumed_caption").removeClass().addClass("metric-caption metric-white");
    }

    if ('battery_charge' in metrics_source) {
        $("#" + metrics_id + "_battery_charge_card").show();
        value_dict = format_energy_value(metrics_source.battery_charge, 
                                         std_energy_unit, 
                                         mega_energy_unit, 
                                         milli_energy_unit);
        $("#" + metrics_id + "_battery_charge_caption").html('Battery Charge');
        $("#" + metrics_id + "_battery_charge_value").html(value_dict['value']);
        $("#" + metrics_id + "_battery_charge_unit").html(value_dict['unit']);

        if (metrics_source.battery_charge > 0) {
            $("#" + metrics_id + "_battery_charge_value").removeClass().addClass("metric metric-charge");
            $("#" + metrics_id + "_battery_charge_icon").removeClass().addClass("metric-icon metric-charge");
            $("#" + metrics_id + "_battery_charge_unit").removeClass().addClass("metric-unit metric-charge");
        }
        else {
            $("#" + metrics_id + "_battery_charge_value").removeClass().addClass("metric metric-grey");
            $("#" + metrics_id + "_battery_charge_icon").removeClass().addClass("metric-icon metric-grey");
            $("#" + metrics_id + "_battery_charge_unit").removeClass().addClass("metric-unit metric-grey");
        }
    }
    else {
        $("#" + metrics_id + "_battery_charge_card").hide();
    }

    if ('battery_discharge' in metrics_source) {
        $("#" + metrics_id + "_battery_discharge_card").show();
        value_dict = format_energy_value(metrics_source.battery_discharge, 
                                         std_energy_unit, 
                                         mega_energy_unit, 
                                         milli_energy_unit);
        $("#" + metrics_id + "_battery_discharge_caption").html('Battery Discharge');
        $("#" + metrics_id + "_battery_discharge_value").html(value_dict['value']);
        $("#" + metrics_id + "_battery_discharge_unit").html(value_dict['unit']);

        if (metrics_source.battery_discharge > 0) {
            $("#" + metrics_id + "_battery_discharge_value").removeClass().addClass("metric metric-discharge");
            $("#" + metrics_id + "_battery_discharge_icon").removeClass().addClass("metric-icon metric-discharge");
            $("#" + metrics_id + "_battery_discharge_unit").removeClass().addClass("metric-unit metric-discharge");
        }
        else {
            $("#" + metrics_id + "_battery_discharge_value").removeClass().addClass("metric metric-grey");
            $("#" + metrics_id + "_battery_discharge_icon").removeClass().addClass("metric-icon metric-grey");
            $("#" + metrics_id + "_battery_discharge_unit").removeClass().addClass("metric-unit metric-grey");
        }
    }
    else {
        $("#" + metrics_id + "_battery_discharge_card").hide();
    }

    if ('battery_soc' in metrics_source) {
        $("#" + metrics_id + "_battery_soc_card").show();
        battery_soc_class = format_battery_class(metrics_source.battery_soc);
        console.log("battery_soc_class:" + battery_soc_class);
        $("#" + metrics_id + "_battery_soc_caption").html('Battery State Of Charge');
        $("#" + metrics_id + "_battery_soc_value").html(metrics_source.battery_soc);
        $("#" + metrics_id + "_battery_soc_unit").html('%');
        $("#" + metrics_id + "_battery_soc_state").removeClass().addClass(battery_soc_class);

        if (metrics_source.battery_soc >= 50) {
            $("#" + metrics_id + "_battery_soc_value").removeClass().addClass("metric metric-green");
            $("#" + metrics_id + "_battery_soc_icon").removeClass().addClass("metric-icon metric-green");
            $("#" + metrics_id + "_battery_soc_unit").removeClass().addClass("metric-unit metric-green");
        }
        else if (metrics_source.battery_soc >= 30) {
            $("#" + metrics_id + "_battery_soc_value").removeClass().addClass("metric metric-orange");
            $("#" + metrics_id + "_battery_soc_icon").removeClass().addClass("metric-icon metric-orange");
            $("#" + metrics_id + "_battery_soc_unit").removeClass().addClass("metric-unit metric-orange");
        }
        else {
            $("#" + metrics_id + "_battery_soc_value").removeClass().addClass("metric metric-red");
            $("#" + metrics_id + "_battery_soc_icon").removeClass().addClass("metric-icon metric-red");
            $("#" + metrics_id + "_battery_soc_unit").removeClass().addClass("metric-unit metric-red");
        }
    }
    else {
        $("#" + metrics_id + "_battery_soc_card").hide();
    }

    value_dict = format_energy_value(metrics_source.co2, 'kg', 'mt', 'g');
    $("#" + metrics_id + "_co2_caption").html('Reduced CO<sub>2</sub> Emissions');
    $("#" + metrics_id + "_co2_value").html(value_dict['value']);
    $("#" + metrics_id + "_co2_unit").html(value_dict['unit']);

    if (metrics_source.co2 > 0) {
        $("#" + metrics_id + "_co2_value").removeClass().addClass("metric metric-green");
        $("#" + metrics_id + "_co2_icon").removeClass().addClass("metric-icon metric-green");
        $("#" + metrics_id + "_co2_unit").removeClass().addClass("metric-unit metric-green");
        $("#" + metrics_id + "_co2_caption").removeClass().addClass("metric-caption metric-white");
    }
    else {
        $("#" + metrics_id + "_co2_value").removeClass().addClass("metric metric-grey");
        $("#" + metrics_id + "_co2_icon").removeClass().addClass("metric-icon metric-grey");
        $("#" + metrics_id + "_co2_unit").removeClass().addClass("metric-unit metric-grey");
        $("#" + metrics_id + "_co2_caption").removeClass().addClass("metric-caption metric-grey");
    }

    value_dict = format_trees(metrics_source.trees);
    $("#" + metrics_id + "_trees_caption").html('Equivalent Trees Planted');
    $("#" + metrics_id + "_trees_value").html(value_dict['value']);

    if (metrics_source.trees > 0) {
        $("#" + metrics_id + "_trees_value").removeClass().addClass("metric metric-green");
        $("#" + metrics_id + "_trees_icon").removeClass().addClass("metric-icon metric-green");
        $("#" + metrics_id + "_trees_unit").removeClass().addClass("metric-unit metric-green");
        $("#" + metrics_id + "_trees_caption").removeClass().addClass("metric-caption metric-white");
    }
    else {
        $("#" + metrics_id + "_trees_value").removeClass().addClass("metric metric-grey");
        $("#" + metrics_id + "_trees_icon").removeClass().addClass("metric-icon metric-grey");
        $("#" + metrics_id + "_trees_unit").removeClass().addClass("metric-unit metric-grey");
        $("#" + metrics_id + "_trees_caption").removeClass().addClass("metric-caption metric-grey");
    }

}

function get_metrics(metric_key) {
    // select metric source
    switch(metric_key) {
      case 'live':
      metric_source = data_dict["live"];
      break;

      case 'today':
      metric_source = data_dict.month[data_dict.month.length - 1];
      break;

      case 'yesterday':
      metric_source = data_dict.month[data_dict.month.length - 2];
      break;

      case 'this_month':
      metric_source = data_dict.year[data_dict.year.length - 1];
      break;

      case 'last_month':
      metric_source = data_dict.year[data_dict.year.length - 2];
      break;

      case 'total':
      metric_source = data_dict["total"];
      break;

      case 'pv_total':
      metric_source = data_dict["total"];
      metric_today = data_dict.month[data_dict.month.length - 1];
      metric_source.solar_today = metric_today.solar;
      metric_source.solar_live = data_dict.live.solar;
      break;

      default:
      metric_source = undefined;
      break;
    }

    return metric_source;
}

// global for metrics layout rotation
// 0 or 1
var metrics_layout_id = 0;

// renders and displays the current dashboard
function display_data() {
    console.log("display_data()");

    // switch from splash to dashboard 
    // only when we have data to show
    // this is a once-off occurrence at the start
    if ('last_updated' in data_dict && 
        data_dict.last_updated > 0) {
        $("#splash").hide();
        $("#about").hide();
    }
    else {
        $("#splash").show();
        $("#about").hide();
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

    if (metric_key == 'about') {
        $("#splash").hide();
        $("#dashboard").hide();
        $("#about").show();
        reformatted_text = data_dict['dashboard']['about_caption'].replaceAll('\n', '<br>');
        $("#about_caption").html(reformatted_text);

        return;
    }

    // populate metrics
    switch(layout) {
      case "dual-metrics":
      // dual-donut + dual metrics layout
      populate_metrics("metrics_a", "live", layout);
      populate_metrics("metrics_b", metric_key, layout);
      $("#donut_a_title").html(get_metric_title("live"));
      $("#donut_b_title").html(get_metric_title(metric_key));
      break;

      case "single-metric":
      // single metric layout
      populate_metrics("single_metric", metric_key, layout);

      default:
      // typical layout of using a single donut and one set of metrics
      populate_metrics("metrics_a", metric_key, layout);
      $("#donut_a_title").html(get_metric_title(metric_key));
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

    metrics_source = get_metrics(metric_key);
    if (metrics_source == undefined) {
        console.log(`No metric source available for ${metric_key}`);
        return;
    }

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
        series_value = metrics_source[series_field];
        if (series_value == undefined) {
            series_value = 0;
        }
        series_label = series_labels[series_field];
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

function render_column_chart(column_chart,
                             chart_id,
                             data_key,
                             chart_options,
                             series_labels,
                             time_unit,
                             chart_series_list) {

    console.log(`rendering column chart ${chart_id} with ${data_key} data`);

    // fre up memory due to leak risk
    if (column_chart != undefined) {
        column_chart.clearChart();
        first_run = false;
    }
    else {
        // will be used later on to draw the 
        // chart twice due to an initial rendering issue
        first_run = true;
    }

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

        // time string
        // not ideal as we have to code variation formatting here
        // for the time field labels
        switch(data_key) {
          case 'day':
          // HH (24hr zero padded)
          time_str = item.hour.toString().padStart(2, '0');
          break;

          case 'month':
          // MMM DD
          time_str = item.month + ' ' + item.day.toString().padStart(2, '0');
          break;

          case 'year':
          // MMM
          time_str = item.month;
          break;

        }

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

    // render the chart
    column_chart.draw(chart_data, chart_options);
    if (first_run) {
        // second draw to fix the width
        column_chart.draw(chart_data, chart_options);
        console.log("second column chart draw for " + chart_id);
    }

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

    // chart height and style variations by layout
    switch(layout) {
      case "single-metric":
      return;
      break;

      case "portrait":
      donut_chart_height = (window.innerHeight) * 0.4;
      legend_font_size_var = "--legend-font-size-portrait";
      slice_font_size_var = "--slice-font-size-portrait";
      break;

      case "dual-metrics":
      donut_chart_height = (window.innerHeight) * 0.40;
      legend_font_size_var = "--legend-font-size-dual";
      slice_font_size_var = "--slice-font-size-dual";
      break;

      case "default":
      donut_chart_height = (window.innerHeight) * 0.40;
      legend_font_size_var = "--legend-font-size-default";
      slice_font_size_var = "--slice-font-size-default";
      break;
    }

    // legend font size.. this is a bit of work
    // we parsed layout and determined the CSS ref variable to 
    // use for legend font. Google does not allow us pass that CSS
    // in for the font size. So it needs to rendered in pixels

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
                                 donut_metric_key, 
                                 donut_options, 
                                 series_labels,
                                 donut_series_list);

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

        // construct column_chart series and colour lists
        column_chart_series_list = []
        column_chart_colour_list = []

        for (series_field of series_fields) {
            if (data_dict.dashboard.bar_chart[series_field]) {
                column_chart_series_list.push(series_field)
                column_chart_colour_list.push(series_colours[series_field])
            }
        }

        // common options
        // but the hAxis title will be tweaked
        var column_chart_options = {
            colors: column_chart_colour_list,
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

            day_chart = render_column_chart(day_chart,
                                            "day_google_chart",
                                            'day',
                                            column_chart_options,
                                            series_labels,
                                            'Hour',
                                            column_chart_series_list);

            chart_title = `Last ${data_dict.day.length} Hours`;
            $("#day_chart_title").html(chart_title);
        }

        // remove the legent for the month and year charts 
        column_chart_options.legend = 'none';
        column_chart_options.chartArea.top = 10;

        // month 
        if (data_dict.month.length > 0 && 
            month_chart_ts != data_dict.month_last_updated) {
            month_chart_ts = data_dict.month_last_updated;

            month_chart = render_column_chart(month_chart,
                                              "month_google_chart",
                                              'month',
                                              column_chart_options,
                                              series_labels,
                                              'Day',
                                              column_chart_series_list);

            chart_title = `Last ${data_dict.month.length} Days`;
            $("#month_chart_title").html(chart_title);
        }

        // year
        if (data_dict.year.length > 0 && 
            year_chart_ts != data_dict.year_last_updated) {
            year_chart_ts = data_dict.year_last_updated;

            year_chart = render_column_chart(year_chart,
                                             "year_google_chart",
                                             'year',
                                             column_chart_options,
                                             series_labels,
                                             'Month',
                                             column_chart_series_list);

            chart_title = `Last ${data_dict.year.length} Months`;
            $("#year_chart_title").html(chart_title);
        }
    }
}
