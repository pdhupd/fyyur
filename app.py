#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
import os
from flask_migrate import Migrate
from forms import *
from models import db, Venue, Artist, Show
#rom models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#----------------------------------------------------------------------------##----------------------------------------------------------------------------##----------------------------------------------------------------------------#
#  Venues
#  ----------------------------------------------------------------#----------------------------------------------------------------------------##----------------------------------------------------------------------------#

@app.route('/venues')
def venues():
  data = []
  venues = Venue.query.all()
  places = Venue.query.distinct(Venue.city, Venue.state).all()
  for place in places:
      data.append({
          'city': place.city,
          'state': place.state,
          'venues': [{
              'id': venue.id,
              'name': venue.name,
          } for venue in venues if
              venue.city == place.city and venue.state == place.state]
      })
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term','').strip()
  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  venue_list = []
  now = datetime.now()
  for venue in venues:
    venue_shows = Show.query.filter_by(venue_id = venue.id).all()
    num_upcoming_shows = 0
    for show in venue_shows:
      if show.start_time > now:
        num_upcoming_shows += 1
    venue_list.append({
      "id" : venue.id,
      "name" : venue.name,
      "num_upcoming_shows" : num_upcoming_shows
    })
  response = {
    "count": len(venues),
    "data" : venue_list
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  #venue = Venue.query.get(venue_id)


  past_shows = []
  past_shows_count = 0
  upcoming_shows = []
  upcoming_shows_count = 0
  now = datetime.now()

  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).\
    all()
  
  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).\
    all()


  data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            # Put the dashes back into phone number
            "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]),
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
            "past_shows_count": len(past_shows),
            "upcoming_shows": [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
            "upcoming_shows_count": len(upcoming_shows)
  }
  
  return render_template('pages/show_venue.html', venue=data)

#----------------------------------------------------------------------------#
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  venue = Venue()
  form.populate_obj(venue)
  if not form.validate():
    flash( form.errors )
    return render_template('pages/home.html')
  else:
    error=False
    try:
      
      db.session.add(venue)
      db.session.commit()
    except:
      print('In except venue')
      db.session.rollback()
      error=True
    finally:
      db.session.close()
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    if error:
      flash('An error occured. Venue ' + request.form['name'] + ' cannote be listed!')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # on successful db insert, flash success
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error=False
  try:
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    form.populate_obj(venue)
    db.session.commit()
  except:
    print('In except venue')
    db.session.rollback()
    error=True
  finally:
    db.session.close()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  if error:
    flash('An error occured. Venue ' + request.form['name'] + ' cannote be listed!')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  delvenue = Venue.query.get(venue_id)
  db.session.delete(delvenue)
  db.session.commit()
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#----------------------------------------------------------------------------##----------------------------------------------------------------------------##----------------------------------------------------------------------------#
# Artists.
#----------------------------------------------------------------------------##----------------------------------------------------------------------------##----------------------------------------------------------------------------#
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.order_by('id').all()
  data = []
  for artist in artists:
    data.append({
      "id" : artist.id,
      "name" : artist.name 
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term','').strip()
  artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  artist_list = []
  now = datetime.now()
  for artist in artists:
    artist_shows = Show.query.filter_by(artist_id = artist.id).all()
    num_upcoming_shows = 0
    for show in artist_shows:
      if show.start_time > now:
        num_upcoming_shows += 1
    artist_list.append({
      "id" : artist.id,
      "name" : artist.name,
      "num_upcoming_shows" : num_upcoming_shows
    })
  response = {
    "count": len(artists),
    "data" : artist_list
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  error=False
  try:
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    form.populate_obj(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
  finally:
    db.session.close()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  if error:
    flash('An error occured. Artist ' + request.form['name'] + ' cannote be listed!')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  artist = Artist()
  form.populate_obj(artist)
  if not form.validate():
    flash( form.errors )
    return render_template('pages/home.html')
  else:
    error=False
    try:
      db.session.add(artist)
      db.session.commit()
    except:
      print('In except')
      db.session.rollback()
      error=True
    finally:
      db.session.close()
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    if error:
      flash('An error occured. Artist ' + request.form['name'] + ' cannote be listed!')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # on successful db insert, flash success
    
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  print(artist)

  past_shows = []
  past_shows_count = 0
  upcoming_shows = []
  upcoming_shows_count = 0
  now = datetime.now()

  past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.artist_id == artist_id,
        Show.venue_id == Venue.id,
        Show.start_time < datetime.now()
    ).\
    all()
  
  upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.artist_id == artist_id,
        Show.venue_id == Venue.id,
        Show.start_time > datetime.now()
    ).\
    all()

  data = {
            "id": artist_id,
            "name": artist.name,
            "genres": artist.genres,
            # "address": artist.address,
            "city": artist.city,
            "state": artist.state,
            # Put the dashes back into phone number
            "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": [{
            'venue_id': venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in past_shows],
            "past_shows_count": len(past_shows),
            "upcoming_shows": [{
            'venue_id': venue.id,
            'venue_name': venue.name,
            'venue_image_link': venue.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in upcoming_shows],
            "upcoming_shows_count": len(upcoming_shows)
        }

  return render_template('pages/show_artist.html', artist=data)

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  delartist = Artist.query.get(artist_id)
  db.session.delete(delartist)
  db.session.commit()
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  ------------------------------------------------------------------------------------------------##  ------------------------------------------------------------------------------------------------#
#  Shows
#  ------------------------------------------------------------------------------------------------##  ------------------------------------------------------------------------------------------------#

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({
      "id" : show.id,
      "artist_id" : show.Artist.id,
      "venue_id" : show.Venue.id,
      "start_time" : show.start_time.strftime("%m/%d/%Y, %H:%M"),
      "artist_name" : show.Artist.name,
      "artist_image_link" : show.Artist.image_link,
      "venue_name": show.Venue.name,
    })


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  show = Show()
  form.populate_obj(show)
  if not form.validate():
    flash( form.errors )
    print('not validated')
    return render_template('pages/home.html')
  else:
    error=False
    try:
      db.session.add(show)
      db.session.commit()
      
    except:
      print('In except')
      db.session.rollback()
      error=True
    finally:
      db.session.close()
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    if error:
      flash('An error occured.')
    else:
      flash('Show  was successfully listed!')
    # on successful db insert, flash success
    #flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 8000))
#     app.run(host='0.0.0.0', port=port)

