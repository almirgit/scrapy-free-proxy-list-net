begin;
do
$$
declare
  l_cnt int;
  l_value text;
  l_listen_address text;
begin

  create table if not exists public.dbinfo(
    id serial primary key,
    key text not null,
    value text
  );

  -- Environment:
  l_listen_address := inet_server_addr()::text;
 
  if l_listen_address = '91.92.136.221/32' then
    l_value := 'STAGING';
  elsif l_listen_address = '188.34.206.113/32' then
    l_value := 'PRODUCTION';
  else
    l_value := 'DEV';
  end if;

  update public.dbinfo set
    value = l_value
  where key = 'ENV';

  get diagnostics l_cnt := row_count;
  if l_cnt = 0 then 
    insert into public.dbinfo (key, value) values ('ENV', l_value);
  end if;


  -- App name:
  l_value := 'scrapy-free-proxy-list-net';
  update public.dbinfo set
    value = l_value
  where key = 'APP_NAME';

  get diagnostics l_cnt := row_count;
  if l_cnt = 0 then 
    insert into public.dbinfo (key, value) values ('APP_NAME', l_value);
  end if;
  
end;
$$;
