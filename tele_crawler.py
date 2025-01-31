import codecs
import posixpath
import re
import logging
import textwrap
from itertools import chain
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from jinja2 import Template
from lxml import etree
from concurrent.futures import ThreadPoolExecutor, as_completed

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class CreateMarkdown:
    """用于解析信息并生成 GitHub Markdown 文件的类，使用多线程优化"""

    def __init__(self, url='https://github.com/jackhawks/rectg', template_file='_template.md'):
        self.url = url
        self.template_file = template_file
        self.session = self.create_session()
        logging.info("CreateMarkdown 实例已创建，初始化URL和模板文件")

    def create_session(self):
        """创建带重试策略的会话"""
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def fetch_url(self, url):
        """获取并解析给定 URL 的 HTML 内容"""
        try:
            logging.info(f"开始请求URL: {url}")
            response = self.session.get(url, timeout=10)  # 超时时间设置为 10 秒
            response.raise_for_status()
            logging.info(f"成功获取URL: {url}")
            return etree.HTML(response.text)
        except requests.RequestException as e:
            logging.error(f"请求失败 URL: {url}，错误: {e}")
            return None

    def readme_links(self):
        """从 README 中提取包含 't.me' 的链接"""
        logging.info("开始提取 README 中的 t.me 链接")
        readme_url = posixpath.join(self.url, "blob/main/README.md")
        html = self.fetch_url(readme_url)
        if html is not None:
            links = [link.replace('\\"', '') for link in html.xpath('//*[contains(@href,"t.me")]/@href')]
            logging.info(f"从 README 中提取到 {len(links)} 个链接")
            return links
        logging.warning("未能从 README 中提取到任何链接")
        return []

    def issue_links(self):
        """从 issue 页面提取包含 't.me' 的链接"""
        logging.info("开始提取 issue 中的 t.me 链接")
        issues_url = posixpath.join(self.url, "issues")
        html = self.fetch_url(issues_url)
        if html is not None:
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(self.fetch_issue_link, urljoin(self.url, issue_path))
                    for issue_path in html.xpath("//div[contains(@role,'group')]//a[contains(@id,'issue_')]/@href")
                ]
                results = [future.result() for future in as_completed(futures) if future.result()]
                logging.info(f"从 issue 中提取到 {len(results)} 个链接")
                return results
        logging.warning("未能从 issue 中提取到任何链接")
        return []

    def fetch_issue_link(self, issue_url):
        """获取单个 issue 中的 t.me 链接"""
        logging.info(f"开始处理 issue URL: {issue_url}")
        issue_html = self.fetch_url(issue_url)
        if issue_html is not None:
            tg_link = issue_html.xpath("//a[contains(@href,'t.me')]/@href")
            if tg_link:
                logging.info(f"提取到 t.me 链接: {tg_link[0]}")
                return tg_link[0]
        logging.warning(f"未能从 issue URL 提取到 t.me 链接: {issue_url}")
        return None

    def parse_tg_page(self, url):
        """从 Telegram 页面提取详细信息"""
        logging.info(f"开始解析 Telegram 页面: {url}")
        html = self.fetch_url(url)
        if html is None:
            logging.warning(f"未能获取 Telegram 页面: {url}")
            return None

        # 检查页面是否包含 "If you have Telegram, you can contact @... right away."
        prompt_pattern = re.compile(r"If you have Telegram, you can contact @\w+ right away\.")
        page_text = ''.join(html.xpath("//body//text()"))  # 提取页面中的所有文本内容

        if prompt_pattern.search(page_text):
            logging.info(f"页面包含提示文本，跳过数据提取: {url}")
            return None

        data = {
            'tg_me_page_url': url,
            'tg_me_page_title': ''.join(html.xpath("//div[contains(@class,'tgme_page_title')]//span/text()")).replace(
                '|', ''),
            'tg_me_page_description': None,
            'tg_me_category': None,
            'tg_me_audience': None
        }

        page_extra = ''.join(html.xpath("//div[contains(@class,'tgme_page_extra')]/text()"))
        page_description = ''.join(html.xpath("//div[contains(@class,'tgme_page_description')]/text()"))

        if page_description and 'If you have' not in page_description:
            data['tg_me_page_description'] = page_description.replace('|', '')

        # 仅提取 "频道"、"群组" 或 "机器人" 类型，其他类型跳过
        if '@' in page_extra:
            data['tg_me_category'] = '机器人'
        elif 'subscribers' in page_extra:
            data['tg_me_category'] = '频道'
            data['tg_me_audience'] = re.search(r'\d+', page_extra.replace(' ', '')).group()
        elif 'members' in page_extra:
            data['tg_me_category'] = '群组'
            data['tg_me_audience'] = re.search(r'\d+', page_extra.replace(' ', '')).group()
        else:
            logging.info(f"非指定类型页面，跳过数据提取: {url}")
            return None  # 非指定类型，跳过

        logging.info(f"成功解析 Telegram 页面数据: {data}")
        return data

    def get_info(self, urls):
        """并行处理每个 URL，提取 Telegram 页面信息并按人数排序"""
        logging.info("开始并行提取 Telegram 页面信息")
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.parse_tg_page, url) for url in urls]
            results = [future.result() for future in as_completed(futures) if future.result()]

        # 处理 None 值，确保 tg_me_category 为字符串类型
        for item in results:
            if item['tg_me_category'] is None:
                item['tg_me_category'] = '其他'
            if item['tg_me_audience'] is not None:
                item['tg_me_audience'] = "{:,}".format(int(item['tg_me_audience']))

        sorted_results = sorted(
            results,
            key=lambda x: int(x['tg_me_audience'].replace(',', '') if x['tg_me_audience'] else 0),
            reverse=True
        )
        logging.info("完成 Telegram 页面信息提取与排序")
        return sorted_results

    def create_md(self, repo):
        """从优化后的模板生成 README.md 文件，按类型分块显示"""
        logging.info("开始生成 README.md 文件")
        template_content = textwrap.dedent("""
            # 【精选推荐】5000+ 高质量 Telegram 群组、频道和机器人 - 精选资源一站汇总，快速找到您需要的内容！
            
            > **免责声明**  
            > 本项目旨在为用户提供精选的 Telegram 群组、频道和机器人资源，所有内容均来自公开网络，仅供学习交流与技术研究使用。请您在访问和使用这些 Telegram 资源时，遵守当地的法律法规。  
            > 若您发现任何不适或敏感内容，欢迎在 GitHub 的 issues 中提交反馈，我们将及时处理，确保资源的质量和安全。  
            
            > **请注意**：本项目不对使用者的行为承担任何责任，使用者需自行承担使用本项目产生的所有后果。如有内容侵犯您的权益，请联系我们删除相关内容。
            
            > **项目地址**  
            > [点击访问 GitHub 项目，获取优质 Telegram 群组、频道和机器人资源](https://github.com/jackhawks/rectg)

            {% for category in ["频道", "群组", "机器人"] %}
            {% set items = repo | selectattr("tg_me_category", "equalto", category) | list %}
            {% if items %}
            ## {{ category }}

            | 名称 | 链接 | 人数 | 简介 |
            | :--: | :--: | :--: | ---- |
            {% for item in items %}
            | {{ item.tg_me_page_title or '无名称' }} | [Go]({{ item.tg_me_page_url }}) | {{ item.tg_me_audience or '未知' }} | {{ item.tg_me_page_description or '无简介' }} |
            {% endfor %}

            {% endif %}
            {% endfor %}

            > **注**: 以上信息为自动提取，可能存在数据不准确之处，请自行验证。

            ## Star History

            [![Star History Chart](https://api.star-history.com/svg?repos=jackhawks/rectg&type=Date)](https://star-history.com/#jackhawks/rectg&Date)
        """)
        template = Template(template_content, trim_blocks=True, lstrip_blocks=True)
        rendered_content = template.render(repo=repo)

        with codecs.open("README.md", "w", "utf-8") as output_file:
            output_file.write(rendered_content)
        logging.info("README.md 文件已生成")

    def start(self):
        """执行流程以收集链接、提取信息并生成 Markdown"""
        logging.info("开始执行 Telegram 信息提取和 Markdown 文件生成流程")

        # 提取 Issue 和 README 中的链接
        issue_links = self.issue_links()
        readme_links = self.readme_links()

        # 如果没有找到任何链接，则记录日志并退出
        if not issue_links and not readme_links:
            logging.warning("未找到任何 t.me 链接，流程终止")
            return

        # 合并链接并去重
        urls = set(chain(issue_links, readme_links))

        # 执行并行页面信息提取
        info = self.get_info(urls)
        if not info:
            logging.warning("未提取到有效的 Telegram 页面信息，流程终止")
            return

        # 生成 README 文件
        self.create_md(info)
        logging.info("流程执行完成")


if __name__ == '__main__':
    cm = CreateMarkdown()
    cm.start()
