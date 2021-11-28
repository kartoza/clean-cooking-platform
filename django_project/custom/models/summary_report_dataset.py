from django.db import models


class SummaryReportDataset(models.Model):

    dataset_file = models.FileField(
        max_length=512,
        null=True,
        blank=True,
        upload_to='summary_raster_file/'
    )

    @staticmethod
    def get_or_create_dataset_file(boundary, dataset_file):
        import os
        created = False
        file_name = f'{boundary}/{os.path.basename(dataset_file.name)}'
        dataset = SummaryReportDataset.objects.filter(
            dataset_file__icontains=file_name
        ).first()
        if not dataset:
            dataset = SummaryReportDataset.objects.create()
            dataset.dataset_file.save(
                file_name,
                dataset_file
            )
            created = True
        return dataset, created

    def __str__(self):
        return self.dataset_file.name if self.dataset_file else self.pk

