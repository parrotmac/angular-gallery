from django.db import models
from django.contrib.auth.models import User


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
    user = models.ForeignKey(User)
    # Django User model includes email and first+last name

    website = models.URLField(verbose_name='Website')
    phone_number = models.CharField(max_length=40, blank=True, verbose_name='Phone Number')
    fax_number = models.CharField(max_length=40, blank=True, verbose_name='Fax Number')
    address_1 = models.CharField(max_length=128, blank=True, verbose_name='Address')
    address_2 = models.CharField(max_length=128, blank=True, verbose_name='Address, Line 2')
    city = models.CharField(max_length=30, blank=True, verbose_name='City')
    state = models.CharField(max_length=30, blank=True, verbose_name='State or Province')
    zip = models.CharField(max_length=30, blank=True, verbose_name='ZIP Code')
    country = models.CharField(max_length=128, blank=True, verbose_name='Country')

    agree_tos = models.BooleanField(default=False, blank=False)  # La la la you're gonna forget about this

    def __unicode__(self):
        return self.user


class Gallery(models.Model):
    name = models.CharField(max_length=35)
    slug = models.SlugField(max_length=35)
    active = models.BooleanField(default=False)
    cover_photo = models.ForeignKey('Photo', blank=True, related_name='gallery_cover_photo')

    def __unicode__(self):
        return self.name

    def get_first_image(self):
        return Photo.objects.filter(gallery=self).first()

    class Meta:
        verbose_name_plural = 'galleries'


class Tag(models.Model):
    tag = models.CharField(max_length=35)

    def __unicode__(self):
        return self.tag


class Photo(models.Model):
    title = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True, null=True)
    gallery = models.ManyToManyField(Gallery)
    image = models.ImageField(upload_to='uploads/')
    thumbnail = models.FileField(upload_to='uploads/thumbnails/')
    tags = models.ManyToManyField(Tag)
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


class GalleryFeature(models.Model):
    gallery = models.ForeignKey(Gallery)
    image = models.ForeignKey(Photo)
    type = models.SmallIntegerField(choices=FEATURE_TYPE)

    def __unicode__(self):
        return self.image.title + " - " + str(FEATURE_TYPE[self.type][1])


class LightBox(models.Model):
    name = models.CharField(max_length=35)
    user = models.ForeignKey(Customer)
    images = models.ManyToManyField(Photo)

    def __unicode__(self):
        return self.name