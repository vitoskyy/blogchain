from api.utils import sendTransaction
from django.contrib.auth.models import User
from django.db import models
import hashlib


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    datetime = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    hash = models.CharField(max_length=64, default=None, null=True)
    txId = models.CharField(max_length=66, default=None, null=True)

    def writeOnChain(self):
        self.hash = hashlib.sha256(self.content.encode('utf-8')).hexdigest()
        self.txId = sendTransaction(self.hash)
        self.save()

    def __str__(self):
        return self.title


# La seguente classe permette di conservare gli indirizzi IP di ciascun utente
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ipAddress = models.CharField(max_length=30)

    def __str__(self):
        return self.user.username
