from django.db import models
from django.contrib.auth.models import User

class FinancialItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField()
    year = models.IntegerField()
    tag = models.CharField(max_length=255, default='Misc')
    #budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Add budget field
    def __str__(self):
        return f"{self.name} - ${self.cost} - {self.month}/{self.year} - {self.tag}"
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    progress_bar = models.IntegerField(default=1, choices=[(1, '1/3'), (2, '2/3'), (3, '3/3')])
    level_number = models.IntegerField(default=1)
    progress_year = models.IntegerField(null=True, blank=True)
    progress_month = models.IntegerField(null=True, blank=True)

    def update_progress_and_level(self, latest_item):
        if latest_item and (latest_item.year != self.progress_year or latest_item.month != self.progress_month):
            if self.progress_bar < 3:
                self.progress_bar += 1
            else:
                self.progress_bar = 1
                self.level_number += 1
            self.progress_year = latest_item.year
            self.progress_month = latest_item.month
            self.save()

    def __str__(self):
        return f"{self.user.username}'s profile"

