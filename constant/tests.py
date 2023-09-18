from django.test import TestCase
from django.urls import reverse


# Create your tests here.
class TestCountryStateCityList(TestCase):
    def test_country_list(self):
        url = reverse("constant:country")
        response = self.client.get(url)
        # response_data = response.json()
        self.assertEquals(response.status_code, 200)

    def test_state_list(self):
        query_params = "?country_code=NG"
        url = reverse("constant:state") + query_params
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)

    def test_city_list(self):
        query_params = "?country_code=NG&state_code=OG"
        url = reverse("constant:city") + query_params
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
