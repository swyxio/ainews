import sqlite_utils

def setup_database(db_path):
    db = sqlite_utils.Database(db_path)

    def create_table_if_not_exists(table_name, schema, **kwargs):
        if table_name not in db.table_names():
            db[table_name].create(schema, **kwargs)
            print(f"Created table: {table_name}")
            return True
        else:
            return False

    # User table
    created = create_table_if_not_exists("User", {
        "user_id": str,
        "pseudonym": str,
        "markdown_bio": str,
        "created_at": str
    }, pk="user_id", not_null={"pseudonym"}, defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["User"].create_index(["pseudonym"], unique=True)
    
    user_count = next(db.query("SELECT count(*) FROM User"))['count(*)']
    if user_count < 1:
        print("No users found.  Creating  one.")

        import random
        import string

        def generate_random_username(length=8):
            letters = string.ascii_lowercase
            return ''.join(random.choice(letters) for i in range(length))

        pseudonym = generate_random_username()

        import uuid
        user_id = str(uuid.uuid4())

        db["User"].insert({
            "user_id": user_id,
            "pseudonym": pseudonym,
            "markdown_bio": f"I am {pseudonym}"
        })
    else:
        print("Users found.")

    # Comment table
    created = create_table_if_not_exists("Comment", {
        "comment_id": str,
        "user_id": str,
        "parent_id": str,
        "content": str,
        "created_at": str
    }, pk="comment_id", not_null={"content"}, defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["Comment"].add_foreign_key("user_id", "User", "user_id")
        db["Comment"].add_foreign_key("parent_id", "Comment", "comment_id")

    # Tag table
    created = create_table_if_not_exists("Tag", {
        "tag_id": str,
        "name": str,
        "description": str
    }, pk="tag_id", not_null={"name"})
    if created:
        db["Tag"].create_index(["name"], unique=True)

    # TagGroup table
    created = create_table_if_not_exists("TagGroup", {
        "group_id": str,
        "name": str,
        "description": str
    }, pk="group_id", not_null={"name"})
    if created: 
        db["TagGroup"].create_index(["name"], unique=True)

    # TagGroupAssociation table
    created= create_table_if_not_exists("TagGroupAssociation", {
        "group_id": str,
        "tag_id": str
    }, pk=("group_id", "tag_id"))
    if created:
        db["TagGroupAssociation"].add_foreign_key("group_id", "TagGroup", "group_id")
        db["TagGroupAssociation"].add_foreign_key("tag_id", "Tag", "tag_id")

    # Source table
    created= create_table_if_not_exists("Source", {
        "source_id": str,
        "url": str,
        "title": str,
        "description": str,
        "source_type": str,
        "created_at": str
    }, pk="source_id", not_null={"url", "title", "source_type"}, defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["Source"].create_index(["url"], unique=True)

    # Submission table
    created = create_table_if_not_exists("Submission", {
        "source_id": str,
        "user_id": str
    }, pk="source_id")
    if created:
        db["Submission"].add_foreign_key("source_id", "Source", "source_id")
        db["Submission"].add_foreign_key("user_id", "User", "user_id")

    # Post table
    created = create_table_if_not_exists("Post", {
        "post_id": str,
        "title": str,
        "description": str,
        "rank": int,
        "created_at": str
    }, pk="post_id", not_null={"title"}, defaults={"rank": 0, "created_at": "CURRENT_TIMESTAMP"})

    # PostSource table
    created = create_table_if_not_exists("PostSource", {
        "post_id": str,
        "source_id": str
    }, pk=("post_id", "source_id"))
    if created:
        db["PostSource"].add_foreign_key("post_id", "Post", "post_id")
        db["PostSource"].add_foreign_key("source_id", "Source", "source_id")

    # PostTag table
    created = create_table_if_not_exists("PostTag", {
        "post_id": str,
        "tag_id": str
    }, pk=("post_id", "tag_id"))
    if created:
        db["PostTag"].add_foreign_key("post_id", "Post", "post_id")
        db["PostTag"].add_foreign_key("tag_id", "Tag", "tag_id")

    # Bookmark table
    created = create_table_if_not_exists("Bookmark", {
        "bookmark_id": str,
        "user_id": str,
        "post_id": str,
        "created_at": str
    }, pk="bookmark_id", defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["Bookmark"].add_foreign_key("user_id", "User", "user_id")
        db["Bookmark"].add_foreign_key("post_id", "Post", "post_id")

    # Friends table
    created = create_table_if_not_exists("Friends", {
        "user_id": str,
        "friend_id": str,
        "created_at": str
    }, pk=("user_id", "friend_id"), defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["Friends"].add_foreign_key("user_id", "User", "user_id")
        db["Friends"].add_foreign_key("friend_id", "User", "user_id")

    # PostVote table
    created = create_table_if_not_exists("PostVote", {
        "vote_id": str,
        "user_id": str,
        "post_id": str,
        "vote_type": int,
        "created_at": str
    }, pk="vote_id", not_null={"user_id", "post_id", "vote_type"}, defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["PostVote"].add_foreign_key("user_id", "User", "user_id")
        db["PostVote"].add_foreign_key("post_id", "Post", "post_id")
        db["PostVote"].create_index(["user_id", "post_id"], unique=True)

    # CommentVote table
    created = create_table_if_not_exists("CommentVote", {
        "vote_id": str,
        "user_id": str,
        "comment_id": str,
        "vote_type": int,
        "created_at": str
    }, pk="vote_id", not_null={"user_id", "comment_id", "vote_type"}, defaults={"created_at": "CURRENT_TIMESTAMP"})
    if created:
        db["CommentVote"].add_foreign_key("user_id", "User", "user_id")
        db["CommentVote"].add_foreign_key("comment_id", "Comment", "comment_id")
        db["CommentVote"].create_index(["user_id", "comment_id"], unique=True)

    # print_schema(db)

def print_schema(db):
    print("\nDatabase schema setup complete.")
    print("\nDumping CREATE SQL statements for all tables:")

    for table_name in db.table_names():
        create_sql = db[table_name].schema
        print(f"\n-- Table: {table_name}")
        print(create_sql)

    print("\nSchema dump complete.")