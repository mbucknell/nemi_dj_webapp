describe('Tests for WQP.wqpSitesLayer', function() {
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
		server = sinon.fakeServer.create();
	});
	
	afterEach(function() {
		server.restore();
	});
	
	it('Expects WQP_MAP.wqpSitesLayer to be created with the default options', function() {
		var siteLayer = WQP_MAP.wqpSitesLayer();
		
		expect(siteLayer instanceof L.GeoJSON).toBeTruthy();
		expect(siteLayer.options.serviceURL).toBeDefined();
		expect(siteLayer.options.data).toEqual({});
		expect(siteLayer.options.successHandler).toBeDefined();
		expect(siteLayer.options.errorHandler).toBeDefined();
		expect(siteLayer.options.popupHtmlFromProperty).toBeDefined();
		expect(siteLayer.options.onEachFeature).toBeDefined();
	});
	
	it('Expects WQP_Map.wqpSitesLayer to merge specified options rather than using defaults', function() {
		var successHandlerSpy = jasmine.createSpy('successHandlerSpy');
		var errorHandlerSpy = jasmine.createSpy('errorHandler');
		var popupHtmlFromPropertySpy = jasmine.createSpy('popupHtmlFromProperty');
		var onEachFeatureSpy = jasmine.createSpy('onEachFeature');
		var siteLayer = WQP_MAP.wqpSitesLayer({
			serviceURL : 'http://www.test.com/simplestation',
			data : {param1 : 'value2'},
			successHandler : successHandlerSpy,
			errorHandler : errorHandlerSpy,
			popupHtmlFromProperty : popupHtmlFromPropertySpy,
			onEachFeature : onEachFeatureSpy
		});
		
		expect(siteLayer.options.serviceURL).toEqual('http://www.test.com/simplestation');
		expect(siteLayer.options.data).toEqual({param1 : 'value2'});
		expect(siteLayer.options.successHandler).toBe(successHandlerSpy);
		expect(siteLayer.options.errorHandler).toBe(errorHandlerSpy);
		expect(siteLayer.options.popupHtmlFromProperty).toBe(popupHtmlFromPropertySpy);
		expect(siteLayer.options.onEachFeature).toBe(onEachFeatureSpy);
	});
	
	it('Expects that if onEachFeature is not specified that it will use popupHtmlFromProperty to bind to the popup', function() {
		var popupHtmlFromPropertySpy = jasmine.createSpy('popupHtmlFromPropertySpy').andReturn('test');
		var siteLayer = WQP_MAP.wqpSitesLayer({
			popupHtmlFromProperty : popupHtmlFromPropertySpy
		});
		var layer = jasmine.createSpyObj('layer', ['bindPopup']);
		siteLayer.options.onEachFeature({properties : 'a property'}, layer);
		
		expect(popupHtmlFromPropertySpy).toHaveBeenCalled();
		expect(layer.bindPopup).toHaveBeenCalledWith('test');
	});
	
	it('Expects creating a wqpSitesLayer triggers an ajax call to the serviceURL', function() {
		var siteLayer = WQP_MAP.wqpSitesLayer({
			serviceURL : 'http://test.com/simplestations',
			data : {param1 : 'value1'}
		});
		
		expect(server.requests.length).toBe(1);
		expect(server.requests[0].url).toMatch('http://test.com/simplestations');
		expect(server.requests[0].url).toMatch('param1=value1');
	});
	
	it('Expects mimeType equal to json to be appended to query params', function() {
		var siteLayer = WQP_MAP.wqpSitesLayer();
		expect(server.requests[0].url).toMatch('mimeType=json');
		
		siteLayer = WQP_MAP.wqpSitesLayer({
			data : 'param1=value1'
		});
		expect(server.requests[1].url).toMatch('param1=value1&mimeType=json');
		
		siteLayer = WQP_MAP.wqpSitesLayer({
			data : {
				param1 : 'value1'
			}
		});
		expect(server.requests[2].url).toMatch('param1=value1&mimeType=json');
	});
	
	it('Expects a successful service call to add the data to the layer and to call the successHandler', function() {
		var successHandlerSpy = jasmine.createSpy('successHandlerSpy');
		var siteLayer = WQP_MAP.wqpSitesLayer({
			successHandler : successHandlerSpy
		});
		spyOn(siteLayer, 'addData');
		server.requests[0].respond(200, {"Content-Type" : "application/json"}, layerData);
		expect(siteLayer.addData).toHaveBeenCalled();
		expect(successHandlerSpy).toHaveBeenCalled();
	});
	
	it('Expects an unsuccessful service call to not call addData and to call the errorHandler', function() {
		var errorSpy = jasmine.createSpy('errorSpy');
		var siteLayer = WQP_MAP.wqpSitesLayer({
			errorHandler : errorSpy
		});
		spyOn(siteLayer, 'addData');
		server.requests[0].respond(500, 'Bad data');
		expect(siteLayer.addData).not.toHaveBeenCalled();
		expect(errorSpy).toHaveBeenCalled();		
	});
});

describe('Tests for WQP_MAP.siteMap', function() {
	beforeEach(function() {
		$('body').append('<div id="test-map-div"></div>');
	});
	
	afterEach(function() {
		$('#test-map-div').remove();
	});
	
	it('Expects the function to return an map with defaults defined', function() {
		var siteMap = WQP_MAP.siteMap('test-map-div')

		expect(siteMap instanceof L.Map).toBeTruthy();
		expect(siteMap.options.center).toBeDefined();
		expect(siteMap.options.zoom).toBeDefined();
		expect(siteMap.options.attributionControl).toBeDefined();
		expect(siteMap.options.layers).toBeDefined();
	});
	
	it('Expects map defaults to be overriden when mapOptions are specified function call', function() {
		var bLayer = L.marker([45.0, -103.0]);
		spyOn(L, 'map').andCallThrough();
		var siteMap = WQP_MAP.siteMap('test-map-div', {
			center : [45.0, -103.0],
			zoom : 6,
			attributionControl : true,
			layers : [bLayer],
			zoomControl : false
		});
		
		expect(siteMap.getCenter()).toEqual(L.latLng(45.0, -103.0));
		expect(siteMap.getZoom()).toEqual(6);
		expect(siteMap.options.attributionControl).toBe(true);
		expect(siteMap.options.zoomControl).toBe(false);
		expect(siteMap.hasLayer(bLayer)).toBeTruthy();		
	});
});