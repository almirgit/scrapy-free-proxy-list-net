# scrapy-free-proxy-list-net container

This containter contains program that scrapes https://free-proxy-list.net/ site and store scraped proxy info into the DB

## Configuration

Place DB configuration into /var/scrapy-free-proxy-list-net/config/.secret.yml on the docker host machine:

Example:
```
pgdb_host: db1.example.com
pgdb_port: 5432
pgdb_name: proxy_db1
pgdb_user: proxy_user1
pgdb_pass: gq71p6he2OqqQtF0glPRbRIRM0DLHaRt
```

Scraped records gets stored in DB table "data.proxy_list", and in parallel being exported to a CSV file at the host machine: 
```/var/scrapy-free-proxy-list-net/data/proxy_list.csv```