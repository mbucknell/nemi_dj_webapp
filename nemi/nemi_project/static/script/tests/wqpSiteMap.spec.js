describe('Tests for WQP.siteLayer', function() {
	var server;
	
	var layerData = '{' + 
    '"type": "FeatureCollection",' + 
    '"features": [' +
        '{' +
            '"type": "Feature",' +
            '"geometry": {'+
                '"type": "Point",' + 
                '"coordinates": [' + 
                    '-93.9391185,' + 
                    '42.0327602' + 
                ']' + 
            '},' + 
            '"properties": {' + 
               '"ProviderName": "NWIS",' + 
        				'"MonitoringLocationIdentifier": "USGS-420158093562001",' + 
        				'"ResolvedMonitoringLocationTypeName":"Well"' + 
            '}' + 
        '},' + 
        '{' + 
            '"type": "Feature",' + 
            '"geometry": {' + 
                '"type": "Point",' + 
                '"coordinates": [' + 
                    '-93.698220503,' + 
                    '41.9607224179' + 
                ']' + 
            '},' + 
            '"properties": {' + 
                 '"ProviderName": "STEWARDS",' + 
                 '"MonitoringLocationIdentifier": "ARS-IAWC-IAWC225",' + 
                 '"ResolvedMonitoringLocationTypeName": "Land"' + 
            '}' + 
        '}]}';
	
	beforeEach(function() {
		spyOn(L, 'geoJson').andCallThrough();
		server = sinon.fakeServer.create();
	});
	
	afterEach(function() {
		server.restore();
	});
	
	it('Expects WQP.siteLayer to return a geoJson layer with default options', function() {
		var siteLayer = WQP_MAP.siteLayer();
		expect(siteLayer instanceof L.GeoJSON).toBeTruthy();

		expect(L.geoJson.calls[0].args[1].onEachFeature).toBeDefined();
		
		expect(server.requests.length).toBe(1);
		expect(server.requests[0].url).toEqual('http://www.waterqualitydata.us/SimpleStation/search');
		
		var siteLayer2 = WQP_MAP.siteLayer({
			serviceURL : null,
			data : null,
			layerOptions : null,
			errorHandler : null
		});
		expect(server.requests[1].url).toEqual('http://www.waterqualitydata.us/SimpleStation/search');
	});
	
	it('Expects the default onEachFeature function to bind a popup to the layer with html that reflects the features properties', function() {
		var siteLayer = WQP_MAP.siteLayer();
		var onEachFeature = L.geoJson.calls[0].args[1].onEachFeature;
		
		var testLayer = jasmine.createSpyObj('testLayer', ['bindPopup']);
		var feature = {
				type : 'Feature',
				geometry : {
					type : 'Point',
					coordinates : ['-93.698220503', '41.9607224179']
				},
				properties : {
					ProviderName : 'STEWARDS',
					MonitoringLocationIdentifier : 'ARS-IAWC-IAWC225',
					ResolvedMonitoringLocationTypeName : 'Land'
				}
		};
		onEachFeature(feature, testLayer);
		expect(testLayer.bindPopup).toHaveBeenCalled();
		var resultHtml = testLayer.bindPopup.calls[0].args[0];
		expect(resultHtml).toMatch('STEWARDS');
		expect(resultHtml).toMatch('ARS-IAWC-IAWC225');
		expect(resultHtml).toMatch('Land');
	});
	
	it('Expects a successful service call to add the data to the layer', function() {
		var siteLayer = WQP_MAP.siteLayer();
		spyOn(siteLayer, 'addData');
		server.requests[0].respond(200, {"Content-Type" : "application/json"}, layerData);
		expect(siteLayer.addData).toHaveBeenCalled();		
	});
	
	it('Expects an unsuccessful service call to not call addData', function() {
		var siteLayer = WQP_MAP.siteLayer();
		spyOn(siteLayer, 'addData');
		server.requests[0].respond(500, 'Bad data');
		expect(siteLayer.addData).not.toHaveBeenCalled();
	});
	
	it('Expects serviceURL property to override the default', function() {
		var siteLayer = WQP_MAP.siteLayer({serviceURL : 'http://www.fakewaterdataservice.com'});
		expect(server.requests[0].url).toEqual('http://www.fakewaterdataservice.com');
	});
	
	it('Expects data property to be used to form the query parameters', function() {
		var siteLayer = WQP_MAP.siteLayer({data : {param1 : 'value1'}});
		expect(server.requests[0].url).toContain('?param1=value1');
	});
	
	it('Expects layerOptions property to be used to extend default options when creating the layer', function() {
		var siteLayer = WQP_MAP.siteLayer({layerOptions : {style : {color : 'blue'}}});
		var options = L.geoJson.calls[0].args[1];
		expect(options.style).toEqual({color : 'blue'});
	});
	
	it('Expects the specified errorHandler to be called on an error', function() {
		var errorSpy = jasmine.createSpy('errorSpy');
		var siteLayer = WQP_MAP.siteLayer({errorHandler : errorSpy});
		server.requests[0].respond(500, 'Bad data');
		expect(errorSpy).toHaveBeenCalled();		
	});
});

describe('Tests for WQP_MAP.siteMap', function() {
	beforeEach(function() {
		spyOn(WQP_MAP, 'siteLayer').andCallThrough();
		spyOn(jQuery, 'ajax');
		$('body').append('<div id="test-map-div"></div>');
	});
	
	afterEach(function() {
		$('#test-map-div').remove();
	});
	
	it('Expects the function to return an object containing a map and siteLayer properties', function() {
		var siteMap = WQP_MAP.siteMap({
			mapDivId : 'test-map-div'
		});
		expect(siteMap.map).toBeDefined();
		expect(siteMap.map instanceof L.Map).toBeTruthy();
		expect(siteMap.siteLayer).toBeDefined();
		expect(WQP_MAP.siteLayer).toHaveBeenCalledWith({
			serviceURL : null,
			data : null,
			layerOptions : null
		});	
		expect(siteMap.map.hasLayer(siteMap.siteLayer)).toBeTruthy();
	});
	
	it('Expects map defaults to be overriden when mapOptions are specified function call', function() {
		var bLayer = L.marker([45.0, -103.0]);
		spyOn(L, 'map').andCallThrough();
		var siteMap = WQP_MAP.siteMap({
			mapDivId : 'test-map-div',
			mapOptions : {
				center : [45.0, -103.0],
				zoom : 6,
				attributionControl : true,
				layers : [bLayer],
				zoomControl : false
			}			
		});
		
		expect(siteMap.map.getCenter()).toEqual(L.latLng(45.0, -103.0));
		expect(siteMap.map.getZoom()).toEqual(6);
		expect(L.map.calls[0].args[1].attributionControl).toBe(true);
		expect(L.map.calls[0].args[1].zoomControl).toBe(false);
		expect(siteMap.map.hasLayer(bLayer)).toBeTruthy();		
	});
	
	it('Expects siteLayer creation options to be passed through to siteLayer ', function() {
		var siteMap = WQP_MAP.siteMap({
			mapDivId : 'test-map-div',
			serviceURL : 'http://www.test.com/Station/search',
			data : {
				param1 : 'value1'
			},
			layerOptions : {style : {color : 'blue'}}
		});
		
		var siteLayerArgs = WQP_MAP.siteLayer.calls[0].args[0];
		expect(siteLayerArgs.serviceURL).toEqual('http://www.test.com/Station/search');
		expect(siteLayerArgs.data).toEqual({param1 : 'value1'});
		expect(siteLayerArgs.layerOptions).toEqual({style : {color : 'blue'}});
	});	
});