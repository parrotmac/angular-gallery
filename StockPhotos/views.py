from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from StockPhotos.models import *
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from AngualrGallery import settings
from django.core.files import File
from django.template import *
from iptcinfo import IPTCInfo
from django.core.mail import send_mail
import re
import cStringIO
from PIL import Image
import uuid
import os
import json


primary_feature_attributes = ['primary_feature_img',
                              'primary_feature_heading',
                              'primary_feature_subheading',
                              'primary_target_gallery']

secondary_feature_attributes = ['secondary_feature_img',
                                'secondary_feature_heading',
                                'secondary_feature_subheading',
                                'secondary_target_gallery']

def user_login(request):
    notwelcome = {}
    is_staff = False
    if request.method == 'POST':
        if request.POST.has_key('logout'):
            logout(request)
            if 'next' in request.GET.keys():
                return HttpResponseRedirect(request.GET['next'])
            else:
                return HttpResponseRedirect("/")
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
    return render_to_response("login.html", {'notwelcome': notwelcome}, context_instance=RequestContext(request))


def dump_image_paths(request):
    return render(request, "dump_image_paths.html", {'images': Photo.objects.all()})


def view_home(request):
    lightboxes = None
    if request.user.is_authenticated():
        lightboxes = LightBox.objects.filter(user=Customer.objects.get(user=request.user))
    response_dict = {'thumbnail_galleries': Gallery.objects.filter(active=True).order_by('pk'), 'lightboxes': lightboxes}
    for primary in primary_feature_attributes:
        response_dict[primary] = Configuration.get_pref(primary)
    for secondary in secondary_feature_attributes:
        response_dict[secondary] = Configuration.get_pref(secondary)
    return render_to_response("home.html", response_dict, context_instance=RequestContext(request))


def view_gallery(request, gallery_id):
    lightboxes = None
    if request.user.is_authenticated():
        lightboxes = LightBox.objects.filter(user=Customer.objects.get(user=request.user))
    photo_list = Photo.objects.filter(gallery=gallery_id)
    paginator = Paginator(photo_list, 16)
    page = request.GET.get('page')
    try:
        photos = paginator.page(page)
    except PageNotAnInteger:
        photos = paginator.page(1)
    except EmptyPage:
        photos = paginator.page(paginator.num_pages)
    return render(request, "gallery.html", {'gallery': Gallery.objects.get(id=gallery_id),
                                            'photos': photos,
                                            'lightboxes': lightboxes}, context_instance=RequestContext(request))


def view_photo(request, photo_id):
    lightboxes = None
    if request.user.is_authenticated():
        lightboxes = LightBox.objects.filter(user=Customer.objects.get(user=request.user))
    return render(request, "photo.html", {'photo': Photo.objects.get(id=photo_id),
                                          'lightboxes': lightboxes}, context_instance=RequestContext(request))


def lightbox(request, lightbox_id=None):
    if request.user.is_authenticated():
        if request.method == 'POST':
            if "lightbox-delete" in request.POST:
                LightBox.objects.get(id=request.POST['lightbox-delete']).delete()
                return HttpResponseRedirect("/")
        lightboxes = LightBox.objects.filter(user=Customer.objects.get(user=request.user))
        if lightbox_id:
            lightbox = LightBox.objects.get(id=lightbox_id)
            lb_photos = lightbox.images.all()
            paginator = Paginator(lb_photos, 16)
            page = request.GET.get('page')
            try:
                photos = paginator.page(page)
            except PageNotAnInteger:
                photos = paginator.page(1)
            except EmptyPage:
                photos = paginator.page(paginator.num_pages)
            if lightbox.user.user == request.user:
                return render_to_response("lightbox.html", {'lightbox': lightbox, 'photos': photos, 'lightboxes': lightboxes}, context_instance=RequestContext(request))
            else:
                # return HttpResponse("You're not authorized to view this lightbox")
                return HttpResponseRedirect("/")
        else:
            if lightboxes.count() < 1:
                lightboxes = None
            return render_to_response("lightboxes.html", {'lightboxes': lightboxes}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse("login"))


