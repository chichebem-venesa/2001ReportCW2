from marshmallow import post_dump, validates, ValidationError
from config import db, ma
from marshmallow_sqlalchemy import fields
from marshmallow import fields
import pyodbc



# Feature model
class Feature(db.Model):
    __tablename__ = "feature"
    __table_args__ = {'schema': 'CW2'}
    Feature_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Feature_name = db.Column(db.String(510), unique=True, nullable=False)

# Trail model
class Trail(db.Model):
    __tablename__ = "trail"
    __table_args__ = {'schema': 'CW2'}
    TrailID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TrailName = db.Column(db.String(510), unique=True, nullable=False)
    TrailSummary = db.Column(db.String(510))
    TrailDescription = db.Column(db.String(510))
    Difficulty = db.Column(db.String(100))
    Location = db.Column(db.String(510))
    Length = db.Column(db.Float)
    ElevationGain = db.Column(db.Float)
    RouteType = db.Column(db.String(100))
    OwnerID = db.Column(db.Integer, db.ForeignKey('CW2.user_table.UserID'))
    locations = db.relationship('TrailLocation', back_populates='trail', cascade="all, delete-orphan", lazy="joined")

# Trail Location Model
class TrailLocation(db.Model):
    __tablename__ = 'Trail_Location'
    __table_args__ = {'schema': 'CW2'}

    LocationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TrailID = db.Column(db.Integer, db.ForeignKey('CW2.trail.TrailID'))
    Latitude = db.Column(db.Numeric(9, 6))
    Longitude = db.Column(db.Numeric(9, 6))
    Description = db.Column(db.String(255))
    PointOrder = db.Column(db.Integer)

    trail = db.relationship('Trail', back_populates='locations')

# Trail_feature model
class Trail_feature(db.Model):
    __tablename__ = "trail_feature"
    __table_args__ = {'schema': 'CW2'}
    Trail_feature_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Trail_id = db.Column(db.Integer, db.ForeignKey('CW2.trail.TrailID'), nullable=False)
    Feature_id = db.Column(db.Integer, db.ForeignKey('CW2.feature.Feature_id'), nullable=False)

# Define relationships after all models
Trail.trail_features = db.relationship(
    'Trail_feature',
    backref='trail',
    cascade="all, delete-orphan",
    single_parent=True
)

Feature.trail_features = db.relationship(
    'Trail_feature',
    backref='feature',
    cascade="all, delete-orphan",
    single_parent=True
)

# User model
class User(db.Model):
    __tablename__ = "user_table"
    __table_args__ = {'schema': 'CW2'}
    UserID = db.Column(db.Integer, primary_key=True)
    EmailAddress = db.Column(db.String(120), unique=True, nullable=False)
    Role = db.Column(db.String(120))
    trails = db.relationship(
        'Trail',
        backref='owner',
        cascade="all, delete-orphan",
        single_parent=True
    )

# Schemas
class FeatureSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Feature
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    trail_features = fields.Nested('Trail_featureSchema', many=True, exclude=("feature",))
    Feature_id = fields.Int(dump_only=True)

    @post_dump
    def remove_trail_features(self, data, **kwargs):
        # Removing circular reference (trail_features) from serialized data
        data.pop('trail_features', None)
        return data


class TrailLocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TrailLocation
        load_instance = True
        include_fk = True
        sqla_session = db.session
        include_relationships = True

    trail = fields.Nested('TrailSchema', dump_only=True)

    @validates('TrailID')
    def validate_trail_id(self, value):
        if not Trail.query.filter(Trail.TrailID == value).first():
            raise ValidationError(f"TrailID {value} does not exist.")

    @post_dump
    def remove_trail(self, data, **kwargs):

        data.pop('trail', None)
        return data


class TrailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Trail
        load_instance = True
        include_fk = True
        sqla_session = db.session
        include_relationships = True

    trail_features = fields.Nested('Trail_featureSchema', many=True, exclude=("trail",))
    locations = fields.List(fields.Nested('TrailLocationSchema'))
    TrailID = fields.Integer(dump_only=True)

    @post_dump
    def conditionally_remove_relationships(self, data, many, **kwargs):
        if not kwargs.get("include_details", True):
            data.pop('trail_features', None)
            data.pop('locations', None)
        return data


class Trail_featureSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Trail_feature
        load_instance = True
        include_fk = True
        sqla_session = db.session
        include_relationships = True

    trail = fields.Nested('TrailSchema', dump_only=True)
    feature = fields.Nested('FeatureSchema', dump_only=True)

    @post_dump
    def remove_trail_and_feature(self, data, **kwargs):
        if kwargs.get('exclude_references', False):
            data.pop('trail', None)
            data.pop('feature', None)
        return data


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    trails = fields.Nested(TrailSchema, many=True, exclude=("owner",))

    @post_dump
    def remove_trails(self, data, **kwargs):

        data.pop('trails', None)
        return data

# Initialize schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)

trail_schema = TrailSchema()
trails_schema = TrailSchema(many=True)

feature_schema = FeatureSchema()
features_schema = FeatureSchema(many=True)

trail_feature_schema = Trail_featureSchema()
trail_features_schema = Trail_featureSchema(many=True)
