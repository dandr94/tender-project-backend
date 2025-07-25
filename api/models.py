import pycountry
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinLengthValidator
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from api.managers import TenderUserManager


class TenderUser(AbstractBaseUser, PermissionsMixin):
    USERNAME_MAX_LEN = 15
    USERNAME_MIN_LEN = 2
    USERNAME_UNIQUE_ERROR_MESSAGE = 'Username is not available'

    EMAIL_UNIQUE_ERROR_MESSAGE = 'This email is already used'

    username = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=USERNAME_MAX_LEN,
        validators=[MinLengthValidator(USERNAME_MIN_LEN)],
        error_messages={
            'unique': USERNAME_UNIQUE_ERROR_MESSAGE
        }
    )

    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
        error_messages={
            'unique': EMAIL_UNIQUE_ERROR_MESSAGE
        }

    )
    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    is_superuser = models.BooleanField(
        default=False
    )

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = TenderUserManager()


class Category(MPTTModel):
    CODE_MAX_LEN = 20
    NAME_MAX_LEN = 255

    code = models.CharField(max_length=CODE_MAX_LEN, unique=True)
    name = models.CharField(max_length=NAME_MAX_LEN)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return f'{self.code} - {self.name}'


class Country(models.Model):
    COUNTRY_CODE_MAX_LEN = 2
    COUNTRY_NAME_MAX_LEN = 255

    code = models.CharField(max_length=COUNTRY_CODE_MAX_LEN, unique=True)
    name = models.CharField(max_length=COUNTRY_NAME_MAX_LEN, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.name:
            if self.code == 'UK':
                self.name = 'United Kingdom'
            else:
                try:
                    country = pycountry.countries.get(alpha_2=self.code)
                    if country:
                        self.name = country.name
                except (AttributeError, pycountry.db.DataError):
                    pass

        super().save(*args, **kwargs)


class Authority(models.Model):
    official_name = models.TextField(unique=True)
    address = models.TextField(null=True, blank=True)
    town = models.TextField(null=True, blank=True)
    contact_point = models.TextField(null=True, blank=True)
    postal_code = models.TextField(null=True, blank=True)
    fax = models.TextField(null=True, blank=True)
    national_id = models.TextField(null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    nuts = models.TextField(null=True, blank=True)
    website = models.TextField(null=True, blank=True)


class Winner(models.Model):
    official_name = models.TextField(unique=True)
    address = models.TextField(null=True, blank=True)
    town = models.TextField(null=True, blank=True)
    postal_code = models.TextField(null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    nuts = models.TextField(null=True, blank=True)
    val_total = models.FloatField(default=0)  # in Euros
    website = models.TextField(null=True, blank=True)


class ContractObject(models.Model):
    CPV_MAIN_CODE = 10
    TYPE_CONTRACT_MAX_LEN = 50
    VAL_TOTAL_CURRENCY_MAX_LEN = 3

    cpv_main_code = models.ForeignKey(Category, on_delete=models.CASCADE)
    short_descr = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    type_contract = models.CharField(max_length=TYPE_CONTRACT_MAX_LEN, null=True, blank=True)
    val_total = models.FloatField(null=True, blank=True)
    val_total_currency = models.CharField(max_length=VAL_TOTAL_CURRENCY_MAX_LEN, null=True, blank=True)
    val_total_in_euros = models.FloatField(null=True, blank=True)
    lot_division = models.BooleanField()


class ContractObjectItem(models.Model):
    NUTS_CODE_MAX_LEN = 10
    VAL_TOTAL_MAX_LEN = 20
    VAL_TOTAL_CURRENCY_MAX_LEN = 3

    contract_object = models.ForeignKey(ContractObject, related_name='items', on_delete=models.CASCADE)
    cpv_additional = models.ManyToManyField(Category)
    nuts_code = models.CharField(max_length=NUTS_CODE_MAX_LEN, null=True, blank=True)
    short_descr = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    val_total = models.FloatField(null=True, blank=True)
    val_total_currency = models.CharField(max_length=VAL_TOTAL_CURRENCY_MAX_LEN, null=True, blank=True)
    val_total_in_euros = models.FloatField(null=True, blank=True)
    winner = models.ManyToManyField(Winner)


class Contract(models.Model):
    DOC_ID_MAX_LEN = 255
    SHORT_TITLE_MAX_LEN = 255
    CONTRACT_NATURE_MAX_LEN = 255

    CONTRACT_NATURE_CHOICES = [
        ('Services', 'Services'),
        ('Supplies', 'Supplies'),
        ('Works', 'Works'),
        ('Other', 'Other')
    ]
    doc_id = models.CharField(max_length=DOC_ID_MAX_LEN)
    uri = models.URLField()
    date_published = models.DateField()
    short_title = models.CharField(max_length=SHORT_TITLE_MAX_LEN)
    original_cpv = models.ManyToManyField(Category)
    contract_nature = models.CharField(max_length=CONTRACT_NATURE_MAX_LEN, choices=CONTRACT_NATURE_CHOICES)
    authority = models.ForeignKey(Authority, on_delete=models.CASCADE)
    contract_object = models.OneToOneField(ContractObject, on_delete=models.CASCADE)
