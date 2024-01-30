import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import time
from django.core.management import BaseCommand
from django.db import transaction
from ..form_utils.form_03.extract_base_contract import extract_base_contract_data
from ..form_utils.form_03.extract_authority import extract_authority_contract_data
from ..form_utils.form_03.extract_object import extract_object_data
from ...models import Authority, ContractObject, Contract, Winner, Category, ContractObjectItem, BlackListDocument


def clean_official_name(name):
    cleaned_string = name.strip().lower()

    cleaned_string = cleaned_string.translate(
        str.maketrans({'.': ' ', ',': ' '}))

    cleaned_string = re.sub(r'\s+', ' ', cleaned_string)

    return cleaned_string.lower().strip()


def get_current_time() -> str:
    return time.strftime("%H:%M:%S", time.localtime())


def fix_date_publish(date):
    return datetime.strptime(date, "%Y%m%d")


def create_or_get_authority(authority_data):
    official_name = clean_official_name(authority_data.get('OFFICIALNAME'))

    defaults = {
        'address': authority_data.get('ADDRESS', ''),
        'town': authority_data.get('TOWN', ''),
        'contact_point': authority_data.get('CONTACT_POINT', ''),
        'postal_code': authority_data.get('POSTAL_CODE', ''),
        'fax': authority_data.get('FAX', ''),
        'national_id': authority_data.get('NATIONALID', ''),
        'country': authority_data.get('COUNTRY', ''),
        'phone': authority_data.get('PHONE', ''),
        'email': authority_data.get('E_MAIL', ''),
        'nuts': authority_data.get('NUTS', ''),
        'website': authority_data.get('URL_GENERAL', ''),
    }

    authority, created = Authority.objects.get_or_create(
        official_name=official_name,
        defaults=defaults
    )

    if not created:
        for field, value in defaults.items():
            current_value = getattr(authority, field)
            if current_value is not None:
                if value not in current_value:
                    setattr(authority, field, f"{current_value}, {value}")
            else:
                setattr(authority, field, value)

        authority.save()

    return authority


def create_or_get_winner(winner_data):
    official_name = clean_official_name(winner_data['CONTRACTOR_DATA'][0].get('OFFICIALNAME'))

    defaults = {
        'address': winner_data['CONTRACTOR_DATA'][0].get('ADDRESS', ''),
        'town': winner_data['CONTRACTOR_DATA'][0].get('TOWN', ''),
        'postal_code': winner_data['CONTRACTOR_DATA'][0].get('POSTAL_CODE', ''),
        'country': winner_data['CONTRACTOR_DATA'][0].get('COUNTRY', ''),
        'email': winner_data['CONTRACTOR_DATA'][0].get('E_MAIL', ''),
        'nuts': winner_data['CONTRACTOR_DATA'][0].get('NUTS', ''),
        'website': winner_data['CONTRACTOR_DATA'][0].get('URL', ''),

    }

    winner, created = Winner.objects.get_or_create(
        official_name=official_name,
        defaults=defaults
    )

    if not created:
        for field, value in defaults.items():
            current_value = getattr(winner, field)
            if current_value is not None:
                if value not in current_value:
                    setattr(winner, field, f"{current_value}, {value}")
            else:
                setattr(winner, field, value)

        winner.save()

    return winner


def create_contract_object_item(item_data, contract_object):
    winners_data = item_data.get('WINNERS', [])
    if not winners_data:
        return None

    contract_object_item = ContractObjectItem.objects.create(
        contract_object=contract_object,
        nuts_code=item_data.get('NUTS_CODE'),
        title=item_data.get('TITLE'),
        val_total=item_data.get('WINNERS')[0]['VAL_TOTAL'],
        val_total_currency=item_data.get('WINNERS')[0]['VAL_TOTAL_CURRENCY'],
        val_total_in_euros=item_data.get('WINNERS')[0]['VAL_TOTAL_IN_EUROS'],
        short_descr=item_data.get('SHORT_DESCR'),
    )

    cpv_additional = item_data.get('CPV_ADDITIONAL', [])

    if contract_object.cpv_main_code.code not in cpv_additional:
        cpv_additional.append(contract_object.cpv_main_code.code)

    for cpv_code in cpv_additional:
        cpv_category = Category.objects.get(code=cpv_code)
        contract_object_item.cpv_additional.add(cpv_category)

    # Bulk create winners???
    for winner_data in item_data.get('WINNERS', []):
        winner = create_or_get_winner(winner_data)

        val_total_in_euros = winner_data.get('VAL_TOTAL_IN_EUROS')

        winner.val_total = winner.val_total + val_total_in_euros if winner.val_total else val_total_in_euros

        winner.save()

        contract_object_item.winner.add(winner)


