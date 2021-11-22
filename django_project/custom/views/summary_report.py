import time
import os

from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.detail import DetailView

from custom.models import ReportSummary


def sample_raster_with_vector(report_summary: ReportSummary):

    import rasterio
    import geopandas as gpd

    start_time = time.time()

    try:
        base_file = report_summary.vector_layer.get_base_file()[0].file
    except:  # noqa
        base_file = (
            report_summary.vector_layer.upload_session.layerfile_set.all(
            ).filter(
                file__icontains='shp'
            ).first().file
        )
    vector_file = base_file.path
    raster_file = report_summary.raster_file.path
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

    if report_summary.result and 'raster_file_size' in report_summary.result:
        if report_summary.result['raster_file_size'] == raster_file_size:
            return report_summary.result

    result_data = {
        'total_features': len(pts.index),
        'total_in_raster': len(sampling_data.index),
        'total_high': len(high_data.index),
        'execution_time': time.time() - start_time,
        'raster_file_size': raster_file_size
    }
    report_summary.result = result_data
    report_summary.save()

    return result_data


class SummaryReportView(UserPassesTestMixin, DetailView):
    template_name = 'summary_report.html'
    model = ReportSummary

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(SummaryReportView, self).get_context_data(**kwargs)
        context['result'] = sample_raster_with_vector(self.object)
        return context
