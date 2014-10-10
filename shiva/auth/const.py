# -*- coding: utf-8 -*-


class Roles:
    USER = '1'
    ADMIN = '2'
    SHIVA = '3'

    @classmethod
    def as_tuple(cls):
        return (cls.USER, cls.ADMIN, cls.SHIVA)

    @classmethod
    def as_dict(cls):
        return {
            'USER': cls.USER,
            'ADMIN': cls.ADMIN,
            'SHIVA': cls.SHIVA,
        }

    @classmethod
    def get(cls, *args, **kwargs):
        return cls.as_dict().get(*args, **kwargs)
