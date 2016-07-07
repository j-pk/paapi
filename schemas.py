from marshmallow import Schema, fields, ValidationError, pre_load


##### SCHEMAS #####
class ArtistSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str()
    last_name = fields.Str()
    formatted_name = fields.Method('format_name', dump_only=True)

    def format_name(self, artist):
        return "{}, {}".format(artist.last_name, artist.first_name)


def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


class SocialSchema(Schema):
    id = fields.Int(dump_only=False)
    artist = fields.Nested(ArtistSchema, validate=must_not_be_blank)
    website = fields.Str()
    instagram = fields.Str()
    twitter = fields.Str()
    facebook = fields.Str()

    @pre_load
    def process_author(self, data):
        artist_name = data.get('artist')
        if artist_name:
            first_name, last_name = artist_name.split(' ')
            artist_dict = dict(first_name=first_name, last_name=last_name)
        else:
            artist_dict = {}
        data['artist'] = artist_dict
        return data


class PosterSchema(Schema):
    id = fields.Int(dump_only=True)
    artist = fields.Nested(ArtistSchema, validate=must_not_be_blank)
    title = fields.Str(required=True, validate=must_not_be_blank)
    year = fields.Int(required=True, validate=must_not_be_blank)
    date_created = fields.DateTime(dump_only=True)

    @pre_load
    def process_author(self, data):
        artist_name = data.get('artist')
        if artist_name:
            first_name, last_name = artist_name.split(' ')
            artist_dict = dict(first_name=first_name, last_name=last_name)
        else:
            artist_dict = {}
        data['artist'] = artist_dict
        return data


