from django.http import JsonResponse
from django.db.models import Count, Sum, Q

from rest_framework import status
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.pagination import PageNumberPagination

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Authority, Contract, ContractObjectItem, Category, ContractObject, Winner, Country
from .serializers import AuthoritySerializer, WinnerSerializer, CategorySerializer, CPVRankingSerializer, \
    CustomWinnerItemsSerializer, AuthorityContractSerializer, CountryAuthoritySerializer, CountryContractorSerializer, \
    CountryCpvInfoSerializer, CountrySerializer


class CustomPaginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class HomeMapView(APIView):
    def get(self, request, *args, **kwargs):
        country_data = Authority.objects.values('country').annotate(
            country_contracts=Count('contract')
        )

        original_cpv_counts = Contract.objects.values(
            'authority__country',
            'original_cpv__code',
            'original_cpv__name'
        ).annotate(
            original_cpv_count=Count('original_cpv')
        )

        result_data = {}
        for country_item in country_data:
            country_code = country_item['country']

            country_result = {
                'country': country_code,
                'country_contracts': country_item['country_contracts'],
                'top_original_cpvs': {}
            }

            cpvs_for_country = filter(lambda x: x['authority__country'] == country_code, original_cpv_counts)

            top_original_cpvs = sorted(cpvs_for_country, key=lambda x: x['original_cpv_count'], reverse=True)[:3]

            for cpv_item in top_original_cpvs:
                cpv_key = f"{cpv_item['original_cpv__code']} - {cpv_item['original_cpv__name']}"

                country_result['top_original_cpvs'][cpv_key] = cpv_item['original_cpv_count']

            result_data[country_code] = country_result

        return JsonResponse(result_data, safe=False)


