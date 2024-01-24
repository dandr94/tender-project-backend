from ....form_utils.base_helper import BaseHelper


class AuthorityContractHelper(BaseHelper):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_authority_contract_data(obj):
        authority_data = {}

        for element in obj.iter():
            tag = element.tag.split('}')[-1]

            if tag == 'ADDRESS_CONTRACTING_BODY':
                continue

            if tag == 'COUNTRY':
                authority_data[tag] = element.get('VALUE').strip()
            elif tag == 'NUTS':
                authority_data[tag] = element.get('CODE').strip()
            else:
                authority_data[tag] = element.text.strip()

        return authority_data
