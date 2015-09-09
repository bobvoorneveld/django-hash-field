import hashlib

from django.db import models

_hashit = lambda s: hashlib.sha1(s.encode('utf-8')).hexdigest()


class HashField(models.CharField):
    description = ('HashField is related to some other field in a model and'
        'stores its hashed value for better indexing performance.')

    def __init__(self, original, *args, **kwargs):
        '''
        :param original: name of the field storing the value to be hashed
        '''
        self.original = original
        kwargs['max_length'] = 40
        kwargs['null'] = False
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('editable', False)
        super(HashField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(HashField, self).deconstruct()
        del kwargs['max_length']
        del kwargs['null']
        del kwargs['db_index']
        del kwargs['editable']
        return name, path, args, kwargs

    def calculate_hash(self, model_instance):
        original_value = getattr(model_instance, self.original)
        setattr(model_instance, self.attname, _hashit(original_value))

    def pre_save(self, model_instance, add):
        self.calculate_hash(model_instance)
        return super(HashField, self).pre_save(model_instance, add)


class HashMixin(object):
    '''Model mixin for easy work with HashFields.'''

    def calculate_hashes(self):
        '''Calculate hashes of all the HashFields in the model.
        '''
        hashed_fields = [field for field in self._meta.fields
                         if isinstance(field, HashField)]
        for field in hashed_fields:
            field.calculate_hash(self)

    @classmethod
    def calculate_hash(cls, value):
        '''Calculate hash of the given value, which belongs to no specific
        field.
        '''
        return _hashit(value)
