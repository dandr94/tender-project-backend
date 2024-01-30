from django.urls import path

from api.views import CountryInformation, CountryAuthorities, CountryContractors, CPVCategories, \
    AuthorityDetails, AuthorityContracts, HomeMapView, WinnerDetails, WinnerObjectItems, WinnersList, \
    CountryCPVInformation, CPVCountryRanking

urlpatterns = [
    # Index Map API
    path('home-map/', HomeMapView.as_view(), name='home_map'),

    # Country Page API
    path('country/<str:country_code>/overview/', CountryInformation.as_view(), name='country_overview'),
    path('country/<str:country_code>/authorities/', CountryAuthorities.as_view(), name='country_authorities'),
    path('country/<str:country_code>/contractors/', CountryContractors.as_view(), name='country_contractors'),
    path('country/<str:country_code>/cpv-info/', CountryCPVInformation.as_view(), name='country_cpv_information'),

    # Categories API
    path('categories/', CPVCategories.as_view(), name='categories'),
    path('contractors/', WinnersList.as_view(), name='contractors'),

    # Rankings API
    path('cpv/<str:cpv_code>/rankings', CPVCountryRanking.as_view(), name='cpv_rankings'),

    # Authority Page API
    path('authority/<str:official_name>/', AuthorityDetails.as_view(), name='authority_details'),
    path('authority/<str:official_name>/contracts/', AuthorityContracts.as_view(), name='authority_contracts'),

    # Winner Page API
    path('contractor/<str:official_name>/', WinnerDetails.as_view(), name='contractor_details'),
    path('contractor/<str:official_name>/contracts/', WinnerObjectItems.as_view(), name='winner_object_items'),
]
