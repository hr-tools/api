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
    'arabian_horse': {
        'rab/rab': {
            'stallion': {'body': '140cb0216', 'tail': '983ab5ca1'},
            'mare': {'body': 'e9688c125', 'tail': '39faa8b87'}
        },
        'sab2/sab2': {
            'stallion': {'body': '6a3404f05'},
            'mare': {'body': '144659b49'}
        }
    },
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
        'SW1/SW1': {
            'stallion': {'body': '32ecb3064'},
            'mare': {'body': '32ecb3064'}
        },
        'RN': {
            'stallion': {'body': '26a086ea0'},
            'mare': {'body': '26a086ea0'}
        },
        'rab/rab': {
            'stallion': {'body': '9adcd47e5', 'tail': '07b53e4e9'},
            'mare': {'body': '9adcd47e0', 'tail': '9adcd47e8'}
        },
        'SW1': {
            'stallion': {'body': 'fa616ab64'},
            'mare': {'body': 'fa616ab69'}
        },
        'SW1 rab/rab': {
            'stallion': {'body': '4d9cddaa8', 'tail': '4d9cddaa8'},
            'mare': {'body': '4d9cddaa2', 'tail': '4d9cddaa3'}
        },
        'SW1/SW1': {
            'stallion': {'body': '4b3df6d06', 'tail': '4b3df6d07'},
            'mare': {'body': '4b3df6d07', 'tail': '4b3df6d09'}
        },
        'sab2/sab2': {
            'stallion': {'body': '49d8b0b89'},
            'mare': {'body': '49d8b0b80'}
        },
        'SW1 sab2/sab2': {
            'stallion': {'body': '36808cac4'},
            'mare': {'body': '36808cac7'}
        },
        'SW1/SW1 sab2/sab2': {
            'stallion': {'body': '1d6bdb620', 'tail': '1d6bdb620'},
            'mare': {'body': '772eb1c19', 'tail': '772eb1c19'}
        }
    },
    'icelandic_horse': {
        'SW1': {
            'stallion': {'body': 'a6b777b55'},
            'mare': {'body': 'a6b777b53'}
        },
        'SW1/SW1': {
            'stallion': {'body': '84af18d19'},
            'mare': {'body': 'f9256b509'}
        },
        'RN': {
            'stallion': {'body': 'eacb73ad8'},
            'mare': {'body': 'eacb73ad8'}
        },
        'TO': {
            'stallion': {'body': 'e990c7e46', 'mane': '3bc1360f0', 'tail': '3bc1360f9'},
            'mare': {'body': 'e990c7e47', 'mane': 'e990c7e41', 'tail': 'e990c7e44'}
        },
        'TO/TO': {
            'stallion': {'body': 'e990c7e46', 'mane': '3bc1360f0', 'tail': '3bc1360f9'},
            'mare': {'body': 'e990c7e47', 'mane': 'e990c7e41', 'tail': 'e990c7e44'}
        },
        'SW1 TO': {
            'stallion': {'body': 'c2f710f85', 'mane': 'c2f710f87', 'tail': 'c2f710f82'},
            'mare': {'body': 'bf6737529', 'mane': 'c2f710f80', 'tail': 'c2f710f84'}
        },
        'SW1 TO/TO': {
            'stallion': {'body': 'c2f710f85', 'mane': 'c2f710f87', 'tail': 'c2f710f82'},
            'mare': {'body': 'bf6737529', 'mane': 'c2f710f80', 'tail': 'c2f710f84'}
        },
        'SW1/SW1 TO': {
            'stallion': {'body': 'ed41e7553', 'mane': 'ed41e7559', 'tail': 'ed41e7559'},
            'mare': {'body': '56aeac3c4', 'mane': '56aeac3c5', 'tail': '56aeac3c3'}
        },
        'SW1/SW1 TO/TO': {
            'stallion': {'body': 'ed41e7553', 'mane': 'ed41e7559', 'tail': 'ed41e7559'},
            'mare': {'body': '56aeac3c4', 'mane': '56aeac3c5', 'tail': '56aeac3c3'}
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
    'noriker_horse': {
        'RN': {
            'stallion': {'body': '25f231e53'},
            'mare': {'body': '5c51235c8'}
        },
        'TO': {
            'stallion': {'body': 'b4858d809', 'mane': 'b3acc6951', 'tail': 'f8f03d4f7'},
            'mare': {'body': '236c4be48', 'mane': '6ad2b7486', 'tail': '6ad2b7483'}
        },
        'TO/TO': {
            # this is copied from TO because there is no dedicated art for homozygous tobiano
            'stallion': {'body': 'b4858d809', 'mane': 'b3acc6951', 'tail': 'f8f03d4f7'},
            'mare': {'body': '236c4be48', 'mane': '6ad2b7486', 'tail': '6ad2b7483'}
        },
        'sab2/sab2': {
            'stallion': {'body': 'ec6b68635'},
            'mare': {'body': 'ec3f4f641'}
        }
    },
    'oldenburg_horse': {
        'TO': {
            'stallion': {'body': '46869d977', 'mane': 'ea112e255', 'tail': '9d2e56d98'},
            'mare': {'body': 'a68d8d825', 'mane': 'e14a80179', 'tail': '46869d976'}
        },
        'TO/TO': {
            # this is copied from TO because there is no dedicated art for homozygous tobiano
            'stallion': {'body': '46869d977', 'mane': 'ea112e255', 'tail': '9d2e56d98'},
            'mare': {'body': 'a68d8d825', 'mane': 'e14a80179', 'tail': '46869d976'}
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
        },
        'rab/rab': {
            'stallion': {'body': '5bd0eee21', 'tail': '5bd0eee28'},
            'mare': {'body': '3321ed288', 'tail': 'a82d6cab8'}
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
        'SW1/SW1': {
            'stallion': {'body': '01913e555'},
            'mare': {'body': 'f38df15e8'}
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
    'welsh_pony': {
        'RN': {
            'stallion': {'body': '6aabe9204'},
            'mare': {'body': '6aabe9206'}
        },
        'rab/rab': {
            'stallion': {'body': 'fc2512596', 'tail': 'fc2512599'},
            'mare': {'body': 'fc2512592', 'tail': 'fc2512591'}
        },
        'SW1': {
            'stallion': {'body': '634bf8208'},
            'mare': {'body': '634bf8202'}
        },
        'SW1/SW1': {
            'stallion': {'body': '3494da562'},
            'mare': {'body': 'd64b582b1'}
        },
        'sab2/sab2': {
            'stallion': {'body': '072d7c871'},
            'mare': {'body': '072d7c871'}
        },
        'SW1/SW1 sab2/sab2': {
            'stallion': {'body': 'a547be397'},
            'mare': {'body': '29e236050'}
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
    'Engels Volbloed': 'Thoroughbred',
    'Fins Paarde': 'Finnhorse',
    'Fjord': 'Fjord Horse',
    'Fries': 'Friesian Horse',
    'Haflinger': 'Haflinger Horse',
    'IJslander': 'Icelandic Horse',
    'Kladruber': 'Kladruber Horse',
    'Noriker': 'Noriker Horse',
    'Normandische Cob': 'Norman Cob',
    'Oldenburger': 'Oldenburg Horse',
    'Shire': 'Shire Horse',
    'Tinker': 'Irish Cob Horse',
    'Trakehner': 'Trakehner Horse'
}
