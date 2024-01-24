from ....form_utils.base_helper import BaseHelper


class ContractObjectHelper(BaseHelper):
    def __init__(self):
        super().__init__()

    def get_object_contract_cpv_main_code(self, obj):
        object_contract_cpv_main = self.find_element(obj, 'CPV_MAIN')

        object_contract_cpv_main_code = self.find_element(object_contract_cpv_main, 'CPV_CODE')

        return object_contract_cpv_main_code.get('CODE')

    def get_object_contract_type_contract(self, obj):
        object_contract_type_contract = self.find_element(obj, 'TYPE_CONTRACT')

        return object_contract_type_contract.get('CTYPE')

    def get_object_contract_object_description_items(self, obj):
        object_contract_object_descr_items = self.find_all_elements(obj, 'OBJECT_DESCR')

        return object_contract_object_descr_items

    def get_object_contract_lot_no(self, obj):
        object_contract_lot_no = self.find_element(obj, 'LOT_NO').text

        if object_contract_lot_no.isdigit():
            return object_contract_lot_no

        lot_no = object_contract_lot_no.strip('"').lower()

        if self.element_is_allowed(lot_no):
            return lot_no

        return 0

    def get_object_contract_item_nuts_code(self, obj):
        nuts = self.find_element(obj, 'NUTS', prefix='.//n2021')

        return nuts.get('CODE')

    def get_object_contract_cpv_additional_codes(self, obj):
        cpv_additional = self.find_all_elements(obj, 'CPV_ADDITIONAL')

        return cpv_additional

    def get_contract_data_item_data(self, item):
        item_data = {'ID': item.get('ITEM')}

        if self.element_exists(item, 'TITLE'):
            item_data['TITLE'] = self.get_title(item)

        if self.element_exists(item, 'NUTS', prefix='.//n2021'):
            item_data['NUTS_CODE'] = self.get_object_contract_item_nuts_code(item)

        item_cpv_additional = self.get_object_contract_cpv_additional_codes(item)

        item_data['CPV_ADDITIONAL'] = []

        for cpv in item_cpv_additional:
            cpv_code = self.find_element(cpv, 'CPV_CODE')

            item_data['CPV_ADDITIONAL'].append(cpv_code.get('CODE'))

        if self.element_exists(item, 'SHORT_DESCR'):
            item_data['SHORT_DESCR'] = self.get_short_descr(item)

        return item_data
