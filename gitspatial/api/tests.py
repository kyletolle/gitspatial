import json

from django.test import TestCase
from django.test.client import Client

from .exceptions import InvalidSpatialParameterException
from .helpers import query_args


class APIRequestTest(TestCase):
    fixtures = ['gitspatial/fixtures/test_data.json']

    def setUp(self):
        self.client = Client()

    def test_bbox(self):
        response = self.client.get('/api/v1/JasonSanford/mecklenburg-gis-opendata/data/colleges.geojson?bbox=-80.888,35.206,-80.799,35.270')
        self.assertEqual(response.status_code, 200)
        json_content = json.loads(response.content)
        self.assertEqual(len(json_content['features']), 7)

    def test_all_features(self):
        response = self.client.get('/api/v1/JasonSanford/mecklenburg-gis-opendata/data/colleges.geojson')
        self.assertEqual(response.status_code, 200)
        json_content = json.loads(response.content)
        self.assertEqual(len(json_content['features']), 26)

    def test_bbox_too_many_coords(self):
        response = self.client.get('/api/v1/JasonSanford/mecklenburg-gis-opendata/data/colleges.geojson?bbox=-80.888,35.206,-80.799,35.270,99')
        self.assertEqual(response.status_code, 400)
        json_content = json.loads(response.content)
        expected = {
            'status': 'error',
            'message': 'The bbox parameter must contain 4 items: xmin, ymin, xmax, ymax'
        }
        self.assertEqual(json_content, expected)

    def test_bbox_non_floatable(self):
        response = self.client.get('/api/v1/JasonSanford/mecklenburg-gis-opendata/data/colleges.geojson?bbox=lobster,4,cat,8')
        self.assertEqual(response.status_code, 400)
        json_content = json.loads(response.content)
        expected = {
            'status': 'error',
            'message': 'Items in the bbox parameter must be parseable as floats'
        }
        self.assertEqual(json_content, expected)


# Query Prameters
class BBoxTest(TestCase):
    def setUp(self):
        pass

    def test_3_items(self):
        exc = None
        try:
            query_args.by_bbox('1,2,3')
        except Exception as exc:
            pass
        self.assertTrue(isinstance(exc, InvalidSpatialParameterException))
        self.assertEqual(str(exc), 'The bbox parameter must contain 4 items: xmin, ymin, xmax, ymax')

    def test_non_floatable(self):
        exc = None
        try:
            query_args.by_bbox('1,2,3,lobster')
        except Exception as exc:
            pass
        self.assertTrue(isinstance(exc, InvalidSpatialParameterException))
        self.assertEqual(str(exc), 'Items in the bbox parameter must be parseable as floats')
