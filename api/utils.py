def dissect_layer_path(path):
    layer_attrs_list = path.split('/')
    layer_object = {
        'type': layer_attrs_list[2],  # colours, whites
        'horse_type': layer_attrs_list[3],  # mares, stallions, foals
        'body_part': layer_attrs_list[4],  # body, mane, tail
        'size': layer_attrs_list[5],  # small, medium, large
        'id': layer_attrs_list[6].strip('.png'),
    }
    return layer_object

# we use this static data with the "white patterns" and "untestable" dropdown
# options on the front page to supplement the specific genes being unavailable
# to the server
white_pattern_reserves = {
    'brabant_horse': {
        'RN': {
            'stallion': {'body': '8d15e5f79', 'mane': '8d15e5f73', 'tail': '8d15e5f76'},
            'mare': {'body': '6c109d3c3', 'mane': '6c109d3c9', 'tail': '8d15e5f72'}
        }
    },
    'brumby_horse': {
        'TO': {
            'stallion': {'body': '87ae89518', 'mane': '2283c7754', 'tail': '2283c7752'},
            'mare': {'body': '87ae89519', 'mane': '87ae89513', 'tail': '87ae89513'}
        },
        'TO/TO': {
            'stallion': {'body': 'a9838c809', 'mane': 'ec314e433', 'tail': 'ec314e430'},
            'mare': {'body': 'a9838c809', 'mane': 'a9838c800', 'tail': 'a9838c803'}
        },
        'RN': {
            'stallion': {'body': 'a7587fba7'},
            'mare': {'body': 'a7587fba6'}
        }
    },
    'finnhorse': {
        'SW1': {
            'stallion': {},
            'mare': {}
        },
        'SW1/SW1': {
            'stallion': {'body': '32ecb3064'},
            'mare': {'body': '32ecb3064'}
        },
        'RN': {
            'stallion': {'body': '26a086ea0'},
            'mare': {'body': '26a086ea0'}
        },
        'rab/rab': {
            'stallion': {},
            'mare': {}
        }
    },
    'irish_cob_horse': {
        'RN': {
            'stallion': {'body': 'd74290788'},
            'mare': {'body': '898b23378'}
        },
        'TO': {
            'stallion': {'body': 'aa550c7f6', 'mane': 'b0712e883'},
            'mare': {'body': '8186dfa76', 'mane': '8186dfa79'}
        },
        'TO/TO': {
            'stallion': {'body': '834abce16', 'mane': '834abce19', 'tail': '1a6605788'},
            'mare': {'body': '6ed080ad8', 'mane': '6ed080ad8', 'tail': '6ed080ad0'}
        }
    },
    'mustang_horse': {
        'RN': {
            'stallion': {'body': '2cad41e96'},
            'mare': {'body': 'cb6b977c2'}
        },
        'TO': {
            'stallion': {'body': '5a7a79a49', 'mane': '5a7a79a43', 'tail': '391f20f96'},
            'mare': {'body': '8b957b629', 'mane': '11b825733', 'tail': '11b825733'}
        },
        'TO/TO': {
            # this is copied from TO because there is no dedicated art for homozygous tobiano
            'stallion': {'body': '5a7a79a49', 'mane': '5a7a79a43', 'tail': '391f20f96'},
            'mare': {'body': '8b957b629', 'mane': '11b825733', 'tail': '11b825733'}
        },
        'OLW': {
            'stallion': {'body': '46f9c2e48'},
            'mare': {'body': '360701d11'}
        },
        'OLW TO': {
            'stallion': {'body': '0cee1abc6', 'mane': '2fa1049d7'},
            'mare': {'body': 'a6ed4dc95', 'mane': '9890c3654'}
        }
    },
    'trakehner_horse': {
        'RN': {
            'stallion': {'body': '567692d74'},
            'mare': {'body': '4ce789df8'}
        },
        'SW1': {
            'stallion': {'body': 'fb5bbfe85'},
            'mare': {'body': '877293bc7'}
        },
        'TO': {
            'stallion': {'body': 'b0b1e6256', 'mane': 'b0b1e6253'},
            'mare': {'body': 'b0b1e6256', 'mane': 'b0b1e6259'}
        },
        'TO/TO': {
            'stallion': {'body': '97b7ab377', 'mane': '165ae46f1', 'tail': '165ae46f3'},
            'mare': {'body': '774c49666', 'mane': '774c49668', 'tail': '774c49663'}
        },
        'SW1 TO': {
            'stallion': {'body': 'dea811554', 'mane': 'dea811551', 'tail': 'dea811553'},
            'mare': {'body': '96e7b1a27', 'mane': '5c242e864', 'tail': '5c242e861'}
        },
        'SW1/SW1 TO': {
            'stallion': {'body': '90c425889', 'mane': 'ae30207d6', 'tail': 'ae30207d0'},
            'mare': {'body': '73bc49b66', 'tail': '73bc49b68'}
        },
        'SW1 TO/TO': {
            'stallion': {'body': '574a81ce9', 'mane': 'cc01deab4', 'tail': 'cc01deab3'},
            'mare': {'body': 'fe7cbfbd9', 'mane': 'fe7cbfbd0', 'tail': 'fe7cbfbd1'}
        }
    },
    'pura_raza_española': {
        'rab/rab': {
            'stallion': {'body': 'f98ca9b17', 'tail': 'f98ca9b14'},
            'mare': {'body': '3241ceab2', 'tail': '6984ca066'}
        }
    },
    'quarter_horse': {
        'RN': {
            'stallion': {'body': '44a433404'},
            'mare': {'body': '55b4ff4f3'}
        },
        'OLW': {
            'stallion': {'body': 'e22ca4c15'},
            'mare': {'body': '61fdd1e05'}
        },
        'SW1': {
            'stallion': {'body': 'b55401246'},
            'mare': {'body': '77225a284'}
        },
        'rab/rab': {
            'stallion': {'body': 'f12098f51', 'tail': 'f12098f52'},
            'mare': {'body': '385ce9101', 'tail': 'f12098f52'}
        },
        'OLW SW1/SW1': {
            'stallion': {'body': '8ac298a82'},
            'mare': {'body': '4662d5105'}
        },
        'OLW SW1': {
            'stallion': {'body': 'e22ca4c15'},
            'mare': {'body': '3ac840219'}
        }
    },
    'shire': {
        'sab2/sab2': {
            'stallion': {'body': '56c627016'},
            'mare': {'body': '1a300d2b0'}
        }
    },
    'thoroughbred': {
        'RN': {
            'stallion': {'body': '4c8cc7416'},
            'mare': {'body': '87d766949'}
        },
        'OLW': {
            'stallion': {'body': 'ec8b59391', 'mane': 'ec8b59396'},
            'mare': {'body': 'c06b3d2c7', 'mane': 'c06b3d2c5'}
        }
    }
}

