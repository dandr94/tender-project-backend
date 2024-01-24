from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.db.models import Count, Sum

from rest_framework import status, permissions

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Authority, Contract, ContractObjectItem, Category, ContractObject, Winner
from .serializers import AuthoritySerializer, WinnerSerializer, CPVInfoSerializer, CategorySerializer, \
    CPVRankingSerializer, ContractSerializer, UserSerializer


class HomeMapView(APIView):
    def get(self, request, *args, **kwargs):
        # Query to get country-wise contract counts
        country_data = Authority.objects.values('country').annotate(
            country_contracts=Count('contract')
        )

        # Query to get country-wise original_cpv counts with code and name
        original_cpv_counts = Contract.objects.values(
            'authority__country',
            'original_cpv__code',
            'original_cpv__name'
        ).annotate(
            original_cpv_count=Count('original_cpv')
        )

        # Structure the data as needed
        result_data = {}
        for country_item in country_data:
            country_code = country_item['country']
            country_result = {
                'country': country_code,
                'country_contracts': country_item['country_contracts'],
                'top_original_cpvs': {}
            }

            # Find original_cpv counts for the country
            cpvs_for_country = filter(lambda x: x['authority__country'] == country_code, original_cpv_counts)

            # Sort original cpvs based on counts and get the top 3
            top_original_cpvs = sorted(cpvs_for_country, key=lambda x: x['original_cpv_count'], reverse=True)[:3]

            for cpv_item in top_original_cpvs:
                cpv_key = f"{cpv_item['original_cpv__code']} - {cpv_item['original_cpv__name']}"
                country_result['top_original_cpvs'][cpv_key] = cpv_item['original_cpv_count']

            result_data[country_code] = country_result

        return JsonResponse(result_data, safe=False)


