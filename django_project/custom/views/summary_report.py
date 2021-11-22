import time
import os

from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.detail import DetailView

from custom.models import SummaryReportResult


def sample_raster_with_vector(summary_report_result: SummaryReportResult):

    import rasterio
    import geopandas as gpd

    start_time = time.time()
    summary_report = summary_report_result.summary_report_category

    try:
        base_file = summary_report.vector_layer.get_base_file()[0].file
    except:  # noqa
        base_file = (
            summary_report.vector_layer.upload_session.layerfile_set.all(
            ).filter(
                file__icontains='shp'
            ).first().file
        )
    vector_file = base_file.path
    raster_file = summary_report_result.raster_file.path
    raster_file_size = os.stat(raster_file).st_size

    # Read points from shapefile
    pts = gpd.read_file(vector_file)
    pts = pts[['fid', 'geometry']]
    pts.index = range(len(pts))
    coords = [(x, y) for x, y in zip(pts['geometry'].x, pts['geometry'].y)]

    # Open the raster and store metadata
    src = rasterio.open(raster_file)

    pts['Raster Value'] = [x for x in src.sample(coords)]

    sampling_data = pts[pts['Raster Value'].lt(255)]
    high_data = sampling_data[sampling_data['Raster Value'].gt(190.0)]

    if summary_report_result.result and 'raster_file_size' in summary_report_result.result:
        if summary_report_result.result['raster_file_size'] == raster_file_size:
            return summary_report_result.result

    result_data = {
        'total_features': len(pts.index),
        'total_in_raster': len(sampling_data.index),
        'total_high': len(high_data.index),
        'execution_time': time.time() - start_time,
        'raster_file_size': raster_file_size
    }
    summary_report_result.result = result_data
    summary_report_result.save()

    return result_data


class SummaryReportView(UserPassesTestMixin, DetailView):
    template_name = 'summary_report.html'
    model = SummaryReportResult

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(SummaryReportView, self).get_context_data(**kwargs)
        context['result'] = sample_raster_with_vector(self.object)
        return context
