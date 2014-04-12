from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'StockPhotos.views.home', name='home'),
    url(r'^gallery/(?P<gallery_id>\d{5})', 'StockPhotos.views.get_gallery_by_id', name='gallery_id'),
    url(r'^gallery/(?P<gallery_slug>\w+)', 'StockPhotos.views.get_gallery_by_slug', name='gallery_slug'),
    url(r'^image/(?P<image_id>\d+)', 'StockPhotos.views.image', name='image_id'),

    # Just for development
    url(r'^admin/', include(admin.site.urls)),
)
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