def user_lightbox_ajax(request):
    if request.method == "POST":
        if request.POST['transaction_type'] == 'create':
            new_or_excisting_lb = LightBox.objects.get_or_create(name=request.POST['lightboxName'],
                                                                 user=Customer.objects.get(user=request.POST['userId']))
            new_lb_id = new_or_excisting_lb[0].id
            new_lb_name = new_or_excisting_lb[0].name
            return HttpResponse(json.dumps({'success': True, 'id': new_lb_id, 'name': new_lb_name}),
                                content_type='application/json')
        if request.POST['transaction_type'] == 'delete':
            LightBox.objects.filter(id=request.POST['id']).delete()
            return HttpResponse(json.dumps({'success': True}), content_type='application/json')
        if request.POST['transaction_type'] == 'add_photo':
            new_lb_relation = LightBox.objects.get(id=request.POST['lightbox_id']).images.add(Photo.objects.get(id=request.POST['image_id']))
            return HttpResponse(json.dumps({'success': True}), content_type='application/json')
        if request.POST['transaction_type'] == 'remove_photo':
            photo_id = request.POST['photo_id']
            target_lightbox = LightBox.objects.get(id=request.POST['lightbox_id'])
            if target_lightbox.user.user == request.user:
                target_lightbox.images.remove(Photo.objects.get(id=photo_id))
                return HttpResponse(json.dumps({'success': True, 'photo_id': photo_id}), content_type='application/json')
            else:
                return HttpResponse(json.dumps({'success': False, 'reason': 'unauthorized'}))
    return HttpResponse(json.dumps({'success': False}), content_type='application/json')


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage(request):
    return render(request, "manage/manage_base.html")

@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_gallery_cover(request):
    selected_gallery = request.GET['selected_gallery'] if 'selected_gallery' in request.GET else None
    return render(request, "manage/manage_gallery_covers.html",
                  {'galleries': Gallery.objects.all().order_by("pk"),
                   'selected_gallery': selected_gallery})

@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_galleries(request):
    if request.method == "POST":
        if 'new_gallery' in request.POST:
            new_gallery = Gallery.objects.create(name=request.POST['name'], slug=request.POST['slug'])
            new_gallery.save()
            json_response = '{"id": "%s", "name":"%s", "slug":"%s"}' % (new_gallery.pk, new_gallery.name, new_gallery.slug)
            return HttpResponse(json_response)
        elif 'gallery_to_delete' in request.POST:
            Gallery.objects.get(pk=request.POST['gallery_to_delete']).delete()
            return HttpResponse(json.dumps({"success": True}))
        elif 'rename' in request.POST:
            gallery = Gallery.objects.get(pk=request.POST['gallery_id'])
            gallery.name = request.POST['name']
            gallery.slug = request.POST['slug']
            gallery.save()
            json_response = '{"id": "%s", "name":"%s", "slug":"%s"}' % (gallery.pk, gallery.name, gallery.slug)
            return HttpResponse(json_response)
        elif 'toggle_active' in request.POST:
            gallery_to_toggle = Gallery.objects.get(pk=request.POST['toggle_active'])
            if request.POST['active_state'] == 'true':
                gallery_to_toggle.active = True
            else:
                gallery_to_toggle.active = False
            gallery_to_toggle.save()
            return HttpResponse(json.dumps({gallery_to_toggle.pk: gallery_to_toggle.active}))
    return render(request, "manage/manage_galleries.html", {"galleries": Gallery.objects.all().order_by('pk')})


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_gallery(request, gallery_id):
    return render(request, "manage/manage_gallery.html", {'gallery': Gallery.objects.get(pk=gallery_id), 'images': Photo.objects.filter(gallery=gallery_id).order_by('pk')})


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_photos(request, page_number=None):
    image_list = Photo.objects.all().order_by('pk')
    paginator = Paginator(image_list, 24)  # Whoohoo for 6x4
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
        photo_to_change = Photo.objects.get(id=request.POST['photoPk'])
        if request.POST['transaction_type'] == 'photo-gallery-relation':
            suspect_gallery = Gallery.objects.get(id=request.POST['galleryPk'])
            if request.POST['makeBreak'] == "true":
                photo_to_change.gallery.add(suspect_gallery.pk)
            else:
                photo_to_change.gallery.remove(suspect_gallery)
            return HttpResponse(json.dumps({"success": True}))
        if request.POST['transaction_type'] == 'title':
            photo_to_change.title = request.POST['value']
        if request.POST['transaction_type'] == 'published':
            photo_to_change.published = True if request.POST['value'] == 'true' else False
            print request.POST['value']
        if request.POST['transaction_type'] == 'delete' and request.POST['value'] == 'confirm':
            photo_to_change.obliterate_object()  # This deletes the records, as well as the file
            return HttpResponse(json.dumps({'success': True}))
        if request.POST['transaction_type'].startswith('attr_'):
            setattr(photo_to_change, request.POST['transaction_type'], request.POST['value'])
            return HttpResponse(json.dumps({'success': True}))
        if request.POST['transaction_type'].endswith('_release'):
            setattr(photo_to_change, request.POST['transaction_type'], request.POST['value'])
        photo_to_change.save()
        HttpResponse(json.dumps({'success': True}))
    return HttpResponse(json.dumps({"cool": True}))

