from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class User(db.Model):
    __tablename__ = 'user'
    # Here we define columns for the table user
    # Notice that each column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    last_name = db.Column(db.String(80), unique=False, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    planets = db.Column(db.String(80), unique=False, nullable=True)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):                                          #defino el dictionary de mi clase para que le asigne las propiedades a mi objeto
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "password": self.password,
            "planets": self.planets  
            # do not serialize the password, its a security breach
        }
"""
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(150), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
"""
class TokenBlockedList(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    token=db.Column(db.String(200), unique=True, nullable=False)
    email=db.Column(db.String(200), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "token":self.token,
            "email":self.email,
            "created_at":self.created_at
        }


        
class People(db.Model):
    #estoy creando una clase People  
    __tablename__ = 'people'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)                                        #este tipo de dato me permite escoger en tre imagen video o galeria
    url = db.Column(db.String(250))
    
    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url
        }

class Planets(db.Model):
    #estoy creando una clase PLANETAs media que hereda el ID de mi tabla Post
    __tablename__ = 'planetas'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)                                        #este tipo de dato me permite escoger en tre imagen video o galeria
    name = db.Column(db.String(250))
    users=db.Column(db.String(250))
    
    #estoy relacionando la variable post  de la clase Post en mi clase Media.
    
    def __repr__(self):
        return '<Planets %r>' % self.name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "users": self.users         
        }

class Favorites(db.Model):
    #estoy creando una clase FAVORITOS que hereda el ID de mi tabla User y el ID de mi tabla Comment
    __tablename__ = 'favorites'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User)
    planeta_id = db.Column(db.Integer, db.ForeignKey('planetas.id'))                            #estoy indicando que mi clave post id se relaciona con la clave id de post
    planetas = db.relationship(Planets)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'))                            #estoy indicando que mi clave post id se relaciona con la clave id de post
    people = db.relationship(People)
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planeta_id": self.planeta_id,
            "people_id": self. people_id
            
        }
    