class CountryInformation(APIView):
    def get(self, request, country_code):
        try:
            total_val_euros = 0

            # Get all contracts where the authority's country equals the specified country_code
            contracts = Contract.objects.select_related('contract_object', 'authority') \
                .filter(authority__country=country_code)

            # Iterate over the contracts and sum the val_total_in_euros from the related ContractObject
            for contract in contracts:
                total_val_euros += contract.contract_object.val_total_in_euros

            data = {
                'country_flag': '???',
                'country_code': country_code,
                'total_val_in_euros': total_val_euros,
                'europe_ranking': '???'
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CountryAuthorities(APIView):
    def get(self, request, country_code):
        try:
            # Query authorities based on the country code
            authorities = Authority.objects.filter(country=country_code)

            # Serialize the data if needed
            serializer = AuthoritySerializer(authorities, many=True)

            for authority in serializer.data:
                authority_id = authority['id']

                top_cpv_codes = Contract.objects.filter(authority_id=authority_id) \
                                    .values('original_cpv__code', 'original_cpv__name') \
                                    .annotate(occurrence_count=Count('original_cpv__code')) \
                                    .order_by('-occurrence_count')[:3]
                val_total = ContractObject.objects.filter(contract__authority_id=authority_id) \
                    .aggregate(total_value=Sum('val_total_in_euros'))['total_value']

                authority['top_cpv_codes'] = top_cpv_codes
                authority['val_total'] = val_total

            return Response({'authorities': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CountryContractors(APIView):
    def get(self, request, country_code):
        try:
            # Query winners based on the country code
            contractors = Winner.objects.filter(country=country_code)

            # Serialize the data using the serializer
            serializer = WinnerSerializer(contractors, many=True)

            for contractor in serializer.data:
                contractor_id = contractor['id']

                if contractor['official_name'] == 'getinge gmbh':
                    items = ContractObjectItem.objects.filter(winner__id=contractor_id)
                    for item in items:
                        print(item.contract_object.id)
                        contract = Contract.objects.get(contract_object_id=35)
                        print(contract.uri)

                top_cpv_codes = ContractObjectItem.objects.filter(winner__id=contractor_id) \
                                    .values('cpv_additional__code', 'cpv_additional__name') \
                                    .annotate(occurrence_count=Count('cpv_additional__code')) \
                                    .order_by('-occurrence_count')[:3]

                contractor['top_cpv_codes'] = top_cpv_codes

            return Response({'contractors': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CPVInformation(APIView):
    def get(self, request, country_code):
        try:
            # Group by CPV code and calculate the total value for each group
            cpv_info = ContractObjectItem.objects.filter(contract_object__contract__authority__country=country_code) \
                .values('cpv_additional__code', 'cpv_additional__name') \
                .annotate(val_total=Sum('val_total_in_euros'))

            cpv_info = [item for item in cpv_info if item['cpv_additional__code'].startswith('33')]

            # Serialize the CPV information
            serializer = CPVInfoSerializer(cpv_info, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CPVCategories(APIView):
    def get(self, request):
        try:
            selected_cpv_code = request.GET.get('cpv_code', '')

            if selected_cpv_code:
                items_with_cpv = ContractObjectItem.objects.filter(cpv_additional__code=selected_cpv_code)

                cpv_ranking = items_with_cpv.values('contract_object__contract__authority__country') \
                    .annotate(val_total=Sum('val_total_in_euros')) \
                    .order_by('-val_total')

                serializer = CPVRankingSerializer(cpv_ranking, many=True)

                return Response({'cpv_ranking': serializer.data}, status=status.HTTP_200_OK)

            else:
                # If no CPV code is provided, return all categories starting with '33'
                cpv_categories = Category.objects.filter(code__startswith='33')
                serializer = CategorySerializer(cpv_categories, many=True)
                return Response({'cpv_categories': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WinnersList(APIView):
    def get(self, request):
        try:
            winners = Winner.objects.all()

            serializer = WinnerSerializer(winners, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AuthorityDetails(APIView):
    def get(self, request, official_name):
        try:
            # Retrieve the authority based on the official_name
            authority = Authority.objects.get(official_name=official_name)

            # Get the total number of contracts and total val_total spent by the authority
            total_contracts = Contract.objects.filter(authority=authority).count()
            val_total = \
                Contract.objects.filter(authority=authority).aggregate(Sum('contract_object__val_total_in_euros'))[
                    'contract_object__val_total_in_euros__sum']

            # Serialize the authority details along with additional information
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


class AuthorityContracts(APIView):
    def get(self, request, official_name):
        try:
            # Retrieve the authority based on the official_name
            authority = Authority.objects.get(official_name=official_name)
            # Retrieve all contracts associated with the authority
            contracts = Contract.objects.filter(authority=authority)

            # Serialize the contract details
            serializer = ContractSerializer(contracts, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Authority.DoesNotExist:
            return Response({'error': 'Authority not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WinnerDetails(APIView):
    def get(self, request, official_name):
        try:
            winner = Winner.objects.get(official_name=official_name)
            contract_object_items = ContractObjectItem.objects.filter(winner=winner)
            serializer = WinnerSerializer(winner)

            data = {
                'winner_details': serializer.data,
                'winner_contracts_overview': {'total_contracts': len(contract_object_items),
                                              'val_total': serializer.data['val_total']}
            }

            return Response(data, status=status.HTTP_200_OK)

        except Winner.DoesNotExist:
            return Response({'error': 'Winner not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WinnerObjectItems(APIView):
    def get(self, request, official_name):
        try:
            winner = Winner.objects.get(official_name=official_name)
            contract_object_items = ContractObjectItem.objects.filter(winner=winner)

            response_data = []

            for item in contract_object_items:
                contract_object = item.contract_object
                authority = contract_object.contract.authority

                data = {
                    'id': item.id,
                    "contract_object_item_title": item.title if item.title else item.short_descr,
                    "contract_object_title": contract_object.title,
                    "authority_official_name": authority.official_name,
                    'contract_uri': contract_object.contract.uri,
                    'val_total': item.val_total_in_euros,
                    'cpv_codes': [f'{cpv.code} - {cpv.name}' for cpv in item.cpv_additional.all()]

                }

                response_data.append(data)

            return Response(response_data, status=status.HTTP_200_OK)

        except Winner.DoesNotExist:
            return Response({'error': 'Winner object items not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
