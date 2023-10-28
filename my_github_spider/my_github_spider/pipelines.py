from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings
import psycopg2


class MyGithubSpiderPipeline:
    def __init__(self):
        settings = get_project_settings()
        self.database = settings['DB_DATABASE']
        self.host = settings['DB_HOST']
        self.user = settings['DB_USER']
        self.password = settings['DB_PASSWORD']
        self.port = settings['DB_PORT']

    def open_spider(self, spider):
        self.connect()

    def connect(self):
        self.conn = psycopg2.connect(
            database=self.database,
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
        )
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        tg_url = adapter.get('tg_url')
        tg_name = adapter.get('tg_name')
        tg_desc = adapter.get('tg_desc')
        tg_person_num = adapter.get('tg_person_num')
        tg_category = adapter.get('tg_category')

        sql = f"INSERT INTO jack_github_md ( tg_url, tg_name, tg_desc, tg_person_num, tg_category) VALUES ( %s,%s,%s,%s,%s)"
        self.cursor.execute(sql, (tg_url, tg_name, tg_desc, tg_person_num, tg_category))
        self.conn.commit()

        return item