def create_contract_object(object_data):
    cpv_main_code = object_data.pop('cpv_main_code')
    cpv_category = Category.objects.get(code=cpv_main_code)

    return ContractObject.objects.create(
        cpv_main_code=cpv_category,
        **object_data
    )


def create_contract(base_contract_data, authority, contract_object):
    return Contract.objects.create(
        doc_id=base_contract_data.get('DATE_PUB'),
        uri=base_contract_data.get('URI_DOC_ORIGINAL'),
        date_published=base_contract_data.get('DATE_PUB'),
        short_title=base_contract_data.get('SHORT_TITLE'),
        contract_nature=base_contract_data.get('NC_CONTRACT_NATURE'),
        authority=authority,
        contract_object=contract_object,
    )


def link_original_cpv_codes(contract, original_cpv_codes):
    for cpv_code in original_cpv_codes:
        cpv_category = Category.objects.get(code=cpv_code.split(' - ')[0])
        contract.original_cpv.add(cpv_category)


def save_data_to_models(data):
    with transaction.atomic():
        authority_data = data.get('AUTHORITY_DATA', {})
        base_contract_data = data.get('BASE_CONTRACT_DATA', {})
        object_data = data.get('OBJECT_DATA', {})

        authority = create_or_get_authority(authority_data)
        contract_data_mapped = {x.lower(): y for x, y in object_data.items() if x != 'ITEMS'}
        contract_object = create_contract_object(contract_data_mapped)

        for item_id, item_data in object_data.get('ITEMS', {}).items():
            create_contract_object_item(item_data, contract_object)

        contract = create_contract(base_contract_data, authority, contract_object)

        original_cpv_codes = base_contract_data.get('ORIGINAL_CPV', [])
        link_original_cpv_codes(contract, original_cpv_codes)


class Command(BaseCommand):
    help = 'Import XML data from folder to Database'

    def handle(self, *args, **options):
        root_directory = r'C:\Users\dandr\OneDrive\Documents\xml_test_medical\F03'

        for folder_name, sub_folders, filenames in os.walk(root_directory):
            for filename in filenames:
                if filename.endswith('.xml'):
                    xml_file_path = os.path.join(folder_name, filename)

                    tree = ET.parse(xml_file_path)

                    self.stdout.write(f'[{get_current_time()}] - Working on {xml_file_path}...')

                    blacklist, created = BlackListDocument.objects.get_or_create(document_id=filename)

                    try:
                        if not created:
                            self.stdout.write(self.style.WARNING(
                                f'[{get_current_time()}] - {filename} is already processed! Continuing to next xml...'))
                            continue

                        data_dict = self.extract_data_from_xml(tree, xml_file_path)

                        save_data_to_models(data_dict)

                        self.stdout.write(self.style.SUCCESS(
                            f'[{get_current_time()}] - Successfully saved data to database from {xml_file_path}'))

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f'[{get_current_time()}] - Error processing {filename}: {e}'))
                        self.stdout.write(self.style.WARNING(
                            f'[{get_current_time()}] - Deleting {filename} from Database'))
                        blacklist.delete()

    def extract_data_from_xml(self, tree, xml_file_path):
        base_contract_data = extract_base_contract_data(tree)

        if not base_contract_data:
            self.stdout.write(self.style.ERROR(
                f'[{get_current_time()}] - Warning: No Base Contract data in {xml_file_path}! Continuing to next xml...'))
            return 0

        authority_data = extract_authority_contract_data(tree)

        if not authority_data:
            self.stdout.write(self.style.ERROR(
                f'[{get_current_time()}] - Warning: No Authority data in {xml_file_path}! Continuing to next xml...'))
            return 0

        object_data = extract_object_data(tree)

        if not object_data:
            self.stdout.write(self.style.ERROR(
                f'[{get_current_time()}] - Warning: No Object data in {xml_file_path}! Continuing to next xml...'))
            return 0

        if not object_data['ITEMS']:
            self.stdout.write(self.style.ERROR(
                f'[{get_current_time()}] - Warning: Items have no Winners in {xml_file_path}! Continuing to next xml...'))
            return 0

        data_dict = {
            'BASE_CONTRACT_DATA': base_contract_data,
            'AUTHORITY_DATA': authority_data,
            'OBJECT_DATA': object_data,
        }

        return data_dict
