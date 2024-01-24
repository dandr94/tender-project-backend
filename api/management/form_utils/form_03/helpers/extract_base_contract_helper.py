from ....form_utils.base_helper import BaseHelper


class BaseContractHelper(BaseHelper):
    def __init__(self):
        super().__init__()

    def get_base_contract_uri_doc(self, obj):
        uri_doc = self.find_element(obj, 'URI_DOC')

        return uri_doc.text

    def get_base_contract_date_publish(self, obj):
        date_publish = self.find_element(obj, 'DATE_PUB')

        date_published_fixed = self.fix_date_publish(date_publish.text)

        return date_published_fixed

    def get_translated_short_title_in_english(self, obj):
        translated_title = self.find_element(obj, "ML_TI_DOC[@LG='EN']")

        translated_title_text = self.find_element(translated_title, 'TI_TEXT')

        translated_title_text_p = self.find_element(translated_title_text, 'P')

        return translated_title_text_p.text

    def get_base_contract_original_cpv(self, obj):
        original_cpv = self.find_all_elements(obj, 'ORIGINAL_CPV')

        return original_cpv

    def get_base_contract_nc_contract_nature(self, obj):
        nc_contract_nature = self.find_element(obj, 'NC_CONTRACT_NATURE')

        return nc_contract_nature.text

