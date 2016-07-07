import datetime
import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from schemas import ArtistSchema, PosterSchema, SocialSchema

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), 'paapi-db.db')
db_uri = 'sqlite:////{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##### MODELS #####
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))


class Social(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website = db.Column(db.String(180))
    instagram = db.Column(db.String(80))
    twitter = db.Column(db.String(80))
    facebook = db.Column(db.String(80))
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    artist = db.relationship("Artist", backref=db.backref("social", lazy="dynamic"))


class Poster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    year = db.Column(db.Integer)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    artist = db.relationship("Artist", backref=db.backref("posters", lazy="dynamic"))
    date_created = db.Column(db.DateTime)


artist_schema = ArtistSchema()
artists_schema = ArtistSchema(many=True)
social_schema = SocialSchema(only=('artist', 'website', 'instagram', 'twitter', 'facebook'))
poster_schema = PosterSchema()
posters_schema = PosterSchema(many=True, only=('id', 'year', 'title'))


#### API ####
@app.route('/artists')
def get_artists():
    artists = Artist.query.all()
    # serialize the dataset
    artists = artists_schema.dump(artists)
    return jsonify({
        'artists': artists.data
    })


@app.route('/artists/<int:pk>')
def get_artist(pk):
    try:
        artist = Artist.query.get(pk)
        social = Social.query.get(pk)
    except IntegrityError:
        return jsonify({
            "Error": "Artist could not be found."
        }), 400
    artist_result = artist_schema.dump(artist)
    social_result = social_schema.dump(social)
    poster_result = posters_schema.dump(artist.posters.all())
    return jsonify({
        'artist': artist_result.data,
        'social': social_result.data,
        'posters': poster_result.data
    })


@app.route('/artists/', methods=['POST'])
def add_artist():
    json_data = request.get_json()
    if not json_data:
        return jsonify({
            'Error': 'No data provided.'
        }), 400
    # Validate and deserializes input
    data, errors = social_schema.load(json_data)
    if errors:
        return jsonify, 422
    website, instagram, twitter, facebook = data['website'], data['instagram'], data['twitter'], data['facebook']
    add_social = Social.query.filter_by(website=website).first()
    first, last = data['artist']['first_name'], data['artist']['last_name']
    artist = Artist.query.filter_by(first_name=first, last_name=last).first()
    if artist is None:
        # Create new artist
        artist = Artist(
            first_name=first,
            last_name=last
        )
        db.session.add(artist)
    else:
        return jsonify({
            'Error': 'Artist data already exist.'
        }), 400

    if add_social is None:
        add_social = Social(
            artist=artist,
            website=website,
            instagram=instagram,
            twitter=twitter,
            facebook=facebook
        )
        db.session.add(add_social)

    db.session.commit()
    result = social_schema.dump(Social.query.get(add_social.id))
    return jsonify({
        'message': 'New artist added.',
        'artist': result.data
    })


@app.route('/posters/', methods=['GET'])
def get_posters():
    posters = Poster.query.all()
    posters_result = posters_schema.dump(posters)
    return jsonify({
        'posters': posters_result.data
    })


@app.route('/posters/<int:pk>')
def get_poster(pk):
    try:
        poster_id = Poster.query.get(pk)
    except IntegrityError:
        return jsonify({
            "Error": "Poster could not be found."
        }), 400
    poster_id = poster_schema.dump(poster_id)
    return jsonify({
        'poster': poster_id.data
    })


@app.route('/posters/', methods=['POST'])
def new_poster():
    json_data = request.get_json()
    if not json_data:
        return jsonify({
            'Error': 'No data provided.'
        }), 400
    # Validate and deserializes input
    data, errors = poster_schema.load(json_data)
    if errors:
        return jsonify, 422
    first, last = data['artist']['first_name'], data['artist']['last_name']
    artist = Artist.query.filter_by(first_name=first, last_name=last).first()
    if artist is None:
        # Create new artist
        artist = Artist(
            first_name=first,
            last_name=last
        )
        db.session.add(artist)
    # Create new poster
    add_poster = Poster(
        title=data['title'],
        year=data['year'],
        artist=artist,
        date_created=datetime.datetime.utcnow()
    )
    db.session.add(add_poster)
    db.session.commit()
    result = poster_schema.dump(Poster.query.get(add_poster.id))
    return jsonify({
        'message': 'New poster added.',
        'poster': result.data
    })


def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table %s' % table)
        session.execute(table.delete())
    session.commit()


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=8000)
