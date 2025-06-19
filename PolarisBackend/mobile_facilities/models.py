from django.db import models
from authentication.models import User # Assuming User model is from django.contrib.auth

class UserLocationData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="location_data")  
    # Location details
    timestamp = models.DateTimeField(null=True, blank=True)  # Time of data collection
    latitude = models.DecimalField(max_digits=25, decimal_places=15)  # Latitude (e.g., 35.470540)
    longitude = models.DecimalField(max_digits=25, decimal_places=15)  # Longitude (e.g., 50.983306)
    
    plmn_id = models.IntegerField()  # PLMN Id
    lac = models.IntegerField(null=True, blank=True)  # LAC (nullable)
    rac = models.IntegerField(null=True, blank=True)  # RAC (nullable)
    tac = models.IntegerField(null=True, blank=True)  # TAC
    cell_id = models.IntegerField(null=True, blank=True)  # Cell ID
    band = models.CharField(max_length=10,null=True, blank=True)  # Band (e.g., "2147483647")
    arfcn = models.IntegerField(null=True, blank=True)  # ARFCN (Absolute Radio Frequency Channel Number)

    # Signal details (Signal Strengths)
    rsrp = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)  # RSRP (e.g., -108)
    rsrq = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)  # RSRQ (e.g., -12)
    rssi = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)  # RSSI (e.g., -77)
    rscp = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)  # RSCP (nullable)
    ec_no = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)  # Ec/No (nullable)
    rx_lev = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)  # RxLev (nullable)
    power = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    quality = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    
    # Scan information
    network_type = models.CharField(max_length=20)  # Scan Tech (e.g., "LTE (4G)")
    
    def __str__(self):
        return f"Location data at {self.timestamp}"

    def get_signal_power(self):
        # Primary Power field for 4G/5G
        if self.rsrp is not None:
            return self.rsrp
        
        # Fallback to RSSI for 2G/3G/4G
        elif self.rssi is not None:
            return self.rssi
        elif self.rscp is not None:
            return self.rscp
        
        return None  # Return None if no power information is available

    def get_signal_quality(self):
        # Primary Quality field for 4G/5G
        if self.rsrq is not None:
            return self.rsrq
        
        # Fallback to Ec/No for 3G/4G/5G
        elif self.ec_no is not None:
            return self.ec_no
        
        return None  # Return None if no quality information is available
 
        
    def get_tac_lac(self):
        return next((val for val in [self.lac, self.tac, self.rac] if val is not None), None)

    def save(self, *args, **kwargs):
        self.power = self.get_signal_power()
        self.quality = self.get_signal_quality()
        super().save(*args, **kwargs) 
    
    class Meta:
        verbose_name = "User Location Data"
        verbose_name_plural = "User Location Data"