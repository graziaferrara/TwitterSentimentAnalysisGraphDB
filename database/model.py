from neomodel import StructuredNode, StringProperty, RelationshipTo, RelationshipFrom, IntegerProperty, BooleanProperty, FloatProperty

class Trend(StructuredNode):
    id_mongo = StringProperty(unique_index=True, required=True)
    url = StringProperty(unique_index=True, required=True)
    name = StringProperty()
    location = StringProperty()
    date = StringProperty()
    tweets = RelationshipFrom('Tweet', 'RELATED_TO')

class Tweet(StructuredNode):
    id_mongo = StringProperty(unique_index=True, required=True)
    url = StringProperty(unique_index=True, required=True)
    username = StringProperty(required=True)
    text = StringProperty(required=True)
    sentiment = FloatProperty(required=True)
    retweets = IntegerProperty(required=True)
    likes = IntegerProperty(required=True)
    shares = IntegerProperty(required=True)
    user = RelationshipTo('User', 'POSTED_BY')
    trend = RelationshipTo('Trend', 'RELATED_TO')
    comments = RelationshipTo('Tweet', 'COMMENTED_ON')

class User(StructuredNode):
    id_mongo = StringProperty(unique_index=True, required=True)
    username = StringProperty(unique_index=True, required=True)
    followers = IntegerProperty(required=True)
    following = IntegerProperty(required=True)
    verified = BooleanProperty(required=True)
    tweets = RelationshipFrom('Tweet', 'POSTED_BY')