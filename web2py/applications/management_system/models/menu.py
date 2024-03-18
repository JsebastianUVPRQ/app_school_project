response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
(T('Index'),URL('default','index')==URL(),URL('default','index'),[]),
(T('Salones'),URL('default','salones_manage')==URL(),URL('default','salones_manage'),[]),
(T('Estudiantes'),URL('default','estudiantes_manage')==URL(),URL('default','estudiantes_manage'),[]),
(T('Materias'),URL('default','materias_manage')==URL(),URL('default','materias_manage'),[]),
(T('Notas'),URL('default','notas_manage')==URL(),URL('default','notas_manage'),[]),
(T('Asistencia'),URL('default','asistencia_manage')==URL(),URL('default','asistencia_manage'),[]),
]