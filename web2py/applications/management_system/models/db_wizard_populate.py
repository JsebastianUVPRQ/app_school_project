from gluon.contrib.populate import populate
if db(db.auth_user).isempty():
     populate(db.auth_user,10)
     populate(db.t_salones,10)
     populate(db.t_estudiantes,10)
     populate(db.t_materias,10)
     populate(db.t_notas,10)
