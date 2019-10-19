from collections import OrderedDict

TARGETS = OrderedDict([('2.5', (2, 5)),
                       ('2.6', (2, 6)),
                       ('2.7', (2, 7)),
                       ('3.0', (3, 0)),
                       ('3.1', (3, 1)),
                       ('3.2', (3, 2)),
                       ('3.3', (3, 3)),
                       ('3.4', (3, 4)),
                       ('3.5', (3, 5)),
                       ('3.6', (3, 6)),
                       ('3.7', (3, 7)),
                       ('3.8', (3, 8))])

SYNTAX_ERROR_OFFSET = 5

TARGET_ALL = next(reversed(TARGETS.values()))
