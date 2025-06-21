from django.db import models
from authentication.models import User 

class UserMobileTests(models.Model):
    PING = 'ping'
    DNS = 'dns'
    SMS = 'sms'
    UP = 'up'
    DOWN = 'down'
    WEB = 'web'
    test_choice= (
        (PING,'ping'),
        (SMS, 'sms'),
        (DOWN , 'down'),
        (WEB, 'web'),
        (UP, 'up'),
        (DNS, 'dns')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mobile_tests")
    name = models.CharField(blank=False, null=False,max_length=6, choices=test_choice)
    timestamp = models.DateTimeField()
    test_domain = models.CharField(blank=True, null=True)
    result = models.FloatField()

