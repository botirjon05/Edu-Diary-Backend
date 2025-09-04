from django.db import models

class Subject(models.Model):
    code = models.CharField(max_length = 10, unique = True)  # MS for Math
    name = models.CharField(max_length = 100)                # Mathematics
    color = models.CharField(max_length = 7, blank = True, null = True)  # #22c55e
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"{self.code} - {self.name}"