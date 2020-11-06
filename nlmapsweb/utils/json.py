import json

from nlmaps_tools.parse_mrl import Symbol


class SymbolAwareJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Symbol):
            return 'SYMBOL: ' + str(obj)
        return super().default(obj)
