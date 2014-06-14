from django.db import models
from django.contrib.auth.models import User
import os
import json


FEATURE_TYPE = (
    (0, 'Primary Feature'),
    (1, 'Secondary Feature')
)

IMAGE_RELEASE = (
    (0, 'Yes'),
    (1, 'No'),
    (2, 'N/A'),
)


class Customer(models.Model):
    user = models.OneToOneField(User)
    # Django User model includes email and first+last name

    website = models.URLField(verbose_name='Website', blank=True)
    phone_number = models.CharField(max_length=40, blank=True, verbose_name='Phone Number')
    fax_number = models.CharField(max_length=40, blank=True, verbose_name='Fax Number')
    address_1 = models.CharField(max_length=128, blank=True, verbose_name='Address')
    address_2 = models.CharField(max_length=128, blank=True, verbose_name='Address, Line 2')
    city = models.CharField(max_length=30, blank=True, verbose_name='City')
    state = models.CharField(max_length=30, blank=True, verbose_name='State or Province')
    zip = models.CharField(max_length=30, blank=True, verbose_name='ZIP Code')
    country = models.CharField(max_length=128, blank=True, verbose_name='Country')
    agree_tos = models.BooleanField(default=False, blank=False)

    def __unicode__(self):
        return self.user.username


class Gallery(models.Model):
    name = models.CharField(max_length=35)
    slug = models.SlugField(max_length=35)
    active = models.BooleanField(default=False)
    cover_photo = models.ForeignKey('Photo', blank=True, null=True, related_name='gallery_cover_photo')

    def __unicode__(self):
        return self.name

    def get_first_image(self):
        return Photo.objects.filter(gallery=self).first()

    def get_cover_photo(self):
        if self.cover_photo is None:
            return self.get_first_image()
        else:
            return self.cover_photo

    class Meta:
        verbose_name_plural = 'galleries'

    def cover_photo_defined(self):
        return False if self.cover_photo is None else True


class Tag(models.Model):
    tag = models.CharField(max_length=35)

    def __unicode__(self):
        return self.tag


class Photo(models.Model):
    title = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True, null=True)
    gallery = models.ManyToManyField(Gallery, related_name='photos')
    image = models.ImageField(upload_to='uploads/')
    preview = models.ImageField(upload_to='uploads/previews/')
    thumbnail = models.FileField(upload_to='uploads/thumbnails/')
    tags = models.ManyToManyField(Tag, related_name='photos')
    model_release = models.SmallIntegerField(choices=IMAGE_RELEASE, default=2)
    property_release = models.SmallIntegerField(choices=IMAGE_RELEASE, default=2)
    published = models.BooleanField(default=True)

    attr_color = models.BooleanField(blank=True, default=False, verbose_name='Color')
    attr_black_white = models.BooleanField(blank=True, default=False, verbose_name='Black & White')
    attr_vertical = models.BooleanField(blank=True, default=False, verbose_name='Vertical')
    attr_horizontal = models.BooleanField(blank=True, default=False, verbose_name='Horizontal')
    attr_panoramic = models.BooleanField(blank=True, default=False, verbose_name='Panoramic')

    def __unicode__(self):
        if self.title.strip(' ').__len__() > 0:
            return self.title
        else:
            return str(self.pk)

    def get_tags(self):
        return self.tags

    def obliterate_object(self):
        if self.image is not None:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        if self.thumbnail is not None:
            if os.path.isfile(self.thumbnail.path):
                os.remove(self.thumbnail.path)
        self.delete()


class GalleryFeature(models.Model):
    gallery = models.ForeignKey(Gallery)
    image = models.ForeignKey(Photo)
    type = models.SmallIntegerField(choices=FEATURE_TYPE)

    def get_feature_type(self):
        return str(FEATURE_TYPE[self.type][1])

    def __unicode__(self):
        return self.image.title + " - " + str(FEATURE_TYPE[self.type][1])


class LightBox(models.Model):
    name = models.CharField(max_length=35)
    user = models.ForeignKey(Customer)
    images = models.ManyToManyField(Photo)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'light boxes'


class Configuration(models.Model):
    name = models.CharField(blank=False, max_length=200)
    document = models.TextField(blank=False)

    def __unicode__(self):
        return self.name

    @classmethod
    def set_pref(cls, key, value):
        cls.objects.filter(name=key).delete()
        conf = cls(name=key)
        conf.document = json.dumps({"value": value})
        conf.save()
        return conf

    @classmethod
    def get_pref(cls, key):
        try:
            config = Configuration.objects.get(name=key)
        except Configuration.DoesNotExist:
            config = None
        try:
            return str(json.loads(config.document)['value'])
        except AttributeError:
            return None