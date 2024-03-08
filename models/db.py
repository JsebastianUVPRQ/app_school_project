# models/db.py
import db


db.define_table('salon',
    Field('nombre', requires=IS_NOT_EMPTY()),
    # Otros campos del salón
)

db.define_table('materia',
    Field('nombre', requires=IS_NOT_EMPTY()),
    # Otros campos de la materia
)
