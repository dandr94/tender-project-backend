from .helpers.extract_base_contract_helper import BaseContractHelper

base_contract_helper = BaseContractHelper()


def extract_base_contract_data(tree):
    contract_data = {
        'DATE_PUB': base_contract_helper.get_base_contract_date_publish(tree),
        'SHORT_TITLE': base_contract_helper.get_translated_short_title_in_english(tree)}

    coded_data_section = base_contract_helper.find_element(tree, 'CODED_DATA_SECTION')

    notice_data = base_contract_helper.find_element(coded_data_section, 'NOTICE_DATA')

    uri_list = base_contract_helper.find_element(notice_data, 'URI_LIST')

    contract_data['URI_DOC_ORIGINAL'] = base_contract_helper.get_base_contract_uri_doc(uri_list)
    contract_data['URI_DOC_TRANSLATED'] = base_contract_helper.convert_uri_doc_to_english(
        base_contract_helper.find_element(uri_list, 'URI_DOC'))

    original_cpv = base_contract_helper.get_base_contract_original_cpv(notice_data)

    original_cpvs = []

    for cpv in original_cpv:
        construct_cpv = base_contract_helper.construct_str_from_cvp_code_and_cpv_text(cpv)

        original_cpvs.append(construct_cpv)

    contract_data['ORIGINAL_CPV'] = original_cpvs

    codif_data = base_contract_helper.find_element(coded_data_section, 'CODIF_DATA')

    contract_data['NC_CONTRACT_NATURE'] = base_contract_helper.get_base_contract_nc_contract_nature(codif_data)

    return contract_data
