"""
Test of Flask-based web API.
"""
import logging

from flask.ext.testing import TestCase
from ruaumoko.dataset import Dataset
from ruaumoko.api import app

from .util import MOCK_DATASET_PATH, MOCK_DATASET_TILE_SIZE

LOG = logging.getLogger(__name__)

class TestAPI(TestCase):
    def create_app(self):
        # Set app configuration
        app.config['ELEVATION_DIRECTORY'] = MOCK_DATASET_PATH
        app.config['ELEVATION_TILE_RESOLUTION'] = MOCK_DATASET_TILE_SIZE
        return app

    def test_root(self):
        """Tests that the root route returns "not found"."""
        self.assert404(self.client.get('/'))

    def test_bad_lat_lng(self):
        """Tests that we must pass in valid lat/longs."""
        self.assert400(self.client.get('/a,b'))
        self.assert400(self.client.get('/a,0'))
        self.assert400(self.client.get('/0,b'))
        self.assert400(self.client.get('/-100,0'))
        self.assert400(self.client.get('/100,0'))
        self.assert400(self.client.get('/52,-32'))
        self.assert400(self.client.get('/52,374'))

    def test_good_lat_lng(self):
        """Tests that we can pass in good lat/longs and get results out which
        match calls to Dataset.get().

        """
        # Load mock dataset
        ds = Dataset(MOCK_DATASET_PATH, expected_res=MOCK_DATASET_TILE_SIZE)

        # Function to compare a response for a lat/long with what we expect
        def compare_request(lat, lng, resp):
            self.assert200(resp)
            body = resp.json
            self.assertIsNotNone(body)
            self.assertIn('elevation', body)
            elevation = body['elevation']

            # Compute "good" elevation
            good_elev = ds.get(lat, lng)

            self.assertAlmostEqual(good_elev, elevation)

        # Kick off a load of requests and compare output
        for lat in range(-85, 85, 5):
            for lng in range(1, 359, 10):
                compare_request(lat, lng, self.client.get('/{0},{1}'.format(lat,lng)))
