select * from products;
select * from order_items;
-- общее количество пользователей
select count(distinct name) as total_users from users;

-- общее количество заказов
select count(order_id) as total_orders from orders;

-- общее количество товаров
select count(product_id) as total_products from order_items;

-- средний чек
select round(avg(price), 2) as avg_price from products;

-- доходы по категориям
select p.category, sum(p.price * oi.quantity) as income from products as p
left join order_items as oi on(p.product_id = oi.product_id)
where oi.quantity is not null
GROUP by p.category;

select * from products;
select * from order_items;
select * from events;

-- смена типа на дату
alter table events
alter column event_date type date using event_date::date;

--воронка продаж общая
with tmp as (select 
count(distinct(
		case 
		when event = 'view' 
		then user_id 
		end)
		) as views,
count(distinct(
		case when event = 'cart'
		then user_id end)
		) as carts,
count(distinct(
		case when event = 'purchase'
		then user_id end)
		) as purchase
from events)
select views, carts, purchase, 
round(100*carts/views, 2) as cart_conver,
round(100*purchase/carts, 2) as purchase_conver,
round(100*purchase/views, 2) as total_conver
from tmp; 

-- воронка продаж по продуктам
with tmp as (select 
product_id,
count(distinct(
		case 
		when event = 'view' 
		then user_id 
		end)
		) as views,
count(distinct(
		case when event = 'cart'
		then user_id end)
		) as carts,
count(distinct(
		case when event = 'purchase'
		then user_id end)
		) as purchase
from events
group by product_id)
select product_id, views, carts, purchase, 
		round(100*carts/views, 2) as cart_conver,
		round(100*purchase/carts, 2) as purchase_conver,
		round(100*purchase/views, 2) as total_conver
from tmp
order by purchase desc;

-- количество заказов на пользователя, средний чек
select * from events;
select * from products;

select e.user_id, count(DISTINCT(e.product_id)),
round(avg(p.price),2) as avg_check
from events as e
left join products as p on(e.product_id = p.product_id)
where event = 'purchase'
group by e.user_id
ORDER by 2 desc,3 Desc
limit 5

select * from users;
-- количество первичных и повторных заказов у юзеров
with tmp as(
select 
user_id, event_date, event, product_id, 
row_number() over(PARTITION by user_id order by event_date) 
from events
where event = 'purchase'), 
classific as (
select 
user_id, 
case
	when row_number = 1 then 'first'
	else 'second'
	end as order_type
from tmp
), 
agg as (
select user_id,
count(*) FILTER (where order_type = 'first') as first,
count(*) FILTER (where order_type = 'second') as second
from classific
group by user_id
)
select 
u.user_id,
COALESCE(a.first, 0) as first_orders,
COALESCE(a.second, 0) as second_orders
from users as u
left join agg as a on(a.user_id = u.user_id);

-- частота повторных заказов
WITH tmp AS (
  SELECT 
    user_id, event_date, event, product_id, 
    ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY event_date) AS row_number
  FROM events
  WHERE event = 'purchase'
), 
classific AS (
  SELECT 
    user_id, 
    CASE
      WHEN row_number = 1 THEN 'first'
      ELSE 'second'
    END AS order_type
  FROM tmp
), 
agg AS (
  SELECT 
    user_id,
    COUNT(*) FILTER (WHERE order_type = 'first') AS first,
    COUNT(*) FILTER (WHERE order_type = 'second') AS second
  FROM classific
  GROUP BY user_id
),
all_users AS (
  SELECT 
    u.user_id,
    COALESCE(a.first, 0) AS first_orders,
    COALESCE(a.second, 0) AS second_orders
  FROM users u
  LEFT JOIN agg a ON u.user_id = a.user_id
)
SELECT 
  COUNT(*) AS total_users,
  COUNT(*) FILTER (WHERE second_orders > 0) AS repeat_buyers,
  ROUND(
    1.0 *COUNT(*) FILTER (WHERE second_orders > 0) / COUNT(*), 
    2
  ) AS repeat_rate
FROM all_users;

-- топ 10 самых покупаемых товаров
select product_id, count(*) from events
where event = 'purchase'
group by product_id
order by 2 desc
limit 10;

select * from products;
-- топ 10 самых просматриваемых товаров
select p.product_name, count(*) as view_count
from events as e
left join products as p on(e.product_id = p.product_id)
where event = 'view'
group by p.product_id
order by 2 desc
limit 10;

select * from products;
select count(distinct(event_date)) from events;

-- сумма продаж по дате
select 
e.event_date, sum(p.price),
round(avg(p.price),2), count(*) 
from events as e
left join products as p on(e.product_id = p.product_id)
where e.event = 'purchase'
group by e.event_date
order by 1

