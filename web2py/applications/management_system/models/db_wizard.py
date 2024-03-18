### we prepend t_ to tablenames and f_ to fieldnames for disambiguity


########################################
db.define_table('t_salones',
    Field('f_nombre_salon', type='string',
          label=T('Nombre Salon')),
    auth.signature,
    format='%(f_nombre_salon)s',
    migrate=settings.migrate)

db.define_table('t_salones_archive',db.t_salones,Field('current_record','reference t_salones',readable=False,writable=False))

########################################
db.define_table('t_estudiantes',
    Field('f_name', type='string',
          label=T('Name')),
    Field('f_birthday', type='date',
          label=T('Birthday')),
    Field('f_codigo', type='reference t_salones',
          label=T('Codigo')),
    auth.signature,
    format='%(f_name)s',
    migrate=settings.migrate)

db.define_table('t_estudiantes_archive',db.t_estudiantes,Field('current_record','reference t_estudiantes',readable=False,writable=False))

########################################
db.define_table('t_materias',
    Field('f_nombre_materia', type='string',
          label=T('Nombre Materia')),
    Field('f_codigo', type='reference t_salones',
          label=T('Codigo')),
    auth.signature,
    format='%(f_nombre_materia)s',
    migrate=settings.migrate)

db.define_table('t_materias_archive',db.t_materias,Field('current_record','reference t_materias',readable=False,writable=False))

########################################
db.define_table('t_notas',
    Field('f_calificacion', type='double',
          label=T('Calificacion')),
    Field('f_codigo', type='reference t_estudiantes',
          label=T('Codigo')),
    Field('f_codigo', type='reference t_materias',
          label=T('Codigo')),
    auth.signature,
    format='%(f_calificacion)s',
    migrate=settings.migrate)

db.define_table('t_notas_archive',db.t_notas,Field('current_record','reference t_notas',readable=False,writable=False))