@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_gallery_json(request):
    if request.method == "POST":
        if 'transaction_type' in request.POST:
            if request.POST['transaction_type'] == "gallery_cover":
                update_gallery = Gallery.objects.get(pk=request.POST['gallery_id'])
                update_gallery.cover_photo = Photo.objects.get(id=request.POST['photo_id'])
                update_gallery.save()
                return HttpResponse(json.dumps({"success": True}))
    if 'gallery_id' in request.GET:
        image_array = []
        images = list(Photo.objects.filter(gallery=request.GET['gallery_id']))
        gallery = Gallery.objects.get(pk=request.GET['gallery_id'])
        galleries_with_cover_photos = []
        for gal in Gallery.objects.all():
            if gal.cover_photo_defined():
                galleries_with_cover_photos.append(gal)
        gallery_photo_id = None
        if gallery.cover_photo_defined():
            gallery_photo_id = gallery.cover_photo.id
        for image in images:
            other_gallery_covers = []
            for gallery_with_cover in galleries_with_cover_photos:
                if str(gallery_with_cover.id) != request.GET['gallery_id']:
                    if image.id == gallery_with_cover.cover_photo.id:
                        other_gallery_covers.append({"id": gallery_with_cover.id, "name": gallery_with_cover.name})
            galleries_in = list(image.gallery.all())
            gallery_in_array = []
            for gi in galleries_in:
                if str(gi.id) != request.GET['gallery_id']:
                    gallery_in_array.append({"id": gi.id, "name": gi.name, "cover_for": 0})
            image_array.append({"id": image.id, "thumbnail_url": image.thumbnail.url, "title": image.title, "published": image.published, "cover": True if gallery_photo_id == image.id else False, 'other_galleries_in': gallery_in_array, 'also_cover_for': other_gallery_covers})
        return HttpResponse(json.dumps(image_array))
    return HttpResponse(json.dumps({"galleries": "r us"}))

