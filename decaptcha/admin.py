from django.contrib import admin
from .models import Partner, CaptchaUsage, CaptchaLog

admin.site.register([Partner, CaptchaUsage, CaptchaLog])
