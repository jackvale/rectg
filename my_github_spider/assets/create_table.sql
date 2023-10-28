/* Table: jack_github_md                                        */
/*==============================================================*/
create table jack_github_md (
   id                   BIGSERIAL            not null,
   tg_url               VARCHAR(255)         null,
   tg_name              VARCHAR(255)         null,
   tg_desc              VARCHAR(255)         null,
   tg_person_num        INT8                 null,
   tg_category          VARCHAR(50)          null,
   constraint PK_JACK_GITHUB_MD primary key (id)
);

comment on table jack_github_md is
'Jack Github README 的数据';

comment on column jack_github_md.id is
'ID';

comment on column jack_github_md.tg_url is
'地址';

comment on column jack_github_md.tg_name is
'名称';

comment on column jack_github_md.tg_desc is
'简介';

comment on column jack_github_md.tg_person_num is
'人数';

comment on column jack_github_md.tg_category is
'分类';