# dutch server support
key_translations = {
    'chipnummer': 'lifenumber',
    'ras': 'breed',
    'leeftijd': 'age',
    'geb._datum': 'birthdate',
    'schofthoogte': 'horse_height',
    'locatie': 'location',
    'eigenaar': 'owner',
    'stamboek': 'registry',
    'predikaten': 'predicates'
}

breed_translations = {
    'Arabisch Volbloed': 'Arabian Horse',
    'Belgisch Trekpaard': 'Brabant Horse',
    'Brumby': 'Brumby Horse',
    'Camargue': 'Camargue Horse',
    'Cleveland Bay': 'Cleveland Bay Horse',
    'Engels Volbloed': 'Thoroughbred',
    'Fins Paarde': 'Finnhorse',
    'Fjord': 'Fjord Horse',
    'Fries': 'Friesian Horse',
    'Haflinger': 'Haflinger Horse',
    'IJslander': 'Icelandic Horse',
    'Kladruber': 'Kladruber Horse',
    'Knabstrupper': 'Knabstrupper Horse',
    'Lusitano': 'Lusitano Horse',
    'Noriker': 'Noriker Horse',
    'Normandische Cob': 'Norman Cob',
    'Oldenburger': 'Oldenburg Horse',
    'Shire': 'Shire Horse',
    'Tinker': 'Irish Cob',
    'Trakehner': 'Trakehner Horse'
}
