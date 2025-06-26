from collections import defaultdict

from .helpers.extract_award_helper import AwardContractHelper

award_content_helper = AwardContractHelper()


def map_document_award_contract(tree):
    document_award_contract_dict = defaultdict(list)

    award_contracts = award_content_helper.find_all_elements(tree, 'AWARD_CONTRACT')

    for award_contract in award_contracts:

        if award_content_helper.element_exists(award_contract, 'NO_AWARDED_CONTRACT'):
            continue

        award_lot = award_content_helper.get_award_content_lot_no(award_contract)

        for lot in award_lot:
            document_award_contract_dict[lot].append(award_contract)
        else:
            document_award_contract_dict['0'].append(award_contract)

    return document_award_contract_dict


def extract_award_contract_winner_data(award_contract):
    award_lot = award_content_helper.get_award_content_lot_no(award_contract)

    award_contract_data = {'ID': award_contract.get('ITEM', 0), 'LOT_NO': award_lot if len(award_lot) > 0 else ['0']}

    award_contract_awarded_contract = award_content_helper.get_award_contract_awarded_contract(award_contract)

    award_contract_awarded_contract_contractors_el = award_content_helper.get_award_contract_awarded_contract_contractors(
        award_contract_awarded_contract)

    if award_contract_awarded_contract_contractors_el is None:
        return []

    award_contract_awarded_contract_contractors_all = award_content_helper.get_award_contract_awarded_contract_contractor_all(
        award_contract_awarded_contract_contractors_el)

    award_contract_data['CONTRACTOR_DATA'] = []

    for contractor in award_contract_awarded_contract_contractors_all:

        # Award can have VALUES or VAL_RANGE_TOTAL for writing the price of the won item
        if award_content_helper.element_exists(award_contract, 'VALUES'):
            award_contract_awarded_contract_values = award_content_helper.get_award_contract_awarded_contract_values(
                award_contract)

            if award_content_helper.element_exists(award_contract_awarded_contract_values, 'VAL_TOTAL'):
                award_contract_data['VAL_TOTAL'] = award_content_helper.get_val_total(
                    award_contract)
                award_contract_data['VAL_TOTAL_CURRENCY'] = award_content_helper.get_val_total_currency(
                    award_contract)
                award_contract_data['VAL_TOTAL_IN_EUROS'] = award_content_helper.get_val_total_in_euros(
                    award_contract_data['VAL_TOTAL_CURRENCY'],
                    award_contract_data['VAL_TOTAL'])

            elif award_content_helper.element_exists(award_contract_awarded_contract_values, 'VAL_ESTIMATED_TOTAL'):
                award_contract_data['VAL_TOTAL'] = award_content_helper.get_val_total_estimate(
                    award_contract)
                award_contract_data['VAL_TOTAL_CURRENCY'] = award_content_helper.get_val_total_estimate_currency(
                    award_contract)
                award_contract_data['VAL_TOTAL_IN_EUROS'] = award_content_helper.get_val_total_in_euros(
                    award_contract_data['VAL_TOTAL_CURRENCY'],

                    float(award_contract_data['VAL_TOTAL']))
            elif award_content_helper.element_exists(award_contract_awarded_contract_values, 'VAL_RANGE_TOTAL'):
                award_contract_awarded_contract_values_val_range_total = award_content_helper.get_award_contract_awarded_contract_values_val_range_total(
                    award_contract_awarded_contract_values)

                award_contract_data[
                    'VAL_TOTAL'] = award_content_helper.get_award_contract_awarded_contract_values_val_range_total_low(
                    award_contract_awarded_contract_values_val_range_total)

                award_contract_data['VAL_TOTAL_CURRENCY'] = award_content_helper.get_val_range_currency(
                    award_contract_awarded_contract_values_val_range_total)

                award_contract_data['VAL_TOTAL_IN_EUROS'] = award_content_helper.get_val_total_in_euros(
                    award_contract_data['VAL_TOTAL_CURRENCY'], award_contract_data['VAL_TOTAL'])
            else:
                award_contract_data['VAL_TOTAL'] = 0
                award_contract_data['VAL_TOTAL_CURRENCY'] = None
                award_contract_data['VAL_TOTAL_IN_EUROS'] = 0
        else:
            award_contract_data['VAL_TOTAL'] = 0
            award_contract_data['VAL_TOTAL_CURRENCY'] = None
            award_contract_data['VAL_TOTAL_IN_EUROS'] = 0

        contractor_data = award_content_helper.get_award_contract_awarded_contract_contractor_data_solo(
            contractor)

        if not contractor_data:
            continue

        award_contract_data['CONTRACTOR_DATA'].append(contractor_data)

    return award_contract_data
