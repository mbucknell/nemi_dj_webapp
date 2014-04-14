from django.conf.urls import patterns, url

from djangojs.views import JasmineView

class ProjectJasmineView(JasmineView):
    
    template_name = 'jasmine_test_runner.html'
    js_files = (
        'script/wqpSiteMap.js',
        'script/tests/lib/sinon-1.9.1.js',
        'script/tests/*.spec.js'
    )
    
urlpatterns = patterns('',
    url(r'^jasmine/$', 
        ProjectJasmineView.as_view(),
        name='project_jasmine_js_tests'),                
)

