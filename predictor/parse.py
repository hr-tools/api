import csv
import json
from io import StringIO

config = json.load(open('config.json'))
sheets_dir = config.get('sheets', 'sheets')

IGNORE_VALUES = ('X', 'x', '')

class SheetParser:
    orders = {
        'akhal_teke': {
            'stallion': ['tail', 'mane', 'body'],
            'mare': ['mane', 'body', 'tail']
        },
        'arabian_horse': {
            'stallion': ['tail', 'body', 'mane'],
            'mare': ['body', 'tail', 'mane']
        },
        'brabant_horse': {
            'stallion': ['body', 'tail', 'mane'],
            'mare': ['body', 'tail', 'mane']
        },
        'brumby_horse': {
            'stallion': ['tail', 'body', 'mane'],
            'mare': ['tail', 'body', 'mane']
        },
        'camargue_horse': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['body', 'mane', 'tail']
        },
        'cleveland_bay': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['body', 'mane', 'tail']
        },
        'exmoor_pony': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['tail', 'body', 'mane']
        },
        'finnhorse': {
            'stallion': ['tail', 'body', 'mane'],
            'mare': ['tail', 'body', 'mane']
        },
        'fjord_horse': {
            'stallion': ['body', 'tail', 'mane'],
            'mare': ['body', 'tail', 'mane']
        },
        'friesian_horse': {
            'stallion': ['tail', 'body', 'mane'],
            'mare': ['tail', 'body', 'mane']
        },
        'haflinger_horse': {
            'stallion': ['tail', 'body', 'mane'],
            'mare': ['tail', 'body', 'mane']
        },
        'icelandic_horse': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['body', 'mane', 'tail']
        },
        'irish_cob_horse': {
            'stallion': ['tail', 'body', 'mane'],
            'mare': ['tail', 'body', 'mane']
        },
        'kladruber_horse': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['body', 'mane', 'tail']
        },
        'knabstrupper': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['body', 'mane', 'tail']
        },
        'lusitano': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['tail', 'body', 'mane']
        },
        'mustang_horse': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['body', 'mane', 'tail']
        },
        'namib_desert_horse': {
            'stallion': ['tail', 'body', 'mane'],
            'mare': ['tail', 'body', 'mane']
        },
        'noriker_horse': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['body', 'mane', 'tail']
        },
        'norman_cob': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['body', 'mane', 'tail']
        },
        'oldenburg_horse': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['body', 'mane', 'tail']
        },
        'pura_raza_española': {
            'stallion': ['tail', 'body', 'mane'],
            'mare': ['tail', 'body', 'mane']
        },
        'quarter_horse': {
            'stallion': ['tail', 'body', 'mane'],
            'mare': ['body', 'mane', 'tail']
        },
        'shire_horse': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['body', 'mane', 'tail']
        },
        'suffolk_punch': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['body', 'mane', 'tail']
        },
        'thoroughbred': {
            'stallion': ['tail', 'body', 'mane'],
            'mare': ['tail', 'body', 'mane']
        },
        'trakehner_horse': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['body', 'mane', 'tail']
        },
        'welsh_pony': {
            'stallion': ['body', 'mane', 'tail'],
            'mare': ['body', 'mane', 'tail']
        }
    }
    def __init__(self):
        self.next_row_block_index = 2
        self.current_layer_block = []
        self.current_layer = {}

    def parse(self, breed=None, *, raw=None):
        all_rows = []
        if breed:
            sheet_csv = open(f'{sheets_dir}/{breed}.csv')
        elif raw:
            sheet_csv = StringIO(raw)
        else:
            raise ValueError(f'One of breed, raw must be specified.')

        for row in csv.reader(sheet_csv):
            all_rows.append(row)

        layers = []
        white_layers = []
        testable_white_layers = []
        def walk_column_whites():
            if self.next_row_block_index >= len(all_rows) - 1:
                return

            for row in all_rows[self.next_row_block_index:]:
                layer = {}
                layer['body_part'] = row[1].lower()
                if layer['body_part'] == 'color':
                    continue

                if row[0].lower() == 'testable white patterns':
                    self.next_row_block_index += 2
                    self.current_layer.clear()
                    self.current_layer_block.clear()
                    walk_column_testable_whites()
                    return

                # layer IDs
                if row[2] in IGNORE_VALUES: row[2] = None
                layer['stallion_id'] = row[2]

                if row[3] in IGNORE_VALUES: row[3] = None
                layer['mare_id'] = row[3]

                if row[4] in IGNORE_VALUES: row[4] = None
                layer['foal_id'] = row[4]

                if row[5] in IGNORE_VALUES: row[5] = None
                layer['roan'] = row[5]

                if row[6] in IGNORE_VALUES: row[6] = None
                layer['rab'] = row[6]

                if row[7] in IGNORE_VALUES: row[7] = None
                layer['roan_rab'] = row[7]

                reg_layer = layer.copy()
                reg_layer['roan'] = False
                reg_layer['rab'] = False
                reg_layer['roan_rab'] = False
                white_layers.append(reg_layer)

                if layer.get('roan'):
                    roan_layer = layer.copy()
                    roan_layer['foal_id'] = roan_layer['roan']
                    roan_layer['roan'] = True
                    roan_layer['rab'] = False
                    white_layers.append(roan_layer)

                if layer.get('rab'):
                    rab_layer = layer.copy()
                    rab_layer['foal_id'] = rab_layer['rab']
                    rab_layer['roan'] = False
                    rab_layer['rab'] = True
                    white_layers.append(rab_layer)

                if layer.get('roan_rab'):
                    roan_rab_layer = layer.copy()
                    roan_rab_layer['foal_id'] = roan_rab_layer['roan_rab']
                    roan_rab_layer['roan'] = True
                    roan_rab_layer['rab'] = True
                    white_layers.append(roan_rab_layer)

                self.next_row_block_index += 1

        def walk_column_testable_whites():
            if self.next_row_block_index >= len(all_rows) - 1:
                return

            for row in all_rows[self.next_row_block_index:]:
                if row[1].lower() == 'color':
                    if (color := row[2]) == '-':
                        color = None
                    else:
                        color = color.strip()  # sometimes they have trailing spaces

                    for obj in self.current_layer_block:
                        if not obj.get('color'):
                            obj['color'] = color

                    self.next_row_block_index += 3
                    for item in self.current_layer_block:
                        testable_white_layers.append(item.copy())

                    self.current_layer_block.clear()

                else:
                    if row[0]:
                        self.current_layer['white_gene'] = row[0]
                    else:
                        try:
                            self.current_layer['white_gene'] = self.current_layer_block[0]['white_gene']
                        except IndexError:
                            self.current_layer['white_gene'] = None

                    self.current_layer['body_part'] = row[1].lower()

                    try:
                        row[2]
                    except IndexError:
                        break

                    # layer IDs
                    if row[2] in IGNORE_VALUES: row[2] = None
                    self.current_layer['stallion_id'] = row[2]

                    if row[3] in IGNORE_VALUES: row[3] = None
                    self.current_layer['mare_id'] = row[3]

                    if row[4] in IGNORE_VALUES: row[4] = None
                    self.current_layer['foal_id'] = row[4]

                    if row[5] in IGNORE_VALUES: row[5] = None
                    self.current_layer['roan'] = row[5]

                    if row[6] in IGNORE_VALUES: row[6] = None
                    self.current_layer['rab'] = row[6]

                    if row[7] in IGNORE_VALUES: row[7] = None
                    self.current_layer['roan_rab'] = row[7]

                    reg_layer = self.current_layer.copy()
                    reg_layer['roan'] = False
                    reg_layer['rab'] = False
                    reg_layer['roan_rab'] = False
                    self.current_layer_block.append(reg_layer)

                    if self.current_layer.get('roan'):
                        roan_layer = self.current_layer.copy()
                        roan_layer['foal_id'] = roan_layer['roan']
                        roan_layer['roan'] = True
                        roan_layer['rab'] = False
                        self.current_layer_block.append(roan_layer)

                    if self.current_layer.get('rab'):
                        rab_layer = self.current_layer.copy()
                        rab_layer['foal_id'] = rab_layer['rab']
                        rab_layer['roan'] = False
                        rab_layer['rab'] = True
                        self.current_layer_block.append(rab_layer)

                    if self.current_layer.get('roan_rab'):
                        roan_rab_layer = self.current_layer.copy()
                        roan_rab_layer['foal_id'] = roan_rab_layer['roan_rab']
                        roan_rab_layer['roan'] = True
                        roan_rab_layer['rab'] = True
                        self.current_layer_block.append(roan_rab_layer)

                    #self.current_layer_block.append(self.current_layer.copy())

        def walk_column(indexes: tuple = (2, 3, 4)):
            if self.next_row_block_index >= len(all_rows) - 1:
                return

            if indexes[0] >= len(all_rows[0]):
                def get_row_count():
                    row_count = 0
                    for row in all_rows[self.next_row_block_index:]:
                        if row[1].lower() == 'color':
                            row_count += 1
                            break
                        else:
                            row_count += 1
                    return row_count

                row_count = get_row_count()
                self.next_row_block_index += row_count
                for item in self.current_layer_block:
                    layers.append(item.copy())
                self.current_layer_block.clear()
                indexes = (2, 3, 4)

            for row in all_rows[self.next_row_block_index:]:
                if row[1].lower() == 'color':
                    if (color := row[indexes[0]]) == '-':
                        color = None
                    else:
                        color = color.strip()  # sometimes they have trailing spaces

                    for obj in self.current_layer_block:
                        if not obj.get('color'):
                            obj['color'] = color

                    break

                else:
                    if row[0].lower() == 'white markings':
                        self.next_row_block_index += 2
                        self.current_layer.clear()
                        self.current_layer_block.clear()
                        walk_column_whites()
                        return

                    elif row[0].lower() == 'testable white patterns':
                        self.next_row_block_index += 1
                        self.current_layer.clear()
                        self.current_layer_block.clear()
                        walk_column_testable_whites()
                        return

                    if row[0]:
                        self.current_layer['dilution'] = row[0]
                    else:
                        try:
                            self.current_layer['dilution'] = self.current_layer_block[0]['dilution']
                        except IndexError:
                            self.current_layer['dilution'] = None

                    self.current_layer['body_part'] = row[1].lower()

                    try:
                        row[indexes[0]]
                    except IndexError:
                        break

                    # layer IDs
                    if row[indexes[0]] in IGNORE_VALUES: row[indexes[0]] = None
                    self.current_layer['stallion_id'] = row[indexes[0]]

                    if row[indexes[1]] in IGNORE_VALUES: row[indexes[1]] = None
                    self.current_layer['mare_id'] = row[indexes[1]]

                    if row[indexes[2]] in IGNORE_VALUES: row[indexes[2]] = None
                    self.current_layer['foal_id'] = row[indexes[2]]

                    self.current_layer['base_genes'] = all_rows[0][indexes[0]]
                    self.current_layer_block.append(self.current_layer.copy())

            walk_column((
                indexes[0] + 3,
                indexes[1] + 3,
                indexes[2] + 3
            ))

        walk_column()
        self.__init__()
        return {'colors': layers, 'whites': white_layers, 'testable_whites': testable_white_layers}
