from django.db import models
from django.contrib.postgres.fields import JSONField
from custom.models.summary_report_category import SummaryReportCategory


class SummaryReportResult(models.Model):

    summary_report_category = models.ForeignKey(
        SummaryReportCategory,
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    raster_file = models.FileField(
        null=True,
        blank=True,
        upload_to="summary_raster_file/"
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        default=''
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    result = JSONField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.summary_report_category.name

    class Meta:
        verbose_name_plural = 'Summary Report Results'
