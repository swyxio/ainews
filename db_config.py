import os
from fasthtml.common import *
from db import setup_database
import sqlite_utils
import seed

def setup_db():
    sqlite_db_path = os.getenv('SQLITE_DB_PATH', "./data/ainews.db")
    setup_database(sqlite_db_path)
    print(f"Creating Application DB Connection: {sqlite_db_path}")
    db = sqlite_utils.Database(sqlite_db_path)
    seed.seed_objects(sqlite_db_path, db)
    db.close()

    db = database(sqlite_db_path)

    comment = db.t.comment
    tag, tagGroup, tagGroupAssociation, source, submission = db.t.tag, db.t.tag_group, db.t.tag_groupAssociation, db.t.source, db.t.submission
    user, topic, topicSource, topicTag, bookmark, friend, topicVote, commentVote, feedback = db.t.user, db.t.topic, db.t.topic_source, db.t.topic_tag, db.t.bookmark, db.t.friend, db.t.topic_vote, db.t.commentVote, db.t.feedback
    Comment, Tag, TagGroup, TagGroupAssociation, Source, Submission, Feedback = comment.dataclass(), tag.dataclass(), tagGroup.dataclass(), tagGroupAssociation.dataclass(), source.dataclass(), submission.dataclass(), feedback.dataclass()
    User, Topic, TopicSource, TopicTag, Bookmark, Friend, TopicVote, CommentVote  = user.dataclass(), topic.dataclass(), topicSource.dataclass(), topicTag.dataclass(), bookmark.dataclass(), friend.dataclass(), topicVote.dataclass(), commentVote.dataclass()

    return db, (
        Comment, Tag, TagGroup, TagGroupAssociation, Source, Submission, Feedback, User, Topic, TopicSource, TopicTag, Bookmark, Friend, TopicVote, CommentVote,
        comment, tag, tagGroup, tagGroupAssociation, source, submission, user, topic, topicSource, topicTag, bookmark, friend, topicVote, commentVote, feedback
    )