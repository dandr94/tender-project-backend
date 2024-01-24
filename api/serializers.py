from rest_framework import serializers

from .models import Authority, Winner, Category, Contract, ContractObject, ContractObjectItem, TenderUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderUser
        fields = ['username']


class AuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Authority
        fields = '__all__'


class WinnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Winner
        fields = '__all__'


class CPVInfoSerializer(serializers.Serializer):
    cpv_code = serializers.CharField(source='cpv_additional__code')
    cpv_name = serializers.CharField(source='cpv_additional__name')
    val_total = serializers.FloatField()


class CPVRankingSerializer(serializers.Serializer):
    country = serializers.CharField(source='contract_object__contract__authority__country')
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


class ContractSerializer(serializers.ModelSerializer):
    contract_object = ContractObjectSerializer()

    class Meta:
        model = Contract
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Convert original_cpv IDs to a list of dictionaries containing code and name
        original_cpv_ids = representation.get('original_cpv', [])
        original_cpv_data = Category.objects.filter(id__in=original_cpv_ids)
        original_cpv_serialized = CategorySerializer(original_cpv_data, many=True).data

        representation['original_cpv'] = original_cpv_serialized

        return representation


class ContractObjectItemSerializer(serializers.ModelSerializer):
    contract_object = ContractObjectSerializer()

    class Meta:
        model = ContractObjectItem
        fields = '__all__'
