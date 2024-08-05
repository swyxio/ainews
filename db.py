import sqlite_utils
import threading
from typing import Dict, Any

def setup_database(db):
    def create_table_if_not_exists(table_name, schema, **kwargs):
        if table_name not in db.table_names():
            db[table_name].create(schema, **kwargs)
            print(f"Created table: {table_name}")
            return True
        else:
            return False

    # user table
    created = create_table_if_not_exists("user", {
        "user_id": str,
        "username": str,
        "password": str,
        "markdown_bio": str,
        "email": str,
        "created_at": str
    }, pk="user_id", not_null={"username"}, defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["user"].create_index(["username"], unique=True)
    

    # tag table
    created = create_table_if_not_exists("tag", {
        "tag_id": str,
        "name": str,
        "description": str
    }, pk="tag_id", not_null={"name"})
    if created:
        db["tag"].create_index(["name"], unique=True)

    # tag_group table
    created = create_table_if_not_exists("tag_group", {
        "group_id": str,
        "name": str,
        "description": str
    }, pk="group_id", not_null={"name"})
    if created: 
        db["tag_group"].create_index(["name"], unique=True)

    # tag_group_association table
    created= create_table_if_not_exists("tag_group_association", {
        "group_id": str,
        "tag_id": str
    }, pk=("group_id", "tag_id"))
    if created:
        db["tag_group_association"].add_foreign_key("group_id", "tag_group", "group_id")
        db["tag_group_association"].add_foreign_key("tag_id", "tag", "tag_id")

    # source table
    created= create_table_if_not_exists("source", {
        "source_id": str,
        "url": str,
        "title": str,
        "description": str,
        "source_type": str,
        "created_at": str
    }, pk="source_id", not_null={"url", "title", "source_type"}, defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["source"].create_index(["url"], unique=True)

    # submission table
    created = create_table_if_not_exists("submission", {
        "source_id": str,
        "user_id": str
    }, pk="source_id")
    if created:
        db["submission"].add_foreign_key("source_id", "source", "source_id")
        db["submission"].add_foreign_key("user_id", "user", "user_id")

    # post table
    created = create_table_if_not_exists("post", {
        "post_id": str,
        "title": str,
        "user_id": str,
        "primary_source_id": str,
        "description": str,
        "rank": int,
        "created_at": str
    }, pk="post_id", not_null={"title"}, defaults={"rank": 0, "created_at": "CURRENT_TIMESTAMP"})


    # post_source table
    created = create_table_if_not_exists("post_source", {
        "post_id": str,
        "source_id": str
    }, pk=("post_id", "source_id"))
    if created:
        db["post_source"].add_foreign_key("post_id", "post", "post_id")
        db["post_source"].add_foreign_key("source_id", "source", "source_id")

    # post_tag table
    created = create_table_if_not_exists("post_tag", {
        "post_id": str,
        "tag_id": str
    }, pk=("post_id", "tag_id"))
    if created:
        db["post_tag"].add_foreign_key("post_id", "post", "post_id")
        db["post_tag"].add_foreign_key("tag_id", "tag", "tag_id")

    # comment table
    created = create_table_if_not_exists("comment", {
        "comment_id": str,
        "user_id": str,
        "parent_id": str,
        "post_id": str,
        "content": str,
        "created_at": str
    }, pk="comment_id", not_null={"content"}, defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["comment"].add_foreign_key("user_id", "user", "user_id")
        db["comment"].add_foreign_key("post_id", "post", "post_id")
        db["comment"].add_foreign_key("parent_id", "comment", "comment_id")

    # bookmark table
    created = create_table_if_not_exists("bookmark", {
        "bookmark_id": str,
        "user_id": str,
        "post_id": str,
        "created_at": str
    }, pk="bookmark_id", defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["bookmark"].add_foreign_key("user_id", "user", "user_id")
        db["bookmark"].add_foreign_key("post_id", "post", "post_id")

    # friends table
    created = create_table_if_not_exists("friend", {
        "user_id": str,
        "friend_id": str,
        "created_at": str
    }, pk=("user_id", "friend_id"), defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["friend"].add_foreign_key("user_id", "user", "user_id")
        db["friend"].add_foreign_key("friend_id", "user", "user_id")

    # post_vote table
    created = create_table_if_not_exists("post_vote", {
        "vote_id": str,
        "user_id": str,
        "post_id": str,
        "vote_type": int,
        "created_at": str
    }, pk="vote_id", not_null={"user_id", "post_id", "vote_type"}, defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["post_vote"].add_foreign_key("user_id", "user", "user_id")
        db["post_vote"].add_foreign_key("post_id", "post", "post_id")
        db["post_vote"].create_index(["user_id", "post_id"], unique=True)

    # comment_vote table
    created = create_table_if_not_exists("comment_vote", {
        "vote_id": str,
        "user_id": str,
        "comment_id": str,
        "vote_type": int,
        "created_at": str
    }, pk="vote_id", not_null={"user_id", "comment_id", "vote_type"}, defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["comment_vote"].add_foreign_key("user_id", "user", "user_id")
        db["comment_vote"].add_foreign_key("comment_id", "comment", "comment_id")
        db["comment_vote"].create_index(["user_id", "comment_id"], unique=True)


def print_schema(db):
    print("\nDatabase schema setup complete.")
    print("\nDumping CREATE SQL statements for all tables:")

    for table_name in db.table_names():
        create_sql = db[table_name].schema
        print(f"\n-- Table: {table_name}")
        print(create_sql)

    print("\nSchema dump complete.")







