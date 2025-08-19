from django.db import models
from authentication.models import User 

class UserMobileTests(models.Model):
    PING = 'ping'
    DNS = 'dns'
    SMS = 'sms'
    UP = 'up'
    DOWN = 'download'
    WEB = 'web'
    test_choice= (
        (PING,'ping'),
        (SMS, 'sms'),
        (DOWN , 'download'),
        (WEB, 'web'),
        (UP, 'up'),
        (DNS, 'dns')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mobile_tests")
    name = models.CharField(blank=False, null=False,max_length=10, choices=test_choice)
    timestamp = models.DateTimeField()
    test_domain = models.CharField(blank=True, null=True)
    result = models.FloatField()

{'name': 'download', 'result': -1.0, 'timestamp': '2025-08-20T01:08:59'}