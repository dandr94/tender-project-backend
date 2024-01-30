import string
from datetime import datetime


class BaseHelper:
    def __init__(self):
        self.namespace = {'ns0': 'http://publications.europa.eu/resource/schema/ted/R2.0.9/publication',
                          'n2021': 'http://publications.europa.eu/resource/schema/ted/2021/nuts',
                          'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
                          'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
                          'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
                          'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'
                          }
        # 11.01.2024 Exchange rates
        # Create DB Model to Handle this type of information
        self.exchange_rates_to_euros = {
            'ALL': 0.00962005,  # Albania,
            'AMD': 0.00224804,  # Armenia,
            'AZN': 0.535567,  # Azerbaijan
            'BYN': 0.276209,  # Belarus
            'BAM': 0.511292,  # Bosnia and Herzegovina
            'BGN': 0.511292,  # Bulgaria
            'CZK': 0.0405105,  # Czech
            'DKK': 0.134101,  # Denmark
            'GEL': 0.339732,  # Georgia
            'HUF': 0.00263746,  # Hungary
            'ISK': 0.00666226,  # Iceland
            'LI': 0.934626,  # Liechtenstein
            'MDL': 0.0512310,  # Moldova
            'MKD': 0.0162412,  # North Macedonia
            'NOK': 0.0884774,  # Norway
            'PLN': 0.229672,  # Poland
            'RON': 0.201123,  # Romania
            'RSD': 0.00853088,  # Serbia
            'SEK': 0.0888406,  # Sweden
            'CHF': 1.06992,  # Switzerland
            'TRY': 0.0302849,  # Türkiye
            'UAH': 0.0239965,  # Ukraine
            'GBP': 1.16357  # Great Kingdom of Britain
        }
        self.allowed_lots = [char.lower() for char in string.ascii_uppercase]

    def find_element(self, obj, el, prefix='.//ns0', ):
        return obj.find(f'{prefix}:{el}', namespaces=self.namespace)

    def find_all_elements(self, obj, el, prefix='.//ns0', ):
        return obj.findall(f'{prefix}:{el}', namespaces=self.namespace)

    def element_exists(self, obj, el, prefix='.//ns0'):
        return self.find_element(obj, el, prefix) is not None

    def element_is_allowed(self, el):
        return el in self.allowed_lots

    def get_title(self, obj):
        title = self.find_element(obj, 'TITLE')

        title_p = self.find_element(title, 'P')

        return title_p.text

    def get_short_descr(self, obj):
        short_description = self.find_element(obj, 'SHORT_DESCR')

        short_description_p = self.find_all_elements(short_description, 'P')

        return '\n'.join(str(p.text) for p in short_description_p)

    def check_if_object_lot_no_is_present_in_award_contract(self, tree, obj_lot_no):
        award_contract = self.find_all_elements(tree, 'AWARD_CONTRACT')

        for award in award_contract:
            lot_no = self.find_element(award, 'LOT_NO')

            if lot_no.text == obj_lot_no:
                return True

        return False

    def get_val_total(self, obj):
        val_total = self.find_element(obj, 'VAL_TOTAL')

        return float(val_total.text)

    def get_val_total_estimate(self, obj):
        val_total_estimate = self.find_element(obj, 'VAL_ESTIMATED_TOTAL')

        return float(val_total_estimate.text)

    def get_val_total_currency(self, obj):
        val_total = self.find_element(obj, 'VAL_TOTAL')

        val_total_currency = val_total.get('CURRENCY')

        return val_total_currency

    def get_val_total_estimate_currency(self, obj):
        val_total_estimate = self.find_element(obj, 'VAL_ESTIMATED_TOTAL')

        val_total_estimate_currency = val_total_estimate.get('CURRENCY')

        return val_total_estimate_currency

    def get_val_total_in_euros(self, currency, val_total):
        if currency not in self.exchange_rates_to_euros:
            return val_total

        euros = self.exchange_rates_to_euros[currency] * val_total

        return float(f"{euros:.2f}")

    @staticmethod
    def fix_date_publish(date):
        original_date = datetime.strptime(date, "%Y%m%d")

        return original_date

    @staticmethod
    def construct_str_from_cvp_code_and_cpv_text(obj):
        cpv_code = obj.get('CODE')
        cpv_text = obj.text

        return f'{cpv_code} - {cpv_text}'

    @staticmethod
    def convert_uri_doc_to_english(uri_doc):
        uri_doc_text = uri_doc.text

        uri_doc_lang = uri_doc.get('LG')

        if uri_doc_lang != 'EN':
            uri_doc_text = uri_doc_text.replace(uri_doc_lang, 'EN')

        return uri_doc_text
