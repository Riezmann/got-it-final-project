from sqlalchemy import create_engine, text


def create_database():
    engine = create_engine("mysql+pymysql://root:giabao0120@127.0.0.1")
    with engine.connect() as conn:
        conn.execute(text("commit"))
        conn.execute(text("create database if not exists catalog"))
        conn.execute(text("use catalog"))
        conn.execute(
            text(
                "create table if not exists users"
                "(id int not null auto_increment,"
                "email varchar(255) not null,"
                "hashed_password varchar(255) not null,"
                "created_time datetime default current_timestamp,"
                "updated_time datetime default current_timestamp on update "
                "current_timestamp,"
                "primary key(id));"
            )
        )

        conn.execute(
            text(
                "create table if not exists categories"
                "(id int not null auto_increment,"
                "name varchar(100),"
                "user_id int not null,"
                "created_time datetime default current_timestamp,"
                "updated_time datetime default current_timestamp on update "
                "current_timestamp,"
                "primary key(id),"
                "foreign key (user_id) references users(id) on delete cascade);"
            )
        )

        conn.execute(
            text(
                "create table if not exists items"
                "(id int not null auto_increment,"
                "name varchar(100),"
                "description varchar(300), "
                "category_id int not null,"
                "user_id int not null,"
                "created_time datetime default current_timestamp, "
                "updated_time datetime default current_timestamp on update "
                "current_timestamp,"
                "primary key(id),"
                "foreign key (user_id) references users(id) on delete cascade,"
                "foreign key (category_id) references categories(id) on delete "
                "cascade);"
            )
        )

        conn.commit()
        conn.close()
