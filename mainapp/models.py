from django.db import models


class TaskCard(models.Model):
    text = models.TextField(null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    status = models.TextField(max_length=30, default='New')
    creator = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name = 'user_creator')
    executor = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=True, blank=True, related_name = 'user_executor')

    def __str__(self) -> str:
        return f"Task {self.creator} |{self.text}|"