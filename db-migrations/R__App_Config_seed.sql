insert into app.config (name, value)
  values ('records_to_export', 200)
  on conflict(name)
  do
    update set value = 200;