@user_passes_test(lambda u: u.is_staff, login_url='/login/')  # This won't work for the rest api...we need to make it
def manage_tag_json(request):
    if request.method == "POST":
        if request.POST['transaction_type'] == 'update_tags':
            photo = Photo.objects.get(id=request.POST['photoId'])
            photo_tags = photo.tags.values('id')
            tag_array = request.POST['tag_list'].split(",")

            #The 'for' nonsense below can be fixed by simply 'get_or_create'-ing all the tags in the request, adding all
            #  to the photo, then looping though the tags in the photo and creating a "destroy array" of all the objects
            #  not in the array

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
                                                            'galleries': Gallery.objects.all(),
                                                            'tags': Tag.objects.all()})


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_clients(request):
    return render_to_response("manage/manage_clients.html", {'customers': Customer.objects.all()})


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def view_client(request, image_id):
    return render_to_response('manage/manage_client.html', {"customer": Customer.objects.get(id=image_id)})


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_upload(request):
    if request.method == "POST":
        if request.POST['transaction_type'] == "upload":
            data_uri = request.POST['image']
            img_str = re.search(r'base64,(.*)', data_uri).group(1)
            temp_thumb_img = cStringIO.StringIO(img_str.decode('base64'))
            temp_preview_img = cStringIO.StringIO(img_str.decode('base64'))
            temp_full_img = cStringIO.StringIO(img_str.decode('base64'))
            temp_tags_img = cStringIO.StringIO(img_str.decode('base64'))
            try:
                thumbnail_image = Image.open(temp_thumb_img)
                preview_image = Image.open(temp_preview_img)
                img_image = Image.open(temp_full_img)
            except IOError, e:
                json_response = '{"id": "%s", "error": "%s"}' % (request.POST['id'], str(e))
                return HttpResponseServerError(json_response)

            thumbnail_size = 160, 160
            preview_size = 600, 600
            image_size = 1000, 1000

            thumbnail_image.thumbnail(thumbnail_size, Image.ANTIALIAS)
            preview_image.thumbnail(preview_size, Image.ANTIALIAS)
            img_image.thumbnail(image_size, Image.ANTIALIAS)

            thumbnail_file_path = os.path.join(settings.MEDIA_ROOT, "tmp", str(uuid.uuid1()) + ".jpg")
            preview_file_path = os.path.join(settings.MEDIA_ROOT, "tmp", str(uuid.uuid1()) + ".jpg")
            image_file_path = os.path.join(settings.MEDIA_ROOT, "tmp", str(uuid.uuid1()) + ".jpg")

            thumbnail_image.save(thumbnail_file_path, "JPEG")
            preview_image.save(preview_file_path, "JPEG")
            img_image.save(image_file_path, "JPEG")

            orientation = None
            if thumbnail_image.size[0] > thumbnail_image.size[1]:
                orientation = 'attr_horizontal'
            elif thumbnail_image.size[0] < thumbnail_image.size[1]:
                orientation = 'attr_vertical'

            image_tags = []
            try:
                image_tags = IPTCInfo(temp_tags_img).keywords
            except Exception:
                pass  # We're just not gonna have keywords

            new_image = Photo.objects.create(title='',
                                             image=File(open(image_file_path)),
                                             thumbnail=File(open(thumbnail_file_path)),
                                             preview=File(open(preview_file_path)))

            setattr(new_image, orientation, True)

            os.remove(thumbnail_file_path)
            os.remove(preview_file_path)
            os.remove(image_file_path)

            json_tags_response = []

            for tag in image_tags:
                possibly_new_tag = Tag.objects.get_or_create(tag=tag)
                json_tags_response.append({'value': possibly_new_tag[0].id, 'text': possibly_new_tag[0].tag })
                new_image.tags.add(possibly_new_tag[0].id)

            new_image.save()

            return HttpResponse(json.dumps({"id": request.POST['id'],
                                            "siteId": new_image.pk,
                                            "thumbnailUrl": new_image.thumbnail.url,
                                            "tags": json_tags_response,
                                            "orientation": orientation}))
    target_gallery_id = None
    target_gallery_name = None
    if 'target' in request.GET:
        target_gallery_id = request.GET['target']
        target_gallery_name = Gallery.objects.get(pk=target_gallery_id).name
    return render(request, "manage/manage_upload.html", {'galleries': Gallery.objects.all(),
                                                         'tags': Tag.objects.all(),
                                                         'target_gallery_id': target_gallery_id,
                                                         'target_gallery_name': target_gallery_name})


@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def manage_feature_upload(request):
    if request.method == "POST":

        if request.POST['transaction_type'] == 'primary_feature':
            Configuration.set_pref(primary_feature_attributes[1], request.POST[primary_feature_attributes[1]])
            Configuration.set_pref(primary_feature_attributes[2], request.POST[primary_feature_attributes[2]])
            Configuration.set_pref(primary_feature_attributes[3], request.POST[primary_feature_attributes[3]])
            if primary_feature_attributes[0] in request.FILES:
                feature_file = request.FILES[primary_feature_attributes[0]]
                file_type = feature_file.content_type.split("/")[1]
                file_extension = None
                if file_type == "png":
                    file_extension = file_type
                if file_type == "jpeg" or file_type == "jpg":
                    file_extension = 'jpg'
                file_name = str(os.path.join("uploads/features", str(uuid.uuid1()) + "." + file_extension))
                feature_file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                Configuration.set_pref(primary_feature_attributes[0], file_name)
                with open(feature_file_path, 'wb+') as destination:
                    for chunk in feature_file.chunks():
                        destination.write(chunk)

        if request.POST['transaction_type'] == 'secondary_feature':
            Configuration.set_pref(secondary_feature_attributes[1], request.POST[secondary_feature_attributes[1]])
            Configuration.set_pref(secondary_feature_attributes[2], request.POST[secondary_feature_attributes[2]])
            Configuration.set_pref(secondary_feature_attributes[3], request.POST[secondary_feature_attributes[3]])
            if secondary_feature_attributes[0] in request.FILES:
                feature_file = request.FILES[secondary_feature_attributes[0]]
                file_type = feature_file.content_type.split("/")[1]
                file_extension = None
                if file_type == "png":
                    file_extension = file_type
                if file_type == "jpeg" or file_type == "jpg":
                    file_extension = 'jpg'
                file_name = str(os.path.join("uploads/features", str(uuid.uuid1()) + "." + file_extension))
                feature_file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                Configuration.set_pref(secondary_feature_attributes[0], file_name)
                with open(feature_file_path, 'wb+') as destination:
                    for chunk in feature_file.chunks():
                        destination.write(chunk)

    request_dictionary = {}
    for attribute in primary_feature_attributes:
        request_dictionary[attribute] = Configuration.get_pref(attribute)
    for attribute in secondary_feature_attributes:
        request_dictionary[attribute] = Configuration.get_pref(attribute)
    request_dictionary['galleries'] = Gallery.objects.all()
    return render_to_response("manage/manage_features.html", request_dictionary, context_instance=RequestContext(request))


