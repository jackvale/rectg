# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import uuid
import psycopg2
import requests
from supabase import create_client
from itemadapter import ItemAdapter


class PostgresPipeline:

    def __init__(self):
        hostname = 'db.bvdnlqhdhqsxelbdvmlo.supabase.co'
        username = 'postgres'
        password = '3ZvLbMiSNCVzhaMj'  # your password
        database = 'postgres'

        ## Create/Connect to database
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)

        ## Create cursor, used to execute commands
        self.cur = self.connection.cursor()

        ## Create quotes table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS telegram(
            id BIGSERIAL PRIMARY KEY,
            origin_url text,
            origin_name text,
            name text,
            user_name text,
            avatar text,
            avatar_url text,
            description text,
            extra text,
            action text,
            action_link text,
            action_title text,
            link text,
            link_title text
        )
        """)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        self.cur.execute(""" insert into telegram (
                    name,
                    user_name,
                    avatar,
                    avatar_url,
                    description,
                    extra,
                    action,
                    action_title,
                    link,
                    link_title
        ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (
            adapter["name"],
            adapter["user_name"],
            adapter["avatar"],
            adapter["avatar_url"],
            adapter["description"],
            adapter["extra"],
            adapter["action"],
            adapter["action_title"],
            adapter["link"],
            adapter["link_title"],
        ))
        self.connection.commit()
        return item

    def close_spider(self, spider):
        ## Close cursor & connection to database
        self.cur.close()
        self.connection.close()


class ImagePipeline:

    def __init__(self):
        self.supabase = create_client('https://bvdnlqhdhqsxelbdvmlo.supabase.co',
                                      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ2ZG5scWhkaHFzeGVsYmR2bWxvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY4NzMyMjY3NiwiZXhwIjoyMDAyODk4Njc2fQ.QjYlRvrKBadPs6EuCpBrnVrEJBSe-1pKPX7G9COqLis')

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        avatar_url = adapter['avatar_url']
        if avatar_url != '' and 'http' in avatar_url:
            suffix = os.path.splitext(avatar_url)[1]
            f = requests.get(avatar_url, stream=True)
            img_name_prefix = uuid.uuid4().hex
            self.supabase.storage.from_('tgqun').upload("avatar/" + img_name_prefix + suffix, f.content,
                                                        file_options={'Content-Type': 'image/jpeg'})
            adapter["avatar"] = self.supabase.storage.from_('tgqun').get_public_url(
                "avatar/" + img_name_prefix + suffix)
        return item
