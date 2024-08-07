-- Schema for table: user
CREATE TABLE [user] (
    [user_id] TEXT PRIMARY KEY,
    [username] TEXT NOT NULL,
    [password] TEXT,
    [markdown_bio] TEXT,
    [email] TEXT,
    [created_at] TEXT DEFAULT CURRENT_TIMESTAMP

)


-- Schema for table: tag
CREATE TABLE [tag] (
    [tag_id] TEXT PRIMARY KEY,
    [name] TEXT NOT NULL,
    [description] TEXT

)


-- Schema for table: tag_group
CREATE TABLE [tag_group] (
    [group_id] TEXT PRIMARY KEY,
    [name] TEXT NOT NULL,
    [description] TEXT

)


-- Schema for table: tag_group_association
CREATE TABLE "tag_group_association" (
    [group_id] TEXT REFERENCES [tag_group]([group_id]),
    [tag_id] TEXT REFERENCES [tag]([tag_id]),
    PRIMARY KEY ([group_id], [tag_id])
    
    ,
    FOREIGN KEY (tag_id) REFERENCES tag (tag_id)
    ,
    FOREIGN KEY (group_id) REFERENCES tag_group (group_id)
    

);


-- Schema for table: source
CREATE TABLE [source] (
    [source_id] TEXT PRIMARY KEY,
    [url] TEXT NOT NULL,
    [title] TEXT NOT NULL,
    [description] TEXT,
    [source_type] TEXT NOT NULL,
    [created_at] TEXT DEFAULT CURRENT_TIMESTAMP

)


-- Schema for table: submission
CREATE TABLE "submission" (
    [source_id] TEXT PRIMARY KEY REFERENCES [source]([source_id]),
    [user_id] TEXT REFERENCES [user]([user_id])
    
    ,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
    ,
    FOREIGN KEY (source_id) REFERENCES source (source_id)
    

);


-- Schema for table: topic
CREATE TABLE [topic] (
    [topic_id] TEXT PRIMARY KEY,
    [title] TEXT NOT NULL,
    [user_id] TEXT,
    [primary_source_id] TEXT,
    [description] TEXT,
    [rank] INTEGER DEFAULT 0,
    [created_at] TEXT DEFAULT CURRENT_TIMESTAMP

)


-- Schema for table: topic_source
CREATE TABLE "topic_source" (
    [topic_id] TEXT REFERENCES [topic]([topic_id]),
    [source_id] TEXT REFERENCES [source]([source_id]),
    PRIMARY KEY ([topic_id], [source_id])
    
    ,
    FOREIGN KEY (source_id) REFERENCES source (source_id)
    ,
    FOREIGN KEY (topic_id) REFERENCES topic (topic_id)
    

);


-- Schema for table: topic_tag
CREATE TABLE "topic_tag" (
    [topic_id] TEXT REFERENCES [topic]([topic_id]),
    [tag_id] TEXT REFERENCES [tag]([tag_id]),
    PRIMARY KEY ([topic_id], [tag_id])
    
    ,
    FOREIGN KEY (tag_id) REFERENCES tag (tag_id)
    ,
    FOREIGN KEY (topic_id) REFERENCES topic (topic_id)
    

);


-- Schema for table: comment
CREATE TABLE "comment" (
    [comment_id] TEXT PRIMARY KEY,
    [user_id] TEXT REFERENCES [user]([user_id]),
    [parent_id] TEXT REFERENCES [comment]([comment_id]),
    [topic_id] TEXT REFERENCES [topic]([topic_id]),
    [content] TEXT NOT NULL,
    [created_at] TEXT DEFAULT CURRENT_TIMESTAMP
    
    ,
    FOREIGN KEY (topic_id) REFERENCES topic (topic_id)
    ,
    FOREIGN KEY (parent_id) REFERENCES comment (comment_id)
    ,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
    

);


-- Schema for table: bookmark
CREATE TABLE "bookmark" (
    [bookmark_id] TEXT PRIMARY KEY,
    [user_id] TEXT REFERENCES [user]([user_id]),
    [topic_id] TEXT REFERENCES [topic]([topic_id]),
    [created_at] TEXT DEFAULT CURRENT_TIMESTAMP
    
    ,
    FOREIGN KEY (topic_id) REFERENCES topic (topic_id)
    ,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
    

);


-- Schema for table: friend
CREATE TABLE "friend" (
    [user_id] TEXT REFERENCES [user]([user_id]),
    [friend_id] TEXT REFERENCES [user]([user_id]),
    [created_at] TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY ([user_id], [friend_id])
    
    ,
    FOREIGN KEY (friend_id) REFERENCES user (user_id)
    ,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
    

);


-- Schema for table: topic_vote
CREATE TABLE "topic_vote" (
    [vote_id] TEXT PRIMARY KEY,
    [user_id] TEXT NOT NULL REFERENCES [user]([user_id]),
    [topic_id] TEXT NOT NULL REFERENCES [topic]([topic_id]),
    [vote_type] INTEGER NOT NULL,
    [created_at] TEXT DEFAULT CURRENT_TIMESTAMP
    
    ,
    FOREIGN KEY (topic_id) REFERENCES topic (topic_id)
    ,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
    

);


-- Schema for table: comment_vote
CREATE TABLE "comment_vote" (
    [vote_id] TEXT PRIMARY KEY,
    [user_id] TEXT NOT NULL REFERENCES [user]([user_id]),
    [comment_id] TEXT NOT NULL REFERENCES [comment]([comment_id]),
    [vote_type] INTEGER NOT NULL,
    [created_at] TEXT DEFAULT CURRENT_TIMESTAMP
    
    ,
    FOREIGN KEY (comment_id) REFERENCES comment (comment_id)
    ,
    FOREIGN KEY (user_id) REFERENCES user (user_id)
    

);