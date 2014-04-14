// Dependent on Leaflet and jquery.

var WQP_MAP = WQP_MAP || {};

WQP_MAP.siteLayer = function(spec) {
	// spec (Object -optional) with the following properties:
	//     serviceURL : (optional)The url to call to get the geoJSON file. Defaults to www.waterqualitydata.us.
	//	   data : (optional)Object or String. Used to retrieve the geoJSON site data from WQP. If a string it is a query string.	
	//     layerOptions : (optional) see Leaflet geojson docs. Default options will be used if not defined.
	//	   errorHandler : (optional) function(jgXHR, textStatus, errorThrown)
	
	var idHtml = function (props) {
		var result = '<table>' +
			'<tr><th>Site:</th><td>' + props.MonitoringLocationIdentifier + '</td></tr>' +
			'<tr><th>Site type:</th><td>' + props.ResolvedMonitoringLocationTypeName + '</td></tr>/' +
			'<tr><th>Data source:</th><td>' + props.ProviderName + '</td></tr></table>';
		return result;
	};
	
	DEFAULT_OPTIONS = {
			onEachFeature : function(feature, layer){
				layer.bindPopup(idHtml(feature.properties));
			}
	};
	
	spec = spec || {};
	var that = L.geoJson([], $.extend({}, DEFAULT_OPTIONS, spec.layerOptions || {}));
	
	$.ajax({
		url : spec.serviceURL || 'http://www.waterqualitydata.us/SimpleStation/search',
		type : 'GET',
		data : spec.data || {},
		success : function(data, textStatus, jqXHR) {
			that.addData(data.features);
		},
		error : spec.errorHandler || function() {return;}
	});
	
	return that;
};

WQP_MAP.siteMap = function(spec) {
	// spec object can should have the following properties
	//      mapDivId : The id of the div which will contain the site map
	//      serviceURL : (optional)The url to call to get the geoJSON file. Defaults to www.waterqualitydata.us.
	//		data : (optional)Object or String. Used to retrieve the geoJSON site data from WQP. If a string it is a query string. 
	//		mapOptions : (optional) Object containing Leaflet map options. These will override any defaults.
	//      layerOptions : (optional) see Leaflet geojson docs. Default options will be used if not defined.
	// Returns an object containing the map created and the geojson layer. The layer has already been added to the map.
	
	var that = {};
	spec.mapOptions = spec.mapOptions || {};
	
	var DEFAULT_MAP_OPTIONS = {
			center : [49.2, -90.5],
			zoom : 3,
			attributionControl : false,
			layers : [L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.png')]
	};
	
	that.map = L.map(spec.mapDivId, $.extend({}, DEFAULT_MAP_OPTIONS, spec.mapOptions));
	that.siteLayer = WQP_MAP.siteLayer({
		serviceURL : spec.serviceURL || null,
		data : spec.data || null,
		layerOptions : spec.layerOptions || null
	});
	that.map.addLayer(that.siteLayer);
		
	return that;	
}