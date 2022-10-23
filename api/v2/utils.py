from typing import Dict, List, Optional
from horsereality import Layer, LayerType


# We use this static data with the "white patterns" and "untestable" dropdown
# options in Realvision to supplement the specific genes being unavailable
# to the server
white_pattern_reserves: Dict[str, Dict[str, Dict[str, Dict[str, str]]]] = {
    'akhal_teke': {
        'rb/rb': {
            'stallion': {'body': 'ee532f869', 'tail': 'ee532f869'},
            'mare': {'body': 'b821651f9', 'tail': 'ee532f861'}
        },
        'sb/sb': {
            'stallion': {'body': 'ad686e083'},
            'mare': {'body': '45ec369a4'}
        }
    },
    'arabian_horse': {
        'rb/rb': {
            'stallion': {'body': 'd830bcf20', 'tail': 'f1e0fb655'},
            'mare': {'body': 'f1e0fb651', 'tail': 'f1e0fb657'}
        },
        'sb/sb': {
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
        'rb/rb': {
            'stallion': {'body': '9adcd47e5', 'tail': '07b53e4e9'},
            'mare': {'body': '9adcd47e0', 'tail': '9adcd47e8'}
        },
        'SW1': {
            'stallion': {'body': 'fa616ab64'},
            'mare': {'body': 'fa616ab69'}
        },
        'SW1 rb/rb': {
            'stallion': {'body': '4d9cddaa8', 'tail': '4d9cddaa8'},
            'mare': {'body': '4d9cddaa2', 'tail': '4d9cddaa3'}
        },
        'SW1/SW1': {
            'stallion': {'body': '4b3df6d06', 'tail': '4b3df6d07'},
            'mare': {'body': '4b3df6d07', 'tail': '4b3df6d09'}
        },
        'sb/sb': {
            'stallion': {'body': '49d8b0b89'},
            'mare': {'body': '49d8b0b80'}
        },
        'SW1 sb/sb': {
            'stallion': {'body': '36808cac4'},
            'mare': {'body': '36808cac7'}
        },
        'SW1/SW1 sb/sb': {
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
        'sb/sb': {
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
        'rb/rb': {
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
        'rb/rb': {
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
        'sb/sb': {
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
        'rb/rb': {
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
        'rb/rb': {
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
        'sb/sb': {
            'stallion': {'body': '072d7c871'},
            'mare': {'body': '072d7c871'}
        },
        'SW1/SW1 sb/sb': {
            'stallion': {'body': 'a547be397'},
            'mare': {'body': '29e236050'}
        }
    }
}


async def name_color(app, breed: str, layers: List[Layer]) -> Optional[Dict[str, str]]:
    # This is a very simple method that does not attempt to resolve duplicate
    # layer IDs and instead just returns the first result it finds.

    # Multiple layer IDs may be passed, but only one is usually necessary.
    # Assuming the caller is Realvision, we know that any data passed to this
    # method will be found in our database, because that is from where it was
    # retrieved.
    # However, when using data directly from Horse Reality (e.g., using Realmerge)
    # we may not already have information for it. In this case we will simply
    # give up; it is too unreliable to attempt to make inferences

    if not layers:
        raise ValueError('layers must not be empty')

    colours = [layer for layer in layers if layer.type is LayerType.colours]
    whites = [layer for layer in layers if layer.type is LayerType.whites]

    pool = app.ctx.psql_pool
    notes: List[str] = []

    if colours:
        # Prefer a body layer for the color name if available
        body_layer: Optional[Layer] = None
        try:
            body_layer = [layer for layer in colours if layer.body_part == 'body'][0]
        except IndexError:
            pass

        if body_layer:
            query = (
                '''
                SELECT dilution, base_genes, color, body_part
                FROM color_layers
                WHERE breed = $1
                AND (
                    stallion_id = $2
                    OR mare_id = $2
                    OR foal_id = $2
                )
                AND dilution IS NOT NULL
                AND color IS NOT NULL
                AND base_genes IS NOT NULL
                ''',
                breed, body_layer.id
            )
        else:
            query = (
                '''
                SELECT dilution, base_genes, color, body_part
                FROM color_layers
                WHERE breed = $1
                AND (
                    stallion_id = ANY($2::text[])
                    OR mare_id = ANY($2::text[])
                    OR foal_id = ANY($2::text[])
                )
                AND dilution IS NOT NULL
                AND color IS NOT NULL
                AND base_genes IS NOT NULL
                ''',
                breed, [layer.id for layer in colours]
            )

        colours_data_rows = await pool.fetch(*query)
        unique = set()
        for row in colours_data_rows:
            if row['body_part'] == 'body':
                # We only care about adding the note if the body layer has duplicates
                unique.add(row['color'])

        if len(unique) > 1:
            notes.append('duplicate_color_found')

        colours_data = colours_data_rows[0]
    else:
        colours_data = {}

    if whites:
        # We don't need to get untestable layers here because we don't have
        # names for them and we already have their values
        whites_data = await pool.fetchrow(
            '''
            SELECT white_gene, color, roan, rab
            FROM testable_white_layers
            WHERE breed = $1
            AND (
                stallion_id = ANY($2::text[])
                OR mare_id = ANY($2::text[])
                OR foal_id = ANY($2::text[])
            )
            AND white_gene IS NOT NULL
            AND color IS NOT NULL
            ''',
            breed, [layer.id for layer in whites]
        )
    else:
        whites_data = {}

    data: Dict[str, str] = {
        'dilution': '',
        'color': '',
        '_raw_testable_color': '',
    }

    if colours_data:
        data['dilution'] = (
            colours_data['base_genes']
            + ' '
            + (
                colours_data['dilution']
                if colours_data['dilution']
                and colours_data['dilution'].lower().strip() != 'no dilution'
                else ''
            )
        )
        data['color'] = colours_data['color']

    if whites_data:
        # We need this for referencing missing white layers in the main Vision function
        # It is never visible to users
        data['_raw_testable_color'] = whites_data['color']

        data['dilution'] += ' ' + whites_data['white_gene']

        if whites_data['color'] != 'Roan':
            data['color'] += ' ' + whites_data['color']
        if whites_data['roan']:
            data['color'] += ' Roan'
        if whites_data['rab']:
            data['color'] += ' Rabicano'
    elif whites:
        notes.append('white_layer_unmatched')

    data['dilution'] = data['dilution'].strip()
    data['color'] = data['color'].strip()

    if not data['dilution'] and not data['color']:
        # We want it to be clear that no data was found
        return None

    if '\N{PLUS-MINUS SIGN}' in data['color']:
        notes.append('shared_genotype')

    if notes:
        data['notes'] = notes

    return data
