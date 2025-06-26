from rest_framework import serializers

from .models import Authority, Winner, Category, Contract, ContractObject, ContractObjectItem, TenderUser, Country


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderUser
        fields = ['username']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['code', 'name']


class AuthoritySerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = Authority
        fields = '__all__'


class WinnerSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = Winner
        fields = '__all__'


class CPVInfoSerializer(serializers.Serializer):
    cpv_code = serializers.CharField(source='cpv_additional__code')
    cpv_name = serializers.CharField(source='cpv_additional__name')
    val_total = serializers.FloatField()


class CPVRankingSerializer(serializers.Serializer):
    country = serializers.SerializerMethodField()

    def get_country(self, obj):
        return {
            'code': obj['contract_object__contract__authority__country__code'],
            'name': obj['contract_object__contract__authority__country__name']
        }

    val_total = serializers.FloatField()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['code', 'name']


class ContractObjectSerializer(serializers.ModelSerializer):
    cpv_main_code = CategorySerializer()

    class Meta:
        model = ContractObject
        fields = '__all__'


class ContractObjectItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractObjectItem
        fields = '__all__'


class CountryAuthoritySerializer(serializers.ModelSerializer):
    top_cpv_codes = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Authority
        fields = ['id', 'official_name', 'top_cpv_codes']


class CountryContractorSerializer(serializers.ModelSerializer):
    top_cpv_codes = CategorySerializer(many=True, read_only=True)
    total_value = serializers.DecimalField(max_digits=50, decimal_places=2, read_only=True)

    class Meta:
        model = Winner
        fields = ['id', 'official_name', 'top_cpv_codes', 'total_value']


class CountryCpvInfoSerializer(serializers.Serializer):
    cpv_additional__code = serializers.CharField()
    cpv_additional__name = serializers.CharField()
    val_total = serializers.FloatField()


class AuthorityContractSerializer(serializers.ModelSerializer):
    uri = serializers.CharField()
    short_title = serializers.CharField()
    original_cpv = CategorySerializer(many=True, read_only=True, source='original_cpv.all')
    contract_nature = serializers.CharField()
    date_published = serializers.DateField()
    contract_object_title = serializers.CharField(source='contract_object.title')
    contract_object_short_descr = serializers.CharField(source='contract_object.short_descr')
    contract_object_val_total_in_euros = serializers.FloatField(source='contract_object.val_total_in_euros')

    class Meta:
        model = Contract
        fields = [
            'id',
            'uri', 'short_title', 'original_cpv',
            'contract_nature', 'date_published',
            'contract_object_title', 'contract_object_short_descr',
            'contract_object_val_total_in_euros'
        ]


class CustomWinnerItemsSerializer(serializers.ModelSerializer):
    cpv_additional = CategorySerializer(many=True, read_only=True)
    contract_object_title = serializers.CharField(source='contract_object.title', read_only=True)
    authority_official_name = serializers.CharField(source='contract_object.contract.authority.official_name',
                                                    read_only=True)
    contract_uri = serializers.CharField(source='contract_object.contract.uri', read_only=True)
    winner = WinnerSerializer(many=True, read_only=True)

    class Meta:
        model = ContractObjectItem
        fields = [
            'id', 'title', 'short_descr', 'val_total', 'val_total_currency', 'val_total_in_euros',
            'cpv_additional', 'contract_object_title', 'authority_official_name', 'contract_uri', 'winner'
        ]
