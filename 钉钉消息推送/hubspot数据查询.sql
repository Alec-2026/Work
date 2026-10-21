WITH get_contacts_table AS (
    SELECT
        JSONExtractString(ifNull(attr, '{}'), 'task_id') AS task_id,
        JSONExtractString(ifNull(attr, '{}'), 'section') AS section,
        toInt32OrZero(JSONExtractString(ifNull(attr, '{}'), 'contact_count')) AS contact_count,
        JSONExtractString(ifNull(attr, '{}'), 'use_time') AS use_time,
        JSONExtractArrayRaw(ifNull(attr, '{}'), 'contacts_ids') AS contacts_ids,
        JSONExtractArrayRaw(ifNull(attr, '{}'), 'gen_mail_status') AS gen_email_status,
        toDateTime(time) AS time,
        toDate(time) AS date
    FROM tag_independent_station_hubspot_transit
    where section = '获取联系人'
), gen_email_contacts_table AS (
    SELECT
        JSONExtractString(ifNull(attr, '{}'), 'task_id') AS task_id,
        toDateTime(time) AS time,
        toDate(time) AS date,
        JSONExtractString(ifNull(attr, '{}'), 'section') AS section,
        toInt32OrZero(JSONExtractString(ifNull(attr, '{}'), 'contact_count')) AS contact_count,
        JSONExtractString(ifNull(attr, '{}'), 'use_time') AS use_time,
        JSONExtractArrayRaw(ifNull(attr, '{}'), 'contacts_ids') AS contacts_ids,
        JSONExtractArrayRaw(ifNull(attr, '{}'), 'gen_mail_status') AS gen_email_status
    FROM tag_independent_station_hubspot_transit
    where section = '生成邮件'
), gen_email_detail_table as (
    SELECT
        task_id,
        replaceAll(contact_id, '"', '') as id,
        replaceAll(email_status, '"', '') as status,
        time
    FROM gen_email_contacts_table
        ARRAY JOIN
         contacts_ids AS contact_id,
         gen_email_status AS email_status
), upload_contacts_table AS (
    SELECT
        JSONExtractString(ifNull(attr, '{}'), 'task_id') AS task_id,
        JSONExtractString(ifNull(attr, '{}'), 'section') AS section,
        toInt32OrZero(JSONExtractString(ifNull(attr, '{}'), 'contact_count')) AS contact_count,
        JSONExtractString(ifNull(attr, '{}'), 'use_time') AS use_time,
        JSONExtractArrayRaw(ifNull(attr, '{}'), 'contacts_ids') AS contacts_ids,
        JSONExtractArrayRaw(ifNull(attr, '{}'), 'gen_mail_status') AS gen_email_status,
        toDateTime(time) AS time,
        toDate(time) AS date
    FROM tag_independent_station_hubspot_transit
    where section = '上传邮件'
), ana_detail_table as (
    select
        aa.task_id as task_id,
        aa.date as date,

        aa.contact_count as get_contact_count,
        aa.time as start_time,

        bb.contact_count as upload_contact_count,
        bb.time as end_time,

        cc.id as user_id,
        cc.status as email_send_status
    from (
        select
            task_id,section,contact_count,use_time,contacts_ids,gen_email_status,time,date
        from get_contacts_table
    ) as aa
    left join (
        select
            task_id,section,contact_count,use_time,contacts_ids,gen_email_status,time,date
        from upload_contacts_table
    ) as bb on aa.task_id = bb.task_id
    left join (
        select
            task_id, id, status
        from gen_email_detail_table
    ) as cc on aa.task_id = cc.task_id
)


select
    tt1.date as date,
    `任务数量`,
    tt2.contact_count as `获取数量`,
    `Ready数量`,
    `Pending数量`,
    tt3.contact_count as `上传的数量`
from (
    -- 明细数据
         select
             date,
             count(distinct task_id) as `任务数量`,
             count(if(email_send_status=='Ready', user_id, null)) as `Ready数量`,
             count(if(email_send_status=='Pending', user_id, null)) as `Pending数量`
         from ana_detail_table
         group by date
) as tt1 left join (
    -- 获取的数量
    select
        date, sum(contact_count) as contact_count
    from get_contacts_table
    group by date
) as tt2 on tt1.date=tt2.date
left join (
    -- 上传的数量
    select
        date, sum(contact_count) as contact_count
    from upload_contacts_table
    group by date
) as tt3 on tt1.date=tt3.date
where tt1.date >= today() - 6
    and tt1.date >= '2026-09-15'
order by tt1.date desc
