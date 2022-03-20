from django.db import models


class Partner(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True, null=False)
    token = models.CharField(max_length=200, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return self.name


class CaptchaUsage(models.Model):
    id = models.AutoField(primary_key=True)
    partner_id = models.IntegerField(null=False)
    using_date = models.DateField(auto_now_add=True, null=False)
    using_count = models.IntegerField(default=0, null=False)
    fail_count = models.IntegerField(default=0, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    def __str__(self):
        return str(self.partner_id) + ':' + str(self.using_date) + ':' + str(self.using_count)


class CaptchaLog(models.Model):
    id = models.AutoField(primary_key=True)
    partner_id = models.IntegerField(null=False)
    decode_value = models.CharField(max_length=20, blank=True)
    status = models.IntegerField(default=0, null=False)
    image = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    train1 = models.CharField(max_length=10, default=None)
    train2 = models.CharField(max_length=10, default=None)

    def __str__(self):
        return str(self.partner_id) + ':' + str(self.decode_value) + ':' + str(self.status)
