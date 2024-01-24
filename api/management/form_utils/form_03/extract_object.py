from .extract_award import extract_award_contract_winner_data, map_document_award_contract
from .helpers.extract_object_helper import ContractObjectHelper

contract_object_helper = ContractObjectHelper()


def map_document_objects(lot_division, items):
    document_objects_dict = {}

    if lot_division is False:
        document_objects_dict['0'] = items
    else:
        for item in items:
            lot_no = contract_object_helper.get_object_contract_lot_no(item)

            document_objects_dict[lot_no] = item

    return document_objects_dict


def make_relationship(document_object_dict, document_award_contract_dict):
    items = {}

    for k, v in document_object_dict.items():
        items[k] = {}

        if isinstance(v, list):
            for j in v:
                data = contract_object_helper.get_contract_data_item_data(j)
                items[k] = data

                items[k]['WINNERS'] = []

                award_contracts = document_award_contract_dict[k]

                for award_contract in award_contracts:
                    winner_data = extract_award_contract_winner_data(award_contract)

                    items[k]['WINNERS'].append(winner_data)

        else:

            data = contract_object_helper.get_contract_data_item_data(v)

            items[k] = data

            items[k]['WINNERS'] = []

            award_contracts = document_award_contract_dict[k]

            for award_contract in award_contracts:
                winner_data = extract_award_contract_winner_data(award_contract)

                items[k]['WINNERS'].append(winner_data)

    return items


def extract_object_data(tree):
    contract_data = {}

    object_contract = contract_object_helper.find_element(tree, 'OBJECT_CONTRACT')

    contract_data['TITLE'] = contract_object_helper.get_title(object_contract)

    contract_data['CPV_MAIN_CODE'] = contract_object_helper.get_object_contract_cpv_main_code(object_contract)

    if contract_object_helper.element_exists(object_contract, 'TYPE_CONTRACT'):
        contract_data['TYPE_CONTRACT'] = contract_object_helper.get_object_contract_type_contract(object_contract)

    contract_data['SHORT_DESCR'] = contract_object_helper.get_short_descr(object_contract)

    contract_data['LOT_DIVISION'] = False

    if contract_object_helper.element_exists(object_contract, 'LOT_DIVISION'):
        contract_data['LOT_DIVISION'] = True

    if contract_object_helper.element_exists(object_contract, 'VAL_TOTAL'):
        val_total = contract_object_helper.find_element(object_contract, 'VAL_TOTAL')

        contract_data['VAL_TOTAL'] = contract_object_helper.get_val_total(
            object_contract)
        contract_data['VAL_TOTAL_CURRENCY'] = contract_object_helper.get_val_total_currency(
            val_total)
        contract_data['VAL_TOTAL_IN_EUROS'] = contract_object_helper.get_val_total_in_euros(
            contract_data['VAL_TOTAL_CURRENCY'], contract_data['VAL_TOTAL'])
    else:
        contract_data['VAL_TOTAL'] = 0
        contract_data['VAL_TOTAL_CURRENCY'] = None
        contract_data['VAL_TOTAL_IN_EUROS'] = 0

    object_contract_object_descr_items = contract_object_helper.get_object_contract_object_description_items(
        object_contract)

    contract_data['ITEMS'] = {}

    document_object_dict = map_document_objects(contract_data['LOT_DIVISION'], object_contract_object_descr_items)

    document_award_contract_dict = map_document_award_contract(tree)

    items = make_relationship(document_object_dict, document_award_contract_dict)

    contract_data['ITEMS'] = items

    return contract_data
