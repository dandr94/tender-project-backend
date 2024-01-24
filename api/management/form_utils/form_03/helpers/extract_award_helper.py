from ....form_utils.base_helper import BaseHelper


class AwardContractHelper(BaseHelper):
    def __init__(self):
        super().__init__()

    def get_award_content_lot_no(self, obj):
        lot_no = self.find_element(obj, 'LOT_NO')

        if lot_no is not None:
            return lot_no.text.split(',')

        return []

    def get_award_contract_awarded_contract(self, obj):
        awarded_contract = self.find_element(obj, 'AWARDED_CONTRACT')

        return awarded_contract

    def get_award_contract_awarded_contract_contractors(self, obj):
        contractors = self.find_element(obj, 'CONTRACTORS')

        return contractors

    def get_award_contract_awarded_contract_contractor_all(self, obj):
        contractor_all = self.find_all_elements(obj, 'CONTRACTOR')

        return contractor_all

    def get_award_contract_awarded_contract_contractor(self, obj):
        contractor = self.find_element(obj, 'CONTRACTOR')

        return contractor

    def get_award_contract_awarded_contract_values(self, obj):
        values = self.find_element(obj, 'VALUES')

        return values

    def get_award_contract_awarded_contract_values_val_range_total(self, obj):
        val_range_total = self.find_element(obj, 'VAL_RANGE_TOTAL')

        return val_range_total

    def get_award_contract_awarded_contract_values_val_range_total_low(self, obj):
        low = self.find_element(obj, 'LOW')

        return float(low.text)

    def get_get_award_contract_awarded_contract_contractor_information(self, obj):
        pass

    def division_is_present_and_lot_no_exists(self, obj, division):
        return division and self.element_exists(obj, 'LOT_NO')

    def get_award_contract_awarded_contract_contractor_data_solo(self, obj):

        contractor_data = {}

        address_contractor_el = self.find_element(obj, 'ADDRESS_CONTRACTOR')

        for element in address_contractor_el.iter():
            tag = element.tag.split('}')[-1]

            if tag == 'ADDRESS_CONTRACTOR':
                continue
            if tag == 'COUNTRY':
                contractor_data[tag] = element.get('VALUE').strip()
            elif tag == 'NUTS':
                contractor_data[tag] = element.get('CODE').strip()
            else:
                contractor_data[tag] = element.text.strip()

        return contractor_data
