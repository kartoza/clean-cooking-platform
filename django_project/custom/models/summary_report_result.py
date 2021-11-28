from django.db import models
from django.contrib.postgres.fields import JSONField
from custom.models.summary_report_category import SummaryReportCategory
from custom.models.summary_report_dataset import SummaryReportDataset


class SummaryReportResult(models.Model):

    summary_report_category = models.ForeignKey(
        SummaryReportCategory,
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    dataset_file = models.ForeignKey(
        SummaryReportDataset,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    boundary_uuid = models.CharField(
        max_length=255,
        default='',
        blank=True
    )

    analysis = models.CharField(
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
        verbose_name_plural = 'Summary Calculation Results'
        verbose_name = 'Summary Calculation Result'
