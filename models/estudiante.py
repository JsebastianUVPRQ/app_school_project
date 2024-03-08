import db
from datetime import datetime



class Estudiante (db.Model):
    __tablename__ = 'estudiante'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    edad = db.Column(db.Integer)
    grado = db.Column(db.String(100))
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    # Relaciones
    materias = db.relationship('Materia', secondary=estudiante_materia, backref=db.backref('estudiantes', lazy='dynamic'))
    # Métodos
    def __init__(self, nombre, apellido, edad, carrera, semestre, email, telefono, direccion, foto, fecha_nacimiento):
        self.nombre = nombre
        self.apellido = apellido
        self.grado = grado

    def __repr__(self):
        return '<Estudiante %r>' % self.nombre
    def serialize(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'grado': self.grado,
            'fecha_registro': self.fecha_registro
        }