class CountryInformation(APIView):
    def get(self, request, country_code):
        print(country_code)
        try:

            country = Country.objects.get(code=country_code)

            total_val_euros = Contract.objects.filter(authority__country=country) \
                                  .aggregate(total_val_euros=Sum('contract_object__val_total_in_euros'))[
                                  'total_val_euros'] or 0

            data = {
                'country_flag': '???',
                'country_code': country_code,
                'country_name': country.name,
                'total_val_in_euros': total_val_euros,
                'europe_ranking': '???'
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CountryAuthorities(ListAPIView):
    serializer_class = CountryAuthoritySerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        country_code = self.kwargs['country_code']

        return Authority.objects.filter(country__code=country_code).order_by('id')

        # RETURN ORDERED BY VALUE

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            paginated_queryset = self.paginate_queryset(queryset)

            serializer = self.get_serializer(paginated_queryset, many=True)

            for authority in serializer.data:
                authority_id = authority['id']

                top_cpv_codes = Contract.objects.filter(authority_id=authority_id) \
                                    .values('original_cpv__code', 'original_cpv__name') \
                                    .annotate(occurrence_count=Count('original_cpv__code')) \
                                    .order_by('-occurrence_count')[:3]

                total_value = ContractObject.objects.filter(contract__authority_id=authority_id) \
                    .aggregate(total_value=Sum('val_total_in_euros'))['total_value']

                authority['total_value'] = total_value

                authority['top_cpv_codes'] = top_cpv_codes

            return self.get_paginated_response(serializer.data)

        except Authority.DoesNotExist:
            return Response({'error': 'Authorities not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CountryContractors(ListAPIView):
    serializer_class = CountryContractorSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        country_code = self.kwargs['country_code']

        return Winner.objects.filter(country__code=country_code) \
            .annotate(total_value=Sum('contractobjectitem__val_total_in_euros')) \
            .order_by('-total_value')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            paginated_queryset = self.paginate_queryset(queryset)

            serializer = self.get_serializer(paginated_queryset, many=True)

            for contractor in serializer.data:
                contractor_id = contractor['id']

                top_cpv_codes = ContractObjectItem.objects.filter(winner=contractor_id) \
                                    .values('cpv_additional__code', 'cpv_additional__name') \
                                    .annotate(occurrence_count=Count('cpv_additional__code')) \
                                    .order_by('-occurrence_count')[:3]

                contractor['top_cpv_codes'] = top_cpv_codes

            return self.get_paginated_response(serializer.data)

        except Winner.DoesNotExist:
            return Response({'error': 'Contractors not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CountryCPVInformation(ListAPIView):
    serializer_class = CountryCpvInfoSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        country_code = self.kwargs['country_code']

        queryset = ContractObjectItem.objects.filter(contract_object__contract__authority__country__code=country_code)

        queryset = queryset.filter(cpv_additional__code__startswith='33')

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            cpv_info = queryset.values('cpv_additional__code', 'cpv_additional__name') \
                .annotate(val_total=Sum('val_total_in_euros')).order_by('-val_total')

            page = self.paginate_queryset(cpv_info)

            serializer = self.get_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CPVCategories(APIView):
    def get(self, request):
        try:
            cpv_categories = Category.objects.filter(code__startswith='33')

            serializer = CategorySerializer(cpv_categories, many=True)

            return Response({'cpv_categories': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CountriesList(APIView):
    def get(self, request):
        try:
            countries = Country.objects.all()

            serializer = CountrySerializer(countries, many=True)

            return Response({'countries': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CPVCountryRanking(ListAPIView):
    serializer_class = CPVRankingSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        cpv_code = self.kwargs['cpv_code']
        queryset = ContractObjectItem.objects.filter(cpv_additional__code=cpv_code)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        cpv_ranking = queryset.values('contract_object__contract__authority__country__name',
                                      'contract_object__contract__authority__country__code') \
            .annotate(val_total=Sum('val_total_in_euros')) \
            .order_by('-val_total')

        page = self.paginate_queryset(cpv_ranking)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(cpv_ranking, many=True)
        return Response(serializer.data)


class WinnersList(ListAPIView):
    queryset = Winner.objects.all().order_by('id')
    serializer_class = WinnerSerializer
    pagination_class = CustomPaginator


class AuthorityDetails(APIView):
    def get(self, request, official_name):
        try:
            authority = Authority.objects.get(official_name=official_name)

            total_contracts = Contract.objects.filter(authority=authority).count()

            val_total = \
                Contract.objects.filter(authority=authority).aggregate(Sum('contract_object__val_total_in_euros'))[
                    'contract_object__val_total_in_euros__sum']

            serializer = AuthoritySerializer(authority)

            data = {
                'authority_details': serializer.data,
                'authority_contracts_overview': {'total_contracts': total_contracts,
                                                 'val_total': val_total}
            }

            return Response(data, status=status.HTTP_200_OK)

        except Authority.DoesNotExist:
            return Response({'error': 'Authority not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AuthorityContracts(ListAPIView):
    serializer_class = AuthorityContractSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        official_name = self.kwargs['official_name']

        authority = get_object_or_404(Authority, official_name=official_name)

        return Contract.objects.filter(authority=authority).order_by('id')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            paginated_queryset = self.paginate_queryset(queryset)

            serializer = self.get_serializer(paginated_queryset, many=True)

            return self.get_paginated_response(serializer.data)

        except Authority.DoesNotExist:
            return Response({'error': 'Authority not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WinnerDetails(APIView):
    def get(self, request, official_name):
        try:
            winner = Winner.objects.get(official_name=official_name)

            contract_object_items = ContractObjectItem.objects.filter(winner=winner).count()

            serializer = WinnerSerializer(winner)

            data = {
                'winner_details': serializer.data,
                'winner_contracts_overview': {'total_contracts': contract_object_items,
                                              'val_total': serializer.data['val_total']}
            }

            return Response(data, status=status.HTTP_200_OK)

        except Winner.DoesNotExist:
            return Response({'error': 'Winner not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WinnerObjectItems(ListAPIView):
    serializer_class = CustomWinnerItemsSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        official_name = self.kwargs['official_name']

        winner = get_object_or_404(Winner, official_name=official_name)

        return ContractObjectItem.objects.filter(winner=winner).order_by('id')

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            paginated_queryset = self.paginate_queryset(queryset)

            serializer = self.get_serializer(paginated_queryset, many=True)

            return self.get_paginated_response(serializer.data)

        except Winner.DoesNotExist:
            return Response({'error': 'Winner object items not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdvancedSearchView(APIView):
    def post(self, request):
        search_criteria = request.data
        entity = search_criteria.get('authorityOrContractor')
        place_of_performance = search_criteria.get('placeOfPerformance')
        nature_of_contract = search_criteria.get('natureOfContract')
        cpv_code = search_criteria.get('cpvCode')

        if entity == 'authority':
            query = Q()

            if place_of_performance:
                query &= Q(authority__country__code=place_of_performance['code'])
            if nature_of_contract:
                query &= Q(contract_nature=nature_of_contract.capitalize())
            if cpv_code:
                query &= Q(original_cpv__code=cpv_code['code'])

            contracts = Contract.objects.filter(query)

            authorities = [contract.authority for contract in contracts]

            serialized_authorities = AuthoritySerializer(authorities, many=True)

            return Response(serialized_authorities.data)
        else:
            query = Q()

            if place_of_performance:
                query &= Q(authority__country__code=place_of_performance['code'])
            if nature_of_contract:
                query &= Q(contract_nature=nature_of_contract.capitalize())
            if cpv_code:
                query &= Q(original_cpv__code=cpv_code['code'])

            contracts = Contract.objects.filter(query)

            authorities = [contract.authority for contract in contracts]

            serialized_authorities = AuthoritySerializer(authorities, many=True)

            return Response(serialized_authorities.data)
