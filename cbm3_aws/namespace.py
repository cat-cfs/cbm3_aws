from types import SimpleNamespace


# https://dev.to/taqkarim/extending-simplenamespace-for-nested-dictionaries-58e8
class Namespace(SimpleNamespace):
    @staticmethod
    def map_entry(entry):
        if isinstance(entry, dict):
            return Namespace(**entry)
        return entry

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, val in kwargs.items():
            if type(val) == dict:
                setattr(self, key, Namespace(**val))
            elif type(val) == list:
                setattr(self, key, list(map(self.map_entry, val)))

    def to_dict(self):
        def unpack(item):
            if isinstance(item, Namespace):
                return {k: unpack(v) for k, v in item.__dict__.items()}
            elif type(item) == list:
                return [unpack(value) for value in item]
            else:
                return item

        output = {}
        for k, v in self.__dict__.items():
            output[k] = unpack(v)
        return output

    def __contains__(self, key):
        return key in self.__dict__
