import os
import requests
import psycopg2
from itemadapter import ItemAdapter
from supabase import create_client
from requests.adapters import HTTPAdapter


class SavePipeline:

    def __init__(self):
        url = ''
        key = ''
        self.bucket_name = 'tgqun'
        self.supabase = create_client(url, key)

        session = requests.Session()
        adapters = HTTPAdapter(max_retries=3)
        session.mount('https://', adapters)
        self.session = session

        hostname = ''
        username = ''
        password = ''
        database = ''

        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()

        # self.cur.execute("""
        # create table IF NOT EXISTS telegram_info (
        #    id                   BIGSERIAL            not null,
        #    user_name            varchar(255)         not null,
        #    nick_name            varchar(255)         null,
        #    link                 varchar(255)         null,
        #    avatar_url           TEXT                 null,
        #    resolve_url          varchar(255)         null,
        #    tg_type              INT2                 null,
        #    category             INT2                 null,
        #    subscribers          INT8                 null,
        #    members              INT8                 null,
        #    biography            TEXT                 null,
        #    create_time          TIMESTAMP            not null,
        #    update_time          TIMESTAMP            not null,
        #    constraint PK_TELEGRAM_INFO primary key (id),
        #    constraint AK_KEY_2_TELEGRAM unique (user_name)
        # );""")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        avatar_url = adapter.get('avatar_url', None)
        user_name = adapter.get('user_name', None)

        if avatar_url:
            if user_name and 'https://cdn' in avatar_url:
                img_suffix = os.path.splitext(avatar_url)[1]
                img_file = self.session.get(avatar_url, stream=True, timeout=10)
                img_name = "avatar/" + user_name + img_suffix
                self.supabase.storage.from_(self.bucket_name).upload(
                    img_name,
                    img_file.content,
                    {'content-type': 'image/jpeg; charset=utf-8', 'x-upsert': 'true'}
                )
                adapter["avatar_url"] = self.supabase.storage.from_(self.bucket_name).get_public_url(img_name)

            elif 'data:image/svg' in avatar_url:
                adapter['avatar_url'] = avatar_url
            else:
                adapter['avatar_url'] = None
        else:
            adapter['avatar_url'] = None

        try:
            self.cur.execute("""
    INSERT INTO telegram_info ( user_name, nick_name, link, avatar_url, resolve_url, tg_type, category, subscribers, members, biography, create_time, update_time )
    VALUES ( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s ) ON CONFLICT ( user_name ) DO NOTHING;""", (
                adapter.get("user_name", None),
                adapter.get("nick_name", None),
                adapter.get("link", None),
                adapter.get("avatar_url", None),
                adapter.get("resolve_url", None),
                adapter.get("tg_type", None),
                adapter.get("category", None),
                adapter.get("subscribers", None),
                adapter.get("members", None),
                adapter.get("biography", None),
                adapter.get("create_time", None),
                adapter.get("update_time", None),
            ))
            self.connection.commit()
        except:
            self.connection.rollback()

        return item

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
