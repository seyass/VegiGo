from django.db import models
from django.contrib.auth.models import AbstractUser


class vgUser(AbstractUser):
    is_blocked = models.BooleanField(default=False)


