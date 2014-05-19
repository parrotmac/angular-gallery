from django.conf.urls import url
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from StockPhotos.models import *
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



# def home(request):
#     primary_feature = GalleryFeature.objects.filter(type='0')[0] # You can call .first() or address [0]
#     secondary_feature_top = GalleryFeature.objects.filter(type='1')[0]
#     secondary_feature_bottom = GalleryFeature.objects.filter(type='2')[0]
#     return render(request, "base.html", {'galleries': Gallery.objects.all(),
#                                          'latest': Photo.objects.all().reverse()[:5],
#                                          'primary_feature': primary_feature,
#                                          'secondary_feature_top': secondary_feature_top,
#                                          'secondary_feature_bottom': secondary_feature_bottom})


def list_galleries(request):
    return HttpResponse("Omg this doesn't actually work.")


def get_gallery_by_id(request, gallery_id):
    images = Photo.objects.filter(gallery=gallery_id)
    return render(request, 'gallery.html', {'gallery': Gallery.objects.get(pk=gallery_id), 'images': images})
    # return render(request, 'gallery.html', {"gallery": Gallery.objects.filter(pk=gallery_id)[0]})
    # gallery_images = Photo.objects.filter(gallery=gallery_id)
    # gallery_name = gallery_images[0].gallery.name
    # return render(request, "gallery.html", {'gallery_name': gallery_name, 'images': gallery_images})


def get_gallery_by_slug(request, gallery_slug):
    # gallery_images = Photo.objects.filter(gallery__slug__contains=gallery_slug)
    requested_gallery = Gallery.objects.filter(slug__contains=gallery_slug)[0]
    images = Photo.objects.filter(gallery=requested_gallery.pk) # ################################################Need to paginate
    return render(request, "gallery.html", {'gallery': requested_gallery, "images": images})
    # print(gallery_slug)
    # return HttpResponse("Are you looking for %s?" % gallery_slug)


def image(request, image_id):
    image_to_display = Photo.objects.filter(pk=image_id)[0]
    return HttpResponse("You're looking for this: <img src=\"%s\" />" % image_to_display.image.url)


def user_login(request):
    notwelcome = {}
    is_staff = False
    if request.method == 'POST':
        if request.POST.has_key('logout'):
            logout(request)
        else:
            #Login
            username = request.POST['username']
            password = request.POST['password']
            active_user = authenticate(username=username, password=password)
            if active_user is not None:
                if active_user.is_active:
                    login(request, active_user)
                    if active_user.is_staff:
                        is_staff = True
                        #TODO: Allow editing

                    # If user was going somewhere, but needs to sign in first,
                    # this will send them on their way once authenticated
                    if 'next' in request.GET.keys():
                        return HttpResponseRedirect(request.GET['next'])
                    else:
                        return HttpResponseRedirect("/")
                else:
                    notwelcome['disabled'] = 'This account has been disabled.'
            else:
                notwelcome['invalid'] = "Invalid username or password"
    return render(request, "login.html", {'notwelcome': notwelcome})

def home(request):

    primary_feature = GalleryFeature.objects.filter(type='0').first()  # You can call .first() or address [0]
    secondary_feature_top = GalleryFeature.objects.filter(type='1').first()
    secondary_feature_bottom = GalleryFeature.objects.filter(type='2').first()

    not_welcome = {}
    is_staff = False
    if request.method == 'POST':
        if request.POST.has_key('logout'):
            logout(request)
        else:
            #Login
            username = request.POST['username']
            password = request.POST['password']
            active_user = authenticate(username=username, password=password)
            if active_user is not None:
                if active_user.is_active:
                    login(request, active_user)
                    if active_user.is_staff:
                        is_staff = True
                        #TODO: Allow editing

                    # If user was going somewhere, but needs to sign in first,
                    # this will send them on their way once authenticated
                    if 'next' in request.GET.keys():
                        return HttpResponseRedirect(request.GET['next'])
                    else:
                        return HttpResponseRedirect("/")
                else:
                    not_welcome['disabled'] = 'This account has been disabled.'
            else:
                not_welcome['invalid'] = "Invalid username or password"
    return render(request, "base.html", {'problems': not_welcome,
                                         'is_staff': is_staff,
                                         'galleries': Gallery.objects.all(),
                                         'latest': Photo.objects.all().reverse()[:5],
                                         'primary_feature': primary_feature,
                                         'secondary_feature_top': secondary_feature_top,
                                         'secondary_feature_bottom': secondary_feature_bottom})


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage(request):
    return render(request, "manage/manage_base.html")


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_galleries(request):
    if request.method == "POST":
        if 'new_gallery' in request.POST:
            new_gallery = Gallery.objects.create(name=request.POST['name'], slug=request.POST['slug'])
            new_gallery.save()
            json_response = '{"id": "%s", "name":"%s", "slug":"%s"}' % (new_gallery.pk, new_gallery.name, new_gallery.slug)
            return HttpResponse(json_response)
        elif request.POST.has_key('gallery_to_delete'):
            Gallery.objects.get(pk=request.POST['gallery_to_delete']).delete()
        elif request.POST.has_key('rename'):
            gallery = Gallery.objects.get(pk=request.POST['gallery_id'])
            gallery.name = request.POST['name']
            gallery.slug = request.POST['slug']
            gallery.save()
            json_response = '{"id": "%s", "name":"%s", "slug":"%s"}' % (gallery.pk, gallery.name, gallery.slug)
            return HttpResponse(json_response)
    return render(request, "manage/manage_galleries.html", {"galleries": Gallery.objects.all().order_by('pk')})


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_gallery(request, gallery_id):
    return render(request, "manage/manage_gallery.html", {'gallery': Gallery.objects.get(pk=gallery_id), 'images': Photo.objects.filter(gallery=gallery_id)})


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_photos(request, page_number=None):
    image_list = Photo.objects.all()
    paginator = Paginator(image_list, 24) # Whoohoo for 6x4
    try:
        images = paginator.page(page_number)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        images = paginator.page(paginator.num_pages)
    return render(request, "manage/manage_photos.html", {'photos': images})


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_photos_by_id(request, image_id):
    return render(request, "manage/manage_photo.html", {'image': Photo.objects.get(pk=image_id), 'image_attributes': ImageAttributes.objects.all(), 'galleries': Gallery.objects.all(), 'tags': Tag.objects.all()})


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_clients(request):
    return render(request, "")


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_upload(request):
    return render(request, "manage/mange_upload.html", {'galleries': Gallery.objects.all()})


# @user_passes_test(lambda u:u.is_staff, login_url='/login/')
# def manage_gallery_slug(request, gallery_slug):
#     return render(request, "manage/manage_gallery_old.html", {"gallery": Gallery.objects.get(slug__contains=gallery_slug),
#                                                    "images_in_gallery": Photo.objects.filter(
#                                                        gallery=Gallery.objects.get(slug=gallery_slug).pk)})