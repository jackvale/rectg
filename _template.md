# 【热门推荐】5000+ 优质 Telegram 群组、频道和机器人，精心筛选，助您迅速找到最佳选择！

> **Note**
> 声明：本项目的所有内容均来源于网络，仅供学习和技术研究使用。

> **Warning**
> 如果大家有发现存在敏感内容的群组、频道和机器人欢迎在 issues 中提交，会在第一时间处理。

> GitHub 项目地址直达
> [https://github.com/jackhawks/rectg](https://github.com/jackhawks/rectg)

{# 头像宏 #}
{% macro avatar(link, alt, img) -%}
<a href="{{ link }}"><img alt="{{ alt }}" src="{{ img }}" height="auto" width="60px" style="border-radius:50%"></a>
{%- endmacro %}

|                             头像                             | 名称 | 简介 | 人数 | 类型 |
| :----------------------------------------------------------: | :--: | :--: | :--: | :--: |
{% for item in repo %}
| {{avatar(item.tg_me_page_url, item.tg_me_page_title, item.tg_me_page_photo)}} | [{{item.tg_me_page_title}}]({{item.tg_me_page_url}}) | {{item.tg_me_page_description}} | {{item.tg_me_audience}} | {{item.tg_me_category}} |
{% endfor %}


## 免责声明

本项目的所有内容均来源于网络，仅供学习和研究使用。项目中列出的频道/群组/机器人等可能包含部分敏感内容。请您自觉遵守当地的法律法规。本项目不对使用者的行为承担任何责任。使用者应自行承担使用本项目所产生的一切后果。如有内容侵犯了您的权益，请联系我们删除相关内容。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=jackhawks/rectg&type=Date)](https://star-history.com/#jackhawks/rectg&Date)