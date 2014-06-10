from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
# from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'StockPhotos.views.view_home', name='home'),
    url(r'^gallery/(?P<gallery_id>\d+)', 'StockPhotos.views.view_gallery', name='view_gallery'),
    url(r'^photo/(?P<photo_id>\d+)', 'StockPhotos.views.view_photo', name='view_photo'),
    url(r'^lightbox/(?P<lightbox_id>\d+)', 'StockPhotos.views.lightbox', name='view_lightbox_id'),
    url(r'^lightbox/', 'StockPhotos.views.lightbox', name='view_lightbox'),
    url(r'^create-account/', 'StockPhotos.views.user_create_account', name='user_create_account'),

    url(r'^json/tags/', 'StockPhotos.views.get_tags', name="get_all_tags"),
    url(r'^json/lightbox/', 'StockPhotos.views.user_lightbox_ajax', name="user_lightbox_ajax"),

    url(r'^login/', 'StockPhotos.views.user_login', name="login"),

    url(r'^dump/image-paths', 'StockPhotos.views.dump_image_paths'),

    url(r'^manage/$', 'StockPhotos.views.manage', name='manage_home'),
    url(r'^manage/gallery/$', 'StockPhotos.views.manage_galleries', name='manage_gallery'),
    url(r'^manage/gallery/(?P<gallery_id>\d+)', 'StockPhotos.views.manage_gallery', name='manage_gallery_by_id'),
    url(r'^manage/gallery/cover/$', 'StockPhotos.views.manage_gallery_cover', name='manage_gallery_cover'),
    url(r'^manage/photo/$', 'StockPhotos.views.manage_photos', name='manage_photos'),
    url(r'^manage/photo/page/(?P<page_number>\d+)$', 'StockPhotos.views.manage_photos', name='manage_photos_by_page'),
    url(r'^manage/photo/(?P<image_id>\d+)', 'StockPhotos.views.manage_photo', name='manage_photo_by_id'),
    url(r'^manage/clients/$', 'StockPhotos.views.manage_clients', name='manage_clients'),
    url(r'^manage/clients/(?P<image_id>\d+)$', 'StockPhotos.views.view_client', name='view_client'),
    url(r'^manage/photo/json/$', 'StockPhotos.views.manage_photo_json', name='manage_photo_json'),
    url(r'^manage/tag/json/$', 'StockPhotos.views.manage_tag_json', name='manage_tag_json'),
    url(r'^manage/gallery/json/$', 'StockPhotos.views.manage_gallery_json', name='manage_gallery_json'),
    url(r'^manage/upload/$', 'StockPhotos.views.manage_upload', name='manage_upload'),
    url(r'^manage/features/$', 'StockPhotos.views.manage_feature_upload', name='manage_feature_upload'),
    # url(r'^manage/gallery/(?P<gallery_slug>[-\w]+)', 'StockPhotos.views.manage_gallery_slug', name='gallery_slug'),

    # Just for development
    url(r'^admin/', include(admin.site.urls)),
)
#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()