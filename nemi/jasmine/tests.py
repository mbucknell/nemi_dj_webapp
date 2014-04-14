from djangojs.runners import JsTestCase, JasmineSuite

class JasmineTests(JasmineSuite, JsTestCase):
    
    urls = 'jasmine.test_urls'
    
    url_name = 'project_jasmine_js_tests'
    
    title = 'WDNR Fish Mapper Jasmine test suite'