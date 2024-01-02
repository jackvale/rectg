import codecs
import posixpath
import re
from itertools import chain
from urllib.parse import urljoin

import requests
from jinja2 import Template
from lxml import etree


class CreateMarkdown:
    """ Create GitHub Markdown """

    def __init__(self):
        self.url = 'https://github.com/jackhawks/rectg'
        self.template_file = 'template.md'

    def readme_handler(self):
        readme_url = posixpath.join(self.url, "blob/main/README.md")
        response = requests.get(readme_url)
        html = etree.HTML(response.text)
        elements = html.xpath('//*[contains(@href,"t.me")]/@href')
        for element in elements:
            yield element.replace('\\"', '')

    def issues_handler(self):
        issues_url = posixpath.join(self.url, "issues")
        response = requests.get(issues_url)
        html = etree.HTML(response.text)
        elements = html.xpath("//div[contains(@role,'group')]//a[contains(@id,'issue_')]/@href")
        for element in elements:
            issues_title_url = urljoin(self.url, element)
            iss_resp = requests.get(issues_title_url)
            iss_html = etree.HTML(iss_resp.text)
            iss_elements = iss_html.xpath("//a[contains(@href,'t.me')]/@href")[0]
            yield iss_elements

    def url_join(self, *args):
        return chain(*args)

    def get_info(self, urls):
        for idx, url in enumerate(urls):

            print(idx, ' ---> ', url)

            response = requests.get(url)
            html = etree.HTML(response.text)

            tg_me_page_url = url

            tg_me_page_photo = dict(enumerate(html.xpath(
                "//div[contains(@class,'tgme_page')]//div[contains(@class,'tgme_page_photo')]//img/@src"))).get(0)

            try:
                tg_me_page_title_raw = dict(enumerate(html.xpath(
                    "//div[contains(@class,'tgme_page')]//div[contains(@class,'tgme_page_title')]//span/text()"))).get(
                    0)
                tg_me_page_title = tg_me_page_title_raw.replace('|', '')
            except:
                continue

            tg_me_page_extra = dict(enumerate(
                html.xpath(
                    "//div[contains(@class,'tgme_page')]//div[contains(@class,'tgme_page_extra')]/text()"))).get(
                0)

            try:
                tg_me_page_description_raw = dict(enumerate(html.xpath(
                    "//div[contains(@class,'tgme_page')]//div[contains(@class,'tgme_page_description')]/text()"))).get(
                    0)
                if 'If you have' in tg_me_page_description_raw:
                    continue

                tg_me_page_description = tg_me_page_description_raw.replace('|', '')

            except:
                tg_me_page_description = None

            # 数据处理
            tg_me_audience = None
            tg_me_category = None
            if '@' in tg_me_page_extra:
                tg_me_category = '机器人'
                tg_me_audience = None
            elif 'subscribers' in tg_me_page_extra:
                tg_me_category = '频道'
                tg_me_audience = re.match(r'\d+', re.sub(' ', '', tg_me_page_extra)).group()
            elif 'members' in tg_me_page_extra:
                tg_me_category = '群组'
                tg_me_audience = re.match(r'\d+', re.sub(' ', '', tg_me_page_extra)).group()

            yield {
                'tg_me_page_url': tg_me_page_url,
                'tg_me_page_photo': tg_me_page_photo,
                'tg_me_page_title': tg_me_page_title,
                'tg_me_audience': tg_me_audience,
                'tg_me_page_description': tg_me_page_description,
                'tg_me_category': tg_me_category,
            }

    def create_md(self, repo):
        with open('template.md', 'r', encoding='utf-8') as file:
            template = Template(file.read(), trim_blocks=True)
            rendered_file = template.render(repo=repo)
            # output the file
            output_file = codecs.open("README.md", "w", "utf-8")
            output_file.write(rendered_file)
            output_file.close()

    def start(self):
        issues = self.issues_handler()
        readme = self.readme_handler()
        urls = self.url_join(issues, readme)
        info = self.get_info(urls)
        self.create_md(info)


if __name__ == '__main__':
    cm = CreateMarkdown()
    cm.start()
