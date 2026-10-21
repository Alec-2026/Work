select
    *
from prompt_customer_aware
order by time desc;

--
select
    business_name, count(1) as cnt, count(distinct version)
from prompt_customer_aware
group by business_name
order by cnt desc;