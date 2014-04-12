from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from StockPhotos.models import Image, Gallery, GalleryFeature, GalleryCover


def home(request):
    primary_feature = GalleryFeature.objects.filter(type='0')[0] # You can call .first() or address [0]
    secondary_feature_top = GalleryFeature.objects.filter(type='1')[0]
    secondary_feature_bottom = GalleryFeature.objects.filter(type='2')[0]
    return render(request, "base.html", {'galleries': Gallery.objects.all(),
                                         'gallery_covers': GalleryCover.objects.all(),
                                         'primary_feature': primary_feature,
                                         'secondary_feature_top': secondary_feature_top,
                                         'secondary_feature_bottom': secondary_feature_bottom})


def get_gallery_by_id(request, gallery_id):
    gallery_images = Image.objects.filter(gallery=gallery_id)
    return render(request, "gallery.html", {'images': gallery_images})


def get_gallery_by_slug(request, gallery_slug):
    # return HttpResponse("You seem to be looking for: %s" % gallery_slug)
    gallery_images = Image.objects.filter(gallery__slug__contains=gallery_slug)
    return render(request, "gallery.html", {'images': gallery_images})


def image(request, image_id):
    image_to_display = Image.objects.filter(pk=image_id)[0]
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
    return render(request, "base.html", {'problems': notwelcome, 'is_staff': is_staff})


@permission_required('Manage Other Stuff', login_url='/login/')
def manage(request):
    return render("base.html")
