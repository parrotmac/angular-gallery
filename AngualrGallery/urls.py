from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'StockPhotos.views.home', name='home'),
    url(r'^login/', 'StockPhotos.views.user_login', name="login_required"),
    url(r'^galleries/$', 'StockPhotos.views.list_galleries', name='galleries'),
    url(r'^gallery/(?P<gallery_id>\d{5})', 'StockPhotos.views.get_gallery_by_id', name='gallery_id'),
    url(r'^gallery/(?P<gallery_slug>[-\w]+)', 'StockPhotos.views.get_gallery_by_slug', name='gallery_slug'),
    url(r'^image/(?P<image_id>\d+)', 'StockPhotos.views.image', name='image_id'),

    # url(r'^login/', 'StockPhotos.views.user_login'),

    # url(r'^manage/galleries/', 'StockPhotos.views.manage_galleries'),
    url(r'^manage/$', 'StockPhotos.views.manage', name='manage_home'),
    url(r'^manage/gallery/$', 'StockPhotos.views.manage_galleries', name='manage_gallery'),
    url(r'^manage/gallery/(?P<gallery_id>\d+)', 'StockPhotos.views.manage_gallery', name='manage_gallery_by_id'),
    url(r'^manage/photo/$', 'StockPhotos.views.manage_photos', name='manage_photos'),
    url(r'^manage/photo/page/(?P<page_number>\d+)$', 'StockPhotos.views.manage_photos', name='manage_photos_by_page'),
    url(r'^manage/photo/(?P<image_id>\d+)', 'StockPhotos.views.manage_photos_by_id', name='manage_photo_by_id'),
    url(r'^manage/clients/$', 'StockPhotos.views.manage_clients', name='manage_clients'),

    url(r'^manage/upload/$', 'StockPhotos.views.manage_upload', name='manage_upload'),
    # url(r'^manage/gallery/(?P<gallery_slug>[-\w]+)', 'StockPhotos.views.manage_gallery_slug', name='gallery_slug'),

    # Just for development
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))