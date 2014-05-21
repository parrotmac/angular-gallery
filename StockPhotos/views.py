from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from StockPhotos.models import *
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from AngualrGallery import settings
from django.core.files import File
from iptcinfo import IPTCInfo
import re
import cStringIO
import Image
import uuid
import os
import json



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


@user_passes_test(lambda u: u.is_staff, login_url='/login/')  # This won't work for the rest api...we need to make it
def manage_photo_json(request):
    if request.method == "POST":
        if request.POST['transaction_type'] == 'photo-gallery-relation':
            photo_to_change = Photo.objects.get(id=request.POST['photoPk'])
            suspect_gallery = Gallery.objects.get(id=request.POST['galleryPk'])
            if request.POST['makeBreak'] == "true":
                photo_to_change.gallery.add(suspect_gallery.pk)
            else:
                photo_to_change.gallery.remove(suspect_gallery)
            return HttpResponse(json.dumps({"success": True}))
    return HttpResponse(json.dumps({"cool": True}))

@user_passes_test(lambda u: u.is_staff, login_url='/login/')  # This won't work for the rest api...we need to make it
def manage_tag_json(request):
    if request.method == "POST":
        if request.POST['transaction_type'] == 'update_tags':
            photo = Photo.objects.get(id=request.POST['photoId'])
            photo_tags = photo.tags.values('id')
            tag_array = request.POST['tag_list'].split(",")

            client_tag_id_array = []

            for tag in tag_array:
                maybe_new_tag = Tag.objects.get_or_create(tag=tag)
                client_tag_id_array.append(maybe_new_tag[0].id)

            current_tag_id_array = []

            for photo_tag_id in photo_tags.values_list():
                current_tag_id_array.append(photo_tag_id[0])

            collision_array = []

            for current_tag in current_tag_id_array:
                for client_tag in client_tag_id_array:
                    if int(current_tag) == int(client_tag):
                        collision_array.append(current_tag)

            for collision in collision_array:
                current_tag_id_array.remove(collision)
                client_tag_id_array.remove(collision)

            for current_id in current_tag_id_array:
                photo.tags.remove(current_id)
            for client_id in client_tag_id_array:
                photo.tags.add(client_id)

            HttpResponse(json.dumps("YAY"), content_type='application/json')
    tags = list(Tag.objects.values('tag'))
    tag_array = []
    for tag in tags:
        tag_array.append(tag.values()[0])
    return HttpResponse(json.dumps(tag_array), content_type='application/json')

    # tags = list(Tag.objects.values('tag'))
    # return HttpResponse(json.dumps(tags), content_type='application/json')


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_photo(request, image_id):
    if request.method == "POST":
        modify_photo = Photo.objects.get(pk=image_id)
        if request.POST['update_type'] is "description":
            modify_photo.description = request.POST['description']
            modify_photo.save()
        if request.POST['update_type'] is "tags":
            print request.POST['tags']
        if request.POST['update_type'] is "other":
            print json.dump(request.POST)
    else:
        return render(request, "manage/manage_photo.html", {'image': Photo.objects.get(pk=image_id),
                                                        'image_attributes': ImageAttributes.objects.all(),
                                                        'galleries': Gallery.objects.all(),
                                                        'tags': Tag.objects.all()})


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_clients(request):
    return render(request, "")


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_upload(request):
    if request.method == "POST":
        if request.POST['transaction_type'] == "upload":
            data_uri = request.POST['image']
            img_str = re.search(r'base64,(.*)', data_uri).group(1)
            temp_thumb_img = cStringIO.StringIO(img_str.decode('base64'))
            temp_preview_img = cStringIO.StringIO(img_str.decode('base64'))
            temp_tags_img = cStringIO.StringIO(img_str.decode('base64'))
            try:
                thumbnail_image = Image.open(temp_thumb_img)
                preview_image = Image.open(temp_preview_img)
            except IOError, e:
                json_response = '{"id": "%s", "error": "%s"}' % (request.POST['id'], str(e))
                return HttpResponseServerError(json_response)

            thumbnail_size = 160, 160
            preview_size = 600, 600

            thumbnail_image.thumbnail(thumbnail_size, Image.ANTIALIAS)
            preview_image.thumbnail(preview_size, Image.ANTIALIAS)

            thumbnail_file_path = os.path.join(settings.MEDIA_ROOT, "tmp", str(uuid.uuid1()) + ".jpg")
            preview_file_path = os.path.join(settings.MEDIA_ROOT, "tmp", str(uuid.uuid1()) + ".jpg")

            thumbnail_image.save(thumbnail_file_path, "JPEG")
            preview_image.save(preview_file_path, "JPEG")

            image_tags = []
            try:
                image_tags = IPTCInfo(temp_tags_img).keywords
            except Exception:
                pass  # We're just not gonna have keywords

            print "Thumbnail temp: " + thumbnail_file_path + "\n Preview temp: " + preview_file_path

            new_image = Photo.objects.create(title='',
                                             image=File(open(preview_file_path)),
                                             thumbnail=File(open(thumbnail_file_path)))

            if os.remove(thumbnail_file_path) and os.remove(preview_file_path):
                print "Removed thumbnail and preview"

            json_tags_response = []

            for tag in image_tags:
                possibly_new_tag = Tag.objects.get_or_create(tag=tag)
                json_tags_response.append({'value': possibly_new_tag[0].id, 'text': possibly_new_tag[0].tag })
                new_image.tags.add(possibly_new_tag[0].id)

            print json.dumps(json_tags_response)

            new_image.save()

            return HttpResponse(json.dumps({"id": request.POST['id'],
                                            "siteId": new_image.pk,
                                            "thumbnailUrl": new_image.thumbnail.url,
                                            "tags": json_tags_response}))
    return render(request, "manage/manage_upload.html", {'galleries': Gallery.objects.all(), 'tags': Tag.objects.all()})


# @user_passes_test(lambda u:u.is_staff, login_url='/login/')
# def manage_gallery_slug(request, gallery_slug):
#     return render(request, "manage/manage_gallery_old.html", {"gallery": Gallery.objects.get(slug__contains=gallery_slug),
#                                                    "images_in_gallery": Photo.objects.filter(
#                                                        gallery=Gallery.objects.get(slug=gallery_slug).pk)})