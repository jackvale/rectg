-- 查询 按人数排序结果
SELECT tg_url                                                                                      as 地址,
       tg_name                                                                                     as 名称,
       tg_desc                                                                                     as 简介,
       tg_person_num                                                                               as 人数,
       tg_category                                                                                 as 类型,
       ROW_NUMBER() OVER ( PARTITION BY tg_category ORDER BY tg_person_num DESC,tg_category DESC ) as 排名
FROM jack_github_md
WHERE tg_category IS NOT NULL