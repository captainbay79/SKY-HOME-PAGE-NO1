"""Presentation order for nationwide province lists; source records stay intact."""
PROVINCE_ORDER = [
    '1100000000', '4100000000', '2800000000', '5100000000',
    '3000000000', '3611000000', '4300000000', '4400000000',
    '5200000000', '1200000000', '2700000000', '4700000000',
    '2600000000', '3100000000', '4800000000', '5000000000',
]
PROVINCE_RANK = {code: index for index, code in enumerate(PROVINCE_ORDER)}

def province_sort_key(row):
    return PROVINCE_RANK.get(row[0], len(PROVINCE_ORDER))
