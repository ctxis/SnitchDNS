from twisted.names.dns import RRHeader


class Record_SNITCH(RRHeader):
    TYPE = -2024
    fancybasename = 'SNITCH_RECORD'
