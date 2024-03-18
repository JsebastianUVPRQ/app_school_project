# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires
def index():
    return dict()

def error():
    return dict()

@auth.requires_login()
def salones_manage():
    form = SQLFORM.smartgrid(db.t_salones,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def estudiantes_manage():
    form = SQLFORM.smartgrid(db.t_estudiantes,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def materias_manage():
    form = SQLFORM.smartgrid(db.t_materias,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def notas_manage():
    form = SQLFORM.smartgrid(db.t_notas,onupdate=auth.archive)
    return locals()

@auth.requires_login()
def asistencia_manage():
    return dict()

