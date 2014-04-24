// Dependent on Leaflet and jquery.

var WQP_MAP = WQP_MAP || {};

/*
 * New options defined are: serviceURL : String containing the url to be used to
 * fetch the site geoJSON data data : String or Object containg the query
 * parameter to be used in the ajax call. Does not need to include the mimeType
 * as it is assumed to be json. popupHtmlFromProperty : function(props(Object))
 * returns html string to be used for the identify popup successHandler :
 * function to execute if the ajax loading call succeeds. Defaults to null
 * function. errorHandler : function to execute if the ajax loading call fails.
 * Defauls to null function. Other options that are defaulted onEachFeature :
 * function(feature, layer). By default this binds a popup to each feature. Can
 * be overriden.
 */
WQP_MAP.WQPSitesLayer = L.GeoJSON
        .extend({
            options : {
                serviceURL : 'http://www.waterqualitydata.us/simplestation/search',
                data : {},
                errorHandler : function(data, textStatus, jqXHR) {
                    return;
                },
                successHandler : function(jqXHR, textStatus, error) {
                    return;
                },
                popupHtmlFromProperty : function(props) {
                    var result = '<table>' + '<tr><th>Site:</th><td>'
                            + props.MonitoringLocationIdentifier + '</td></tr>'
                            + '<tr><th>Site type:</th><td>'
                            + props.ResolvedMonitoringLocationTypeName
                            + '</td></tr>/' + '<tr><th>Data source:</th><td>'
                            + props.ProviderName + '</td></tr></table>';
                    return result;
                }
            },
            initialize : function(options) {
                var queryParams;

                options = options || {};
                if (!(options.onEachFeature)) {
                    options.onEachFeature = function(feature, layer) {
                        layer.bindPopup(this
                                .popupHtmlFromProperty(feature.properties));
                    };
                }
                L.GeoJSON.prototype.initialize.call(this, [], options);

                if (typeof (this.options.data) === 'string') {
                    queryParams = this.options.data;
                } else {
                    queryParams = $.param(this.options.data);
                }
                if (queryParams) {
                    queryParams += '&';
                }
                queryParams += 'mimeType=json';

                $.ajax({
                    url : this.options.serviceURL,
                    type : 'GET',
                    data : queryParams,
                    context : this,
                    success : function(data, textStatus, jqXHR) {
                        this.addData(data.features);
                        this.options.successHandler(data, textStatus, jqXHR);
                    },
                    error : this.options.errorHandler
                });
            }
        });

WQP_MAP.wqpSitesLayer = function(options) {
    return new WQP_MAP.WQPSitesLayer(options);
};

// Creates the default map to be used for mapping the sites.
WQP_MAP.SiteMap = L.Map
        .extend({
            options : {
                center : [ 49.2, -90.5 ],
                zoom : 3,
                attributionControl : false,
                layers : [ L
                        .tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.png') ]
            }
        });

WQP_MAP.siteMap = function(mapDivId, options) {
    return new WQP_MAP.SiteMap(mapDivId, options);
};