from django.db import models
from django.contrib.auth.models import User


FEATURE_TYPE = (
    (0, 'Primary Feature'),
    (1, 'Secondary Feature (Top)'),
    (2, 'Secondary Feature (Bottom)'),
)


class Customer(models.Model):
    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.user.first_name + " " + self.user.last_name

    class Meta:
        verbose_name_plural = 'gallery'


class Gallery(models.Model):
    name = models.CharField(max_length=35)
    slug = models.SlugField(max_length=35)

    def __unicode__(self):
        return self.name

    def get_first_image(self):
        return Image.objects.filter(gallery=self).first()


class Tag(models.Model):
    tag = models.CharField(max_length=35)

    def __unicode__(self):
        return self.tag


class Image(models.Model):
    title = models.CharField(max_length=64, blank=True)
    gallery = models.ForeignKey(Gallery)
    image = models.FileField(upload_to='uploads/')
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        if self.title.strip(' ').__len__() > 0:
            return self.title
        else:
            return str(self.pk).zfill(5)


class GalleryCover(models.Model):
    gallery = models.ForeignKey(Gallery)
    cover = models.ForeignKey(Image)

    def __unicode__(self):
        return self.cover.title + " as cover for " + self.cover.gallery.name

    def gallery_covers(self):
        return self


class GalleryFeature(models.Model):
    gallery = models.ForeignKey(Gallery)
    image = models.ForeignKey(Image)
    type = models.SmallIntegerField(choices=FEATURE_TYPE)

    def __unicode__(self):
        return self.image.title + " - " + str(FEATURE_TYPE[self.type][1])


class LightBox(models.Model):
    name = models.CharField(max_length=35)
    user = models.ForeignKey(Customer)
    images = models.ManyToManyField(Image)

    def __unicode__(self):
        return self.name