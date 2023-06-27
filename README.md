# Telegram 优质群组/频道/机器人 精选推荐

> 声明：本项目的所有内容均来源于网络，只作为学习及技术研究使用。

[GitHub项目直达](https://github.com/alexbei/telegram-groups)

## 项目简介

**背景**：使用 Telegram 的时候，为了能找到一些有意思的、好玩的、纯粹资源分享的群和频道，总是很困难，尽管有些网站推荐了不少的群/频道/机器人，但是往往其中很多都已经过期了，甚至很多都注销了，也有一些变成了涩涩群、机场群，一个一个筛选起来很麻烦，所以决定用 Python 爬虫来解决这一问题。



##### 第一集：

**过程**：用时一天时间，收集整理了很多网站数据，建立 URL 集合，使用 Scrapy 总共从十几个地址，爬了总计 3534 条数据。所有的数据及 SQL 已经放到文件 `data.csv` 中，爬虫代码放在了 `telegram-groups-spider` 文件夹里面。有需要的同学可以自行取用。



**结果**：从 3534 个中，按照订阅数/会员数排序，并排除了其他语言的账号只选择做中文内容的账号，也排除了包含：机场、Sex、Gamble、Politics等内容，手工精选了 200 多个放在了下面的表格里，感兴趣的同学可以根据自己喜好选择加入。



**感悟**：从数据来看，其中有很多是早已注销的群/频道/机器人，也有不是是灰黑产业的账号或者挂羊头卖狗肉的账号。精选账号大概只占到总数的 **6%**，这个比例还是挺惊人的，中文的优质内容在 Telegram 还是相对匮乏，Telegram 在中文内容上更像是一个灰黑产的温床。虽然精选了 200 多个账号，但其中也有不少是羊毛，搬运，资源，影视，破解等内容，这些内容也是处于擦边球地带，真正优质的内容还会更少，当然这也限制与样本本身的质量，也许有不少好的账号还未被发现，也欢迎知道优质账号的同学能在 issue 留下它的链接。



##### 第二集：

首先来看看一些有意思的数据：

- **v2ex**
  - 在帖子发出后的 24 小时内：共有 6232 次点击，206 人收藏，22 人感谢，被 4505 位注册会员查看过。其中 **收藏率 4.6%** ，**感谢占比 0.49%** ，还有 126 次来自 Google 的点击。
- **GitHub**
  - 在帖子发出后的 24 小时内：共收到 Star 552 个，Fork 51 个，有 7 人提交了 issue。平均**每小时 Star 23 个**



昨天发帖之后，发现样本还是太少，所以又重新收集了数据，在昨天数据的基础上，爬了一晚上，样本数来到了 **5000+** （这貌似是我能找到的极限了），基于更大的样本集，也重新产出了一些值得参考的新数据：



- **总样本数量：5205 个**
  - 其中正常账号 3036 个，异常账号 2169 个（主要是已注销账号），**异常账号占比：41.7%**，**正常账号占比：58%**
  
  - 频道数：1700，群组：1136，机器人：198。分别占比：32.7%，21.8%，0.38%
  - 频道订阅人数排名前 10 的没有一个中文账号，前 10 的账号订阅人数均超过了 100 万，**最高订阅人数 912 万**
  - 群组会员人数排名前 10 的 9 个都是中文账号，**最高会员人数 19 万**，最低 6 万
- 在过滤了 144 个关键字之后还**剩下 2209 个**账号，当然这其中依然有不少是需要筛选的（人麻了，筛了5个小时，实在筛不动了...），结果如下：
  - 资源分享类 352个，占比 15.9%
  - 机场、VPS类 103个，占比 4.7%
  - 影视类 108 个，占比 4.9%
  - 音乐类 56 个，占比 2.5%
  - 币圈类 39 个，占比 1.8%
  - 书类 67 个，占比 3%
  - 破解类 44 个，占比 2%
  - 羊毛、优惠类 53 个，占比 2.4%



###### **总结：**

本次总共从 **25 个 URL** 地址获得了 **5205 个样本集**，样本集本身已经做了去重处理，实际的数量应该有 10000+，重复的账号没有分析的意义，就直接过滤掉了没有入库。入库之后的数据进行了二次过滤（主要是人工过滤），过滤了Sex、Gamble、Politics、黑灰产、已注销、私人账号等，经过两轮筛选最终只剩下了 **2209** 个账号，占总数的：**42.4%** ，已经不到一半了，这还是粗筛，如果细筛那最终样本会更少。

从过滤之后的数据来看，貌似各个分类的占比都很少，其实不然，因为很多账号都是跨多个分类，并不是只专精一个分类。另一方面从关键字来筛选分类，并不是很准确，最准确的应该是点进每个账号里去看内容，但这样的话人工成本会很高。

假如按照程序员这个角色的用户画像来进行推荐的话，应该和昨天的 **6%** 差距不大，这也基本反应了现在 Telegram 中文生态的现状。这些数据还有其他的挖掘价值，用来做数据分析还是很不错的。




## 频道




> 公开的高质量 TG 频道推荐，可以根据自己喜好选择订阅



| 频道                                                         | 简介                                                         |
| :----------------------------------------------------------- | ------------------------------------------------------------ |
| [吃瓜群众](https://t.me/chigua2022)                          | 吃瓜搞笑                                                     |
| [TeloNews简体中文-加密货币｜DeFi｜Web3](https://t.me/telonews_cn) | 最新的加密货币新闻，观点和数据分析，洞见市场发展             |
| [破解软件分享-百科全书](https://t.me/OOAPK)                  | 本频道为正规频道，内容包括各种资源工具等                     |
| [阿里云盘发布频道](https://t.me/shareAliyun)                 | 和谐、友爱的阿里云盘分享交流频道                             |
| [[合租通知]Netflix](https://t.me/hezu2)                      | 好物、街拍、软件、小说、搞笑、资源、视频、返利               |
| [科技新闻投稿TestFlight](https://t.me/TestFlightCN)          | 日常推送科技新闻和互动消息                                   |
| [竹新社](https://t.me/tnews365)                              | 7×24不定时编译国内外媒体的即时新闻报道。                     |
| [APP喵-阿喵软件资源共享](https://t.me/appmew)                | iOS，安卓，macOS，windows                                    |
| [GoogleDrive资源](https://t.me/gdsharing)                    | 大电影，小电影，电子书，无损音乐等                           |
| [黑科技软件资源分享](https://t.me/kkaifenxiang)              | 分享免费实用高效率网络资源、黑科技软件、实用黑技巧           |
| [PIXIV站每日Top50搬运](https://t.me/pixiv_top50)             | 搬運PIXIV每天綜合排行榜前50圖片資源，不定時更新              |
| [NEP.Anime动画仓库](https://t.me/AnimeNep)                   | 涅普涅普的动画仓库                                           |
| [快乐星球妹子图收集器](https://t.me/botmzt)                  | 美女妹子精选全网中文快乐星球                                 |
| [Newlearnerの自留地](https://t.me/NewlearnerChannel)         | 不定期推送IT相关资讯，欢迎关注                               |
| [8度科技破解频道](https://t.me/pjrjzy)                       | 8度资源                                                      |
| [风向旗参考快讯](https://t.me/xhqcankao)                     | 互联网科技新闻快讯                                           |
| [颜值即正义](https://t.me/yzjzy)                             | 颜值即正义                                                   |
| [足控天堂](https://t.me/sizukon)                             | 原创美腿丝袜，黑丝、肉丝、蕾丝、足控、高跟鞋、高清美女写真   |
| [你不知道的内幕消息](https://t.me/inside1024)                | 最新行业资讯、以及大公司的负面新闻、财经观点信息、好物       |
| [浥轻尘の资源分享](https://t.me/yqc_123)                     | 专注于iOS破解、规则、脚本、补丁、插件、软件、逆向、越狱、开源、内测、限免、证书、教程、福利等资源分享 |
| [[好读]ReadFine电子书屋](https://t.me/Readfine)              | 好读提供电子书一站式体验。科普、医学、心理、历史、近代史、世界史、政治、禁书、社科、科幻、商业、理财、管理、饮食、推理、法律、悬疑、奇幻、军事、经典、两性、哲学、小说、游历、教育、随笔、文学、文化、纪实、自我成长、耽美、宗教、回忆录 |
| [宝藏女孩·爱酱](https://t.me/BaoZang)                        | 阅天下之美人，品世间之甜美。此乃人间正道，亦是高寿秘诀       |
| [阿里云盘发布频道](https://t.me/Aliyundrive_Share_Channel)   | 和谐、友爱的阿里云盘分享交流频道，每个人在这里都可以分享自己想分享的资源 |
| [阿里云盘4K影视](https://t.me/Aliyun_4K_Movies)              | 影巢&4K影视冢新人必看。更新4K电影更新纪录片更新电视剧更新动画片 |
| [亞洲美女頻道](https://t.me/asiangirlsss)                    | 每日免費推薦大量亞洲美女                                     |
| [豆瓣精选](https://t.me/douban_read)                         | 豆瓣精选。豆瓣书影音，以及相关讨论                           |
| [Solidot](https://t.me/solidot)                              | solidot.org非官方RSS推送频道                                 |
| [每天趣事](https://t.me/Meitian)                             | 本频道内容：多样沙雕冷笑话，津津乐道稀奇事。记录事实另眼看，不屑一顾高级黑 |
| [开源社区](https://t.me/opencfdchannel)                      | Android/Linux/Windows/MacOS/iOS科技人文资讯聊天群组投稿请私信 |
| [4KRemux](https://t.me/Remux_2160P)                          | 4K影视资源分享流媒体合租                                     |
| [Legado｜开源阅读｜频道](https://t.me/Legado_Channels)       | 阅读APK、书源、背景排版及部分公众号内容，还有群友的推文投稿  |
| [彭于晏资源分享频道](https://t.me/py996)                     | iOS破解应用、安卓破解应用、电脑破解软件、优质订阅节点、精品网站导航、Thor破解规则、网球破解规则、捷径破解规则、JS破解脚本、圈X破解脚本、Flex破解补丁、越狱破解插件、优秀开源项目、海量福利资源等 |
| [极客分享](https://t.me/geekshare)                           | 专注分享各种高质量网站、工具、APP、开源项目等一切好玩的东西🚀 |
| [免费资源](https://t.me/freeresource)                        | 本频道主要内容为个人兴趣信息。如steam等                      |
| [宝藏资源分享](https://t.me/iosrxwy)                         | 资源发布、福利分享➜软件黑科技，玩机技巧➜捷径脚本、网球规则、圈X配置➜限免及TF推送、共享账号➜苹果越狱情报、科技资讯➜安卓电脑资讯吃瓜啥都发 |
| [Telegram抽奖活动导航(Cnlottery)](https://t.me/Lottery_home) | 方便好用、公平公正的Telegram群组抽奖工具                     |
| [小声读书](https://t.me/weekly_books)                        | 小声读书是一个探索数字阅读可能性和未来的开放项目，致力于打破信息茧房，挖掘价值信息。亦是一份杂志，一个博客，混搭不拘一格，时常荒腔走板 |
| [少数派sspai](https://t.me/sspai)                            | 少数派(sspai.com)官方频道                                    |
| [表情包贴纸](https://t.me/tiezhia)                           | 电报专业贴纸、表情包分享                                     |
| [心情文案吧](https://t.me/WenAnBa)                           | 🌸心心念念是旧人🌸🌸笔笔写下是旧情🌸文案，壁纸，头像！每日更新，你的关注，是我最大的动力！ |
| [精品软件分享](https://t.me/pj_cn)                           | 初心软件分享频道                                             |
| [阿里云盘资源](https://t.me/zaihuayun)                       | 阿里云盘资源                                                 |
| [好书分享频道](https://t.me/Bookworm_Bibliophile)            | 读书，找到更美的世界与生活。不定期分享收集的好书好资料。     |
| [好软分享](https://t.me/haoruanfenxiang)                     | 好软分享                                                     |
| [Emby影视资源发布](https://t.me/Plus_Movie_Best)             | 普拉斯影业资源发布频道                                       |
| [TKDASHEN](https://t.me/tkdashen)                            | Apple精品破解软件Apple精品资源分享                           |
| [[读书]每天读本书/好书分享](https://t.me/sharebooks4you)     | 电子书丨好文丨佳句丨书摘丨音乐📚每日分享好书                  |
| [纽约时报全文实时推送](https://t.me/niuyueshibao_rss)        | 知乎日报纽约时报                                             |
| [APPDO数字生活指南](https://t.me/appdodo)                    | 💡互联网/数码/App/羊毛/相机/数字指南                          |
| [电子书小说漫画资源分享交流频](https://t.me/ziyuanfeng59)    | 精品电子书漫画小说资源分享交流频道                           |
| [抖音短视频](https://t.me/TiktokA3)                          | 小视频短视频                                                 |
| [每日消费电子观察](https://t.me/CE_Observe)                  | 每日消费电子观察                                             |
| [电子书](https://t.me/dianzhishu)                            | 🔥电子书🔥资源收集自网络                                       |
| [币圈财经新闻](https://t.me/Btc_789)                         | CoinNews社群导航                                             |
| [胖虎の收藏夹](https://t.me/gitbig)                          | 佛系更新，整合关联，收藏实用资源。拒绝焦虑，长期维护，每日更新节点。 |
| [某不知名杂货铺](https://t.me/youthkinga)                    | 某不知名杂货铺，记得看置顶本频道所有应用仅用于学习用途，禁止商用，请于下载后24小时内删除 |
| [Galgame频道](https://t.me/Galgamer_Channel)                 | Galgame资讯和推荐你                                          |
| [秋名山一路向北](https://t.me/ae86_ios)                      | 自己砸壳注入或网络收集的一些ipa，频道内App只保证支持TrollStore |
| [上班划水之沙雕图](https://t.me/goworkbitch)                 | 活干完了吗？还在玩手机！                                     |
| [严选君综合福利社](https://t.me/yxzbp)                       | 每天利用摸鱼时间给你们爱发电，只发精品，做一个精品的白嫖频道 |
| [油油分享频道](https://t.me/youyousharechannel)              | 分享开源、优秀的软件，有趣、实用的网站资源                   |
| [电报指南&精品排行榜](https://t.me/TgTrillion)               | 电报指南&精品排行榜链接                                      |
| [白嫖联盟资源分享频道](https://t.me/iOSQuQ)                  | 加速器/apk/ipa/TF/限免/教程/破解/软件/资源/网站群组          |
| [煎蛋无聊图](https://t.me/jandan_pic)                        | 自动抓取煎蛋首页推荐无聊图及其评论数据                       |
| [蓝光影音频道](https://t.me/voidrss)                         | 蓝光影音频道                                                 |
| [李老斯分享社](https://t.me/hgofxs)                          | 一个每天更新优质资源的白嫖综合频道，毫无保留的分             |
| [计算机类书籍](https://t.me/bookusefor3)                     | 收集偏计算机专业化的书籍系列频道普通休闲书籍资源计算机与部分其他种类书籍资源 |
| [即刻精选](https://t.me/jike_collection)                     | 精选即刻App热门话题更新                                      |
| [破解软件｜教程｜资源｜电影｜线报｜羊毛线报福利频道](https://t.me/sunpojie) | 👗白菜价商品，👄破解软件电视剧，🐏褥羊毛学习资源，🌊最新线报磁力🧲工具，🌍京东优惠券，淘宝优惠券 |
| [频道藏馆](https://t.me/channelhall)                         | 收藏TG频道、群组、机器人                                     |
| [乌鸦观察](https://t.me/bigcrowdev)                          | 不定期推送新闻和杂谈                                         |
| [外滩读书会-最新报纸、杂志、财经报告及流行电子书分享](https://t.me/readingclubus) | 以英文为主的报纸、杂志、电子书及财经报告分享，比如华尔街日报、金融时报、经济学人、哈佛商业评论、福布斯杂志、彭博商业评论、巴伦周刊等等更多资源分享。 |
| [LIHAIChannel](https://t.me/lihaiba)                         | 一个分享频道，不定时不定量更新                               |
| [微信搬运工（旧）](https://t.me/WeChatEssence)               | 本频道两个目的，1.丰富电报上的中文内容（不可否认还是有很多非政治的优质内容在微信公众号里），2.有些微信的内容分享了之后就和谐了，本频道可以做个备份。试运营中，欢迎订阅。目前对于超长文章（超过三万字的）只能发前一部分，剩余内容请参阅原文链接。特别声明：转发不代表支持，完全是机器人处理。友情频道：蛋挞报 |
| [薅羊毛情报](https://t.me/BaccanoSoul)                       | 互联网优质羊毛资源共享集社                                   |
| [iOS优质应用](https://t.me/iospremiumapps)                   | 分享iOS、macOS限免信息，免费使用正版应用                     |
| [苓妹妹ios资源分享](https://t.me/iosfulishare)               | 安卓免费破解频道                                             |
| [书屋电子书](https://t.me/TGeBook)                           | 电子书杂志小说期刊读物不定时更新                             |
| [Yummy](https://t.me/GodlyNews1)                             | 本频道不定期推送科技数码类新资讯                             |
| [计算机与部分其他种类书籍资源](https://t.me/bookusefor2)     | 收集一些与互联网相关或自己觉得有价值的书籍系列频道普通休闲书籍资源计算机与部分其他种类书籍资源 |
| [肯德基4K电影发布频道](https://t.me/XiangxiuNB)              | 主要分享最新的电影资源与资讯                                 |
| [小果子｜专业iOS破解软件分享](https://t.me/ioskkcc)          | 专注于iOS软件破解，本频道软件永不收费                        |
| [有故事的女同学](https://t.me/WenAnGuan_botjihuo)            | 网易云热评                                                   |
| [朱颜别镜妹子图美女图](https://t.me/meizitu3)                | 全网美女,妹子图收藏最是人间留不住,朱颜辞镜花辞树             |
| [程序员资源分享频道](https://t.me/gotoshare)                 | 程序员资源分享频道                                           |
| [PDF图书联盟电子书ebook](https://t.me/PDFtushuguan)          | 无规律无方向的持续分享一些书目，以及资源和有趣的内容         |
| [chatGPT中文社区](https://t.me/LptTech)                      | AI一年，人间十年                                             |
| [PT资讯频道](https://t.me/privatetrackernews)                | PT资讯推送                                                   |
| [资源福利分享](https://t.me/freemorebest)                    | 每天更新各类影视剧集网盘资源、福利活动、实用软件等           |
| [拾趣](https://t.me/peekfun)                                 | 分享一点有趣的事情、有用的东西                               |
| [不求甚解](https://t.me/fakeye)                              | 在这里分享我日常的所见所思                                   |
| [如有乐享](https://t.me/ruyoblog)                            | 要更新如有乐享博客内容，以及其他几个朋友的频道干货。偏云服务器 |
| [AppinnFeed](https://t.me/appinnfeed)                        | 这里有小众软件和发现频道的内容更新                           |
| [飞享一刻｜频道](https://t.me/w37fhy)                        | 飞享一刻｜频道                                               |
| [PDF资料](https://t.me/pdf_001)                              | 读秀/超星/全国图书馆咨询联盟/百度文库全网资料                |
| [赚客吧有奖一起赚](https://t.me/zuanke8)                     | 全网电商平台，优惠促销打折海淘BUG价活动线报，各大支付APP支付活动折扣及时推送，京东、苏宁、淘宝、天猫、国美，你能想到的这里都有，火速入伙！ |
| [Telegram 中文频道](https://t.me/tgcnz)                      | Telegram 中文/汉化/知识/教程, 科技                           |
| [每日沙雕墙](https://t.me/woshadiao)                         | 每日沙雕墙                                                   |
| [飞鱼资源分享](https://t.me/feiyu123)                        | 分享一些工具，软件，网站,歌曲，互联网相关资讯，开源项目，碎碎念的想法 等等。 |



## 群组



> 公共电报群组推荐，加入群组时建议查看置顶内容和群规，避免违规被拉黑




| 群组                                                         | 简介                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [西西书屋精校电子书](https://t.me/xixishuwu)                 | 📖西西书屋-精品电子书搜索服务                                 |
| [Koolcentermerlinfirmware](https://t.me/xbchat)              | 华硕、网件路由器Merlin第三方固件讨论群                       |
| [GoogleDrive无限容量](https://t.me/google_drive)             | 本群提供无限容量GoogleDrive申请方法、大电影小电影电子书无损音乐等资源 |
| [Python中文交流](https://t.me/pythonzh)                      | 分享心得，共同进步                                           |
| [资源搜索](https://t.me/sssoou_resource)                     | 这是一个帮助你节省时间，高效获取资源的地方。输入关键字，搜索tg上的资源，多个关键字用空格分开 |
| [wikipedia-zh](https://t.me/wikipedia_zh_n)                  | 本群組為中文維基百科聊天室，主要讨论维基百科站务             |
| [TikTok抖音自媒体交流群](https://t.me/tiktok520)             | tiktok电报最大抖音自媒体短视频活跃粉丝交流社区抖音自媒体     |
| [好音乐搜索在线听歌](https://t.me/haoyybots)                 | 好音乐在线听歌                                               |
| [GoogleVoice交流群](https://t.me/googlevoice)                | 讨论GoogleVoice号码使用的方法、技巧，以及提供相关服务资讯、商家介绍等不允许任何推广 |
| [RouterGroup软路由硬路由](https://t.me/ruanlu)               | 软路由硬路由                                                 |
| [iBeta尝鲜派官方群](https://t.me/ibetame)                    | iBeta尝鲜派（BetaHub.cn）的官方群组                          |
| [Notion中文社区](https://t.me/Notionso)                      | 以Notion为主，围绕Notion效率工具、经验为辅。核心围绕提升个人生活、工作效率来进行讨论 |
| [V2EX交流群](https://t.me/V2EXPro)                           | 程序员、分享创造、问与答                                     |
| [小声读书](https://t.me/what_youread)                        | 小声读书是一个探索数字阅读可能性和未来的开放项目，致力于打破信息茧房，挖掘价值信息 |
| [北京](https://t.me/beijingz)                                | 北京                                                         |
| [Synology/黑群晖用户群](https://t.me/nasfan)                 | 更多教程请访问论坛https://www.openos.org                     |
| [黑科技软件资源分享交流群](https://t.me/blacktechsharing)    | 分享免费实用高效率网络资源、黑科技软件、实用黑技巧           |
| [影视搜索](https://t.me/VodStore)                            | 电影、电视剧、综艺、体育、动漫、韩剧、美剧、国产剧           |
| [Java编程语言](https://t.me/Javaer)                          | Java一种物件导向程式设计编程语言                             |
| [电子书，小说，漫画资源分享](https://t.me/ziyuanfengxiang59) | 电子书，小说，漫画资源分享                                   |
| [iTunesGiftCards](https://t.me/iTunesGift)                   | 在这里讨论美区，港区，日区App/礼品卡代购                     |
| [NewlearnerGroup](https://t.me/NewlearnerGroup)              | 以IT话题为主，包括但不局限于开源分享、硬件&操作系统技术讨论、消费数码电子相关话题 |
| [Zapro·杂铺](https://t.me/tmioeTG)                           | 影视软件                                                     |
| [读舍-享受阅读时光](https://t.me/shufm)                      | 分享书摘与心得-分享讲座、读书会等信息-言论友善，平等互助     |
| [好棒羊毛超级搜](https://t.me/dajiajia)                      | 羊毛超级搜群组                                               |
| [Docker](https://t.me/dockertutorial)                        | Docker学习                                                   |
| [C++中文交流](https://t.me/cpluspluszh)                      | C++中文交流                                                  |
| [苹果用户交流群](https://t.me/Balancer996)                   | 鼓励有价值的内容、有深度的思考-鼓励友善、互相帮助、努力学习的氛围-分享沉淀 |
| [广州](https://t.me/guangzhouz)                              | 广州                                                         |
| [AppinnTalk](https://t.me/appinn)                            | 小众软件appinn.com                                           |
| [全球主机交流中心](https://t.me/VPSchat)                     | 全球主机交流中心                                             |
| [美剧电影吧](https://t.me/meijukingdom)                      | 最新美剧日剧韩剧泰剧电影交流                                 |
| [Go](https://t.me/GolangCN)                                  | Go                                                           |
| [Apps推荐&抽奖&活动](https://t.me/AppsSweepstakes)           | 佛系推荐APPs，为开发者与用户搭建桥梁！无费用！欢迎开发者来撩频道 |
| [AppleTV](https://t.me/AppleTVPlus)                          | AppleTV用户交流群                                            |
| [羊毛党--TG支部](https://t.me/cn_coupon)                     | 薅死羊不偿命系列                                             |
| [APPDO数字娱乐版](https://t.me/appdododo)                    | 💡科技/数码/App/互联网羊毛/数字指南                           |
| [Ubuntu中文](https://t.me/ubuntuzh)                          | Ubuntu中文交流群                                             |
| [CoderOfftopic中文群](https://t.me/coder_ot)                 | 讨论编程                                                     |
| [GoogleVoice互拨交流群](https://t.me/zh_GV)                  | 💚本群讨论GV相关话题，以及互拨保号                            |
| [C语言中文交流](https://t.me/Clanguagezh)                    | C是一种通用的程式語言，广泛用于系统软件与应用软件的开发      |
| [Pinapps](https://t.me/PinTG)                                | 在这里讨论Pin和JSBox等应用                                   |
| [读书分享](https://t.me/dushufenxiang_chat)                  | 读书分享，影视音乐，科学自然，旅游轶事，人生感悟，社会话题   |
| [Tg云音乐](https://t.me/Tgsongs)                             | 全球无限音乐资源Telegram听歌、找歌、交流等                   |
| [Vultr用户群](https://t.me/vultr_group)                      | Vultr用户群，非官方Vultr                                     |
| [iOS](https://t.me/iOSdevotee)                               | iOS                                                          |
| [NSXboxPSPC游戏闲聊](https://t.me/NintendoSwitchCN)          | 我们一起来游戏本群不欢迎任何广告，专注NS主机、Xbox主机和游戏若干年 |
| [内涵段子之闲聊群](https://t.me/OverseasChinese)             | 狼人杀群:猜大小,21点,赛马等游戏群:糗事百科:笑掉大牙:纯文字段子 |
| [腾讯云阿里云](https://t.me/TencentAliyun)                   | 欢迎加入阿里云☆腾讯云tg群频道推荐                            |
| [OpenWrtDiscuss](https://t.me/ctcgfw_openwrt_discuss)        | OpenWrt                                                      |
| [Cloudflare在中国](https://t.me/CN_Cloudflare)               | Cloudflare在中国的用户                                       |
| [zread读书会](https://t.me/zread)                            | 读书会                                                       |
| [Tg攝影社群](https://t.me/photographyintelegram)             | 電報攝影群組                                                 |
| [HBOSpotifyHulu](https://t.me/zxc1017yyfx)                   | 流媒体                                                       |
| [精选淘宝JD优惠卷](https://t.me/taobaojuan)                  | 羊毛超级搜群组                                               |
| [加密货币爱好者](https://t.me/twittercryptofans)             | 价值投资，长线，不加杠杆不做合约                             |
| [爱奇艺腾讯视频优酷VIP会员共享账号](https://t.me/share_video_vip) | 爱奇艺腾讯视频优酷VIP会员共享账号                            |
| [主机群](https://t.me/zhenggui)                              | 主机群（VPS、独立服务器、虚拟主机、域名等）本群为新手向      |
| [剧小二影视搜索交流群](https://t.me/HanJuSouSuo)             | 音乐搜索影视发布                                             |
| [JavaScript中文交流](https://t.me/javascriptzh)              | JavaScript，通常缩写为JS，是一种高级的，解释执行的编程语言   |
| [AndroidDev](https://t.me/AndroidDevCn)                      | Android开发话题                                              |
| [电影院线](https://t.me/zerodegroup)                         | 影视资源                                                     |
| [FaangbbsAPP北美程序员大群](https://t.me/faangbbs)           | telegram北美程序员大群                                       |
| [中英语言学习](https://t.me/LinguisticAcademy)               | 汉语和英语的学习                                             |
| [python自学交流](https://t.me/P_Y_T_H_O_N)                   | 学习、分享、成长                                             |
| [图拉丁](https://t.me/lajilao)                               | 图拉丁                                                       |
| [Luckydesigner知识分享群](https://t.me/luckydesignerspace)   | 影视平台                                                     |
| [智能手机讨论组](https://t.me/M_Phone)                       | 智能手机讨论组，主要讨论各种手机                             |
| [小米玩机交流群](https://t.me/xiaomi6666)                    | 小米玩机交流群                                               |
| [[好读]ReadFine交流总群](https://t.me/ReadfineChat)          | 好读提供电子书一站式阅读体验                                 |
| [开放世界手游聚集地](https://t.me/Orz_zayu)                  | 开放世界手游聚集地                                           |
| [CoPuppy(DawnWars)-中文愛好者群](https://t.me/copuppy_bsc_chinese) | CoPuppy致力於擴展NFT的使用場景，包含遊戲，金融，收藏等多個概念 |
| [翻译机器人讨论](https://t.me/fanyi_group)                   | 中文翻译机器人讨论群                                         |
| [科技閒聊群組](https://t.me/tech_TW)                         | 歡迎大家加入閒聊科技                                         |
| [简悦-SimpRead](https://t.me/simpreadgroup)                  | 嗨，谢谢使用简悦，欢迎加入简悦                               |
| [期货与期权](https://t.me/CNderivatives)                     | 期货、期权和各类金融交易品的投机与套利电报上最大的衍生品中文讨论群股票 |
| [读者争鸣](https://t.me/duzhe)                               | 优质的读书生活交流群。请理性客观友好讲真话                   |
| [浥轻尘の交流群组](https://t.me/yqc_666)                     | ✅聊天交流群组👨🏻‍💻🍟资源分享频道🤖😍美女写真套图🎆                 |
| [电影爱好者交流组](https://t.me/Moviemarket_group)           | 索片请提供电影详细信息                                       |
| [加密货币与区块链讨论群](https://t.me/onBlockchain)          | 加密货币与区块链频道                                         |
| [WallStreetBets华尔街中文官方交流群](https://t.me/WSBetsZH)  | 华尔街中文官方交流群                                         |
| [維基百科科技與科學群](https://t.me/wikipedia_zh_science_and_tech) | 維基百科科技與科學群                                         |
| [RaspberryPi讨论群](https://t.me/raspicn)                    | RaspberryPi讨论群                                            |
| [CentOS中文](https://t.me/centoszh)                          | CentOS中文                                                   |
| [大虾的编程资源交流群](https://t.me/programmingsrchubgroup)  | 大虾的编程资源库/码农/程序员资源高质量交流群                 |
| [奇点](https://t.me/jidian)                                  | 面向奇点用户的群组                                           |
| [大数据杂谈](https://t.me/bigdatazh)                         | 大数据架构与开发技术交流不卖数据                             |
| [北美矿业](https://t.me/beimei999)                           | 比特币，以太坊，FIL，空投                                    |
| [频道源福利分享Chat](https://t.me/freemorebestchat)          | 每天更新各类影视剧集网盘资源、福利活动、实用软件等           |
| [中国矿工群](https://t.me/chinaminerclub)                    | 最正宗的中文矿工交流群，矿机、矿场、矿池、矿工，矿圈所有生态，一个群就搞定 |
| [iGame游戏交流群](https://t.me/gamecn)                       | 天下玩家是一家。这里是游戏爱好者的交流群                     |
| [Amazon海淘购物交流群](https://t.me/firstAmazon)             | 美亚(美国亚马逊)代购、拼单、转运、优惠劵、FireTVStick团购、海淘交流 |
| [新加坡交流](https://t.me/TGM00002)                          | 新加坡、工作、招聘、求职、咨询、交流                         |
| [Frontend前端中文技术交流](https://t.me/frontend_talk)       | 前端中文技术交流                                             |
| [CSGO](https://t.me/csgocn)                                  | CS:GO中文群组关联频道                                        |
| [Kevin自留地](https://t.me/mrkevinh)                         | 主要内容为主机、技术、羊毛等一切                             |
| [数理化生实验室](https://t.me/mpcblab)                       | 理科学科(数学/物理/化学/生物/天文和其他自然科学)相关话题交流群 |
| [豆瓣小组](https://t.me/doubanners)                          | 电影、文学、哲学、音乐等艺术和人文科学。亦可以资源共享       |
| [Telegram 中文社群](https://t.me/tgcnx)                      | Telegram 中文/汉化/知识/教程, 科技, 机场                     |


## 机器人



> 好用和好玩的电报机器人推荐




| 机器人                                                  |
| ------------------------------------------------------- |
| [酷群导航](https://t.me/kuqun_bot)                      |
| [頻道群組索引機器人](https://t.me/tg_chs_bot)           |
| [Bing词典](https://t.me/bingdict_bot)                   |
| [RSS屋](https://t.me/RSSWBot)                           |
| [Telegram抽奖助手](https://t.me/cnLottery_bot)          |
| [和风天气小棉袄](https://t.me/he_weather_bot)           |
| [网易云音乐ncm转换器](https://t.me/netease_ncm_bot)     |
| [一起搜电影](https://t.me/Cctv365bot)                   |
| [TGCN-CAPTCHA加群验证](https://t.me/tgcnjoincaptchabot) |
| [频道助手](https://t.me/septs_autoclean_bot)            |
| [好音乐搜索](https://t.me/haoyybot)                     |
| [智能合租机器人](https://t.me/daixiahu_bot)             |
| [Telegram抽奖助手](https://t.me/cnLottery123_bot)       |
| [小掌萌](https://t.me/sauweenbot)                       |
| [中文趣群搜索机器人](https://t.me/ququn_bot)            |
| [中文频道群组导航机器人](https://t.me/sousuo_bot)       |
| [GIF出处查询机器人](https://t.me/TumblrAce_bot)         |
| [词云机器人](https://t.me/iWordCloudBot)                |



## 风险提示

Telegram 上的频道/群/机器人中的内容，有很多是难以辨别的假信息。很多频道/群里面的提供软件要谨慎下载！！！发布的链接要谨慎点击！！！以防遭受损失！！！

## 免责声明
本项目的所有内容均来源于网络，只作为学习和研究使用。本项目中列出的频道/群组/机器人等，可能包含部分敏感内容。请自觉遵守当地有关法律法规，所产生的一切后果，本项目概不负责！如有内容侵犯了您的权益，请联系删除相关内容。


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=alexbei/telegram-groups&type=Date)](https://star-history.com/#alexbei/telegram-groups&Date)

