# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, IntegrityError
from datetime import datetime, timedelta
from django.conf import settings


class HitManager(models.Manager):
    def get_for(self, obj, bucket=None):
        if bucket is None:
            bucket_kwargs = {'bucket__isnull': True}
        else:
            bucket_kwargs = {'bucket': bucket}
        if isinstance(obj, models.Model):
            content_type = ContentType.objects.get_for_model(obj.__class__)
            object_pk = getattr(obj, obj._meta.pk.column)
            try:
                return self.get_or_create(content_type=content_type, object_pk=object_pk, **bucket_kwargs)[0]
            except IntegrityError:  # catch race condition
                return self.get(content_type=content_type, object_pk=object_pk, **bucket_kwargs)
        elif isinstance(obj, (str, unicode)):
            try:
                return self.get_or_create(content_type__isnull=True, object_pk=obj, **bucket_kwargs)[0]
            except IntegrityError:  # catch race condition
                return self.get(content_type__isnull=True, object_pk=obj, **bucket_kwargs)
        else:
            raise Exception("Don't know what to do with this obj!?")

    def hit(self, obj, user, ip, bucket=None):
        hit = self.get_for(obj, bucket=bucket)
        hit.hit(user, ip)
        return hit


class Hit(models.Model):
    content_type = models.ForeignKey(ContentType, null=True)
    object_pk = models.CharField(max_length=50)  # TextField not possible, because unique_together is needed, must be enough
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    bucket = models.CharField(max_length=50, blank=True, null=True)  # Each object may have multiple buckets hits get counted in

    views = models.PositiveIntegerField(default=0)  # page hits/views
    visits = models.PositiveIntegerField(default=0)  # unique visits

    objects = HitManager()

    def hit(self, user, ip):
        try:
            with transaction.atomic():
                if self.has_hit_from(user, ip):
                    self.update_hit_from(user, ip)
                    Hit.objects.filter(pk=self.pk).update(views=models.F('views') + 1)
                    self.views += 1
                    return True
                else:
                    self.log.create(user=user, ip=ip)
                    Hit.objects.filter(pk=self.pk).update(views=models.F('views') + 1, visits=models.F('visits') + 1)
                    self.views += 1
                    self.visits += 1
                    return True
        except IntegrityError:
            # CATCH RACE CONDITION
            # log-extry was already created
            # happens when users double-click or reload to fast
            # (we ignore this)
            return False

    def has_hit_from(self, user, ip):
        self.clear_log()
        if self.log.filter(user=user, ip=ip).count():
            return True
        else:
            return False

    def update_hit_from(self, user, ip):
        self.log.filter(user=user, ip=ip).update(when=datetime.now())

    def clear_log(self):
        timespan = datetime.now() - timedelta(days=30)
        for l in self.log.filter(when__lt=timespan).order_by('-when')[25:]:
            l.delete()

    class Meta:
        unique_together = (('content_type', 'object_pk', 'bucket'),)


class HitLog(models.Model):
    hit = models.ForeignKey(Hit, related_name='log')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='hits_log', null=True)
    ip = models.GenericIPAddressField(null=True)
    when = models.DateTimeField(default=datetime.now)

    class Meta:
        unique_together = (('hit', 'user', 'ip'),)


class HitHistory(models.Model):
    hit = models.ForeignKey(Hit, related_name='history')
    when = models.DateTimeField(default=datetime.now)

    views = models.PositiveIntegerField(default=0)
    visits = models.PositiveIntegerField(default=0)

    views_change = models.PositiveIntegerField(default=0)
    visits_change = models.PositiveIntegerField(default=0)



