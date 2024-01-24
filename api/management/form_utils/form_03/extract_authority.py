from .helpers.extract_authority_helper import AuthorityContractHelper

base_contract_helper = AuthorityContractHelper()


def extract_authority_contract_data(tree):
    address_contracting_body = base_contract_helper.find_element(tree, 'ADDRESS_CONTRACTING_BODY')

    if address_contracting_body is None:
        return

    authority_data = base_contract_helper.get_authority_contract_data(address_contracting_body)

    return authority_data