# @user_passes_test(lambda u:u.is_staff, login_url='/login/')
# def manage_gallery_slug(request, gallery_slug):
#     return render(request, "manage/manage_gallery_old.html", {"gallery": Gallery.objects.get(slug__contains=gallery_slug),
#                                                    "images_in_gallery": Photo.objects.filter(
#                                                        gallery=Gallery.objects.get(slug=gallery_slug).pk)})


def get_tags(request):
    tags = list(Tag.objects.values('tag'))
    tag_array = []
    for tag in tags:
        tag_array.append(tag.values()[0])
    return HttpResponse(json.dumps({"tags": tag_array}), content_type='application/json')


def user_create_account(request):
    if request.method == "POST":
        param_dict = {}
        base_user = User.objects.create_user(str(uuid.uuid1())[:30], request.POST['email'], request.POST['password'], first_name=request.POST['first_name'], last_name=request.POST['last_name'])
        base_customer = Customer.objects.create(user=base_user)
        for field in Customer._meta.fields:
            field_name = field.attname
            if field_name == 'id':
                continue
            if field_name == 'user_id':
                continue
        #     if field_name in ['id', 'user_id', 'email', 'password', 'password_repeat', 'csrfmiddlewaretoken']:
            print "CONGRATULATIONS! YOU FOUND " + field_name
        #         continue
        #     print field_name
        #     if request.POST[field_name] is not None:
            if request.POST[field_name] == 'agree_tos':
                if request.request.POST[field_name] == 'on':
                    setattr(base_customer, field_name, True)
            setattr(base_customer, field_name, request.POST[field_name])
        base_customer.save()
        send_mail('Matthew Turley Stock Photography',
                  base_customer.user.first_name + ',\n\n\tThanks for creating an account at MatthewTurleyStock.com.\n\n-The User Robot',
                  'stock@matthewturleystock.com',
                  [base_customer.user.email],
                  fail_silently=True)
        active_user = authenticate(email=request.POST['email'], password=request.POST['password'])
        login(request, active_user)
        return render_to_response('user_create_success.html', context_instance=RequestContext(request))
        # return  HttpResponse(json.dumps(request.POST), content_type='application/json')
    return render_to_response('user_create_account.html', context_instance=RequestContext(request))


def search(request):
    if 'q' in request.GET:
        search_term = request.GET.get('q').strip()
        if search_term == "":
            return render_to_response('search.html', context_instance=RequestContext(request))
        print search_term
        # tags_query = Tag.objects.filter(tag__icontains=search_term)
        # print tags_query.__len__()
        # photo_queries = Photo.objects.filter(tags__in=tags_query)
        # print photo_queries
        # return render_to_response('search.html', {'photos': photo_queries}, context_instance=RequestContext(request))
        matched_tags = []
        search_results = []
        for query_tag in Tag.objects.filter(tag__icontains=search_term):
            if query_tag not in matched_tags:
                matched_tags.append(query_tag)
            for query_photo in query_tag.photos.all():
                if query_photo not in search_results:
                    search_results.append(query_photo)

        paginator = Paginator(search_results, 16)
        page = request.GET.get('page')
        try:
            photos = paginator.page(page)
        except PageNotAnInteger:
            photos = paginator.page(1)
        except EmptyPage:
            photos = paginator.page(paginator.num_pages)

        # if search_term.endswith("s"):
        #     not_plural_search_term = search_term[:-1]
        #     for query_tag in Tag.objects.filter(tag__icontains=not_plural_search_term):
        #         if query_tag.photos.all() not in search_results:
        #             search_results.append(query_tag.photos.all())
        return render_to_response('search.html', {'matched_photos': photos, 'matched_tags': matched_tags, 'search_term': search_term}, context_instance=RequestContext(request))
    return render_to_response('search.html', context_instance=RequestContext(request))