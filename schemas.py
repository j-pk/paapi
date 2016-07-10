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
    instagram = fields.Str(allow_none=True)
    twitter = fields.Str(allow_none=True)
    facebook = fields.Str(allow_none=True)

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
    release_date = fields.Date(allow_none=True)
    class_type = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    technique = fields.Str(allow_none=True)
    size = fields.Str(allow_none=True)
    run_count = fields.Int(allow_none=True)
    image_url = fields.Str(allow_none=True)
    original_price = fields.Float(allow_none=True)
    average_price = fields.Float(allow_none=True)
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


