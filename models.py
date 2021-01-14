from app import db
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    #artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    #genres = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(500))

    #artists = db.relationship('Artist',secondary='Show',backref='Venue')
    shows = db.relationship('Show',backref='Venue',lazy=True)

    def __repr__(self):
        return f'<Venue : {self.id} {self.name}>'

    #past_shows_count = db.Column(db.Integer)
    #upcoming_shows_count = db.Column(db.Integer)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    #genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(500))

    #venues = db.relationship('Venue',secondary='Show', backref='Artist')
    shows = db.relationship('Show',backref='Artist',lazy=True)
    genres = db.Column(db.ARRAY(db.String))

    def __repr__(self):
        return f'<Artist : {self.id} {self.name}>'

    #past_shows = db.relationship('Venue',backref='artist',lazy=True)
    #upcoming_shows = db.relationship('Venue',backref='artist',lazy=True)
    #past_shows_count = db.Column(db.Integer)
    #upcoming_shows_count = db.Column(db.Integer)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer,primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)
  start_time = db.Column(db.DateTime(),nullable=False)
  #start_time = db.Column(db.DateTime(),nullable=False, default=datetime.utcnow)

  def __repr__(self):
    return f'<Show : {self.id}  Artist : {self.artist_id}  Venue: {self.venue_id} Start Time:{self.start_time}'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#db.create_all()