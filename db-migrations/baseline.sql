--
-- PostgreSQL database dump
--

-- Dumped from database version 11.20 (Debian 11.20-1.pgdg100+1)
-- Dumped by pg_dump version 13.11 (Debian 13.11-1.pgdg100+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: app; Type: SCHEMA; Schema: -; Owner: proxy_user
--

CREATE SCHEMA app;


ALTER SCHEMA app OWNER TO proxy_user;

--
-- Name: data; Type: SCHEMA; Schema: -; Owner: proxy_user
--

CREATE SCHEMA data;


ALTER SCHEMA data OWNER TO proxy_user;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

--CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

--COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

--CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

--COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: add_new_proxy(text, text, text, text, text); Type: FUNCTION; Schema: app; Owner: proxy_user
--

CREATE FUNCTION app.add_new_proxy(p_proxy_ip text, p_proxy_port text, p_country text DEFAULT NULL::text, p_anonymity text DEFAULT NULL::text, p_last_checked text DEFAULT NULL::text) RETURNS void
    LANGUAGE plpgsql
    AS $$
declare
  l_function_name text := 'app.load_new_proxy';
  l_proxy_list_retention int;
  --l_proxy_list_rowcnt int;
begin

  insert into data.proxy_list (proxy_ip, proxy_port, country, anonymity, last_checked)
    values (p_proxy_ip::inet, p_proxy_port::int, p_country, p_anonymity, p_last_checked)
  on conflict(proxy_ip, proxy_port)
  do
  update set
    country = p_country,
    anonymity = p_anonymity,
    last_checked = p_last_checked,
    moddate = now(),
    reload_count = data.proxy_list.reload_count + 1;


  l_proxy_list_retention := app.get_config('proxy_list_retention')::int;

  insert into data.proxy_list_archive
        (id, proxy_ip, proxy_port, country, anonymity, last_checked, loading_source, entdate, moddate, reload_count)
  select id, proxy_ip, proxy_port, country, anonymity, last_checked, loading_source, entdate, moddate, reload_count from
  (
    select
    row_number() over (order by moddate desc) rn,
    pl.*
    from data.proxy_list pl
  ) x
  where x.rn > l_proxy_list_retention;

  delete from data.proxy_list
    where id in
  (
    select id from
    (
      select
      row_number() over (order by moddate desc) rn,
      pl.*
      from data.proxy_list pl
    ) x
    where x.rn > l_proxy_list_retention
  );


end;
$$;


ALTER FUNCTION app.add_new_proxy(p_proxy_ip text, p_proxy_port text, p_country text, p_anonymity text, p_last_checked text) OWNER TO proxy_user;

--
-- Name: get_config(text); Type: FUNCTION; Schema: app; Owner: proxy_user
--

CREATE FUNCTION app.get_config(p_name text) RETURNS text
    LANGUAGE plpgsql
    AS $$
declare
  l_function_name text := 'app.get_config';
  l_context text;
  l_value text;
begin

  select value
  into l_value
  from app.config
  where name = p_name;

  return l_value;

exception when others then
  get stacked diagnostics l_context = pg_exception_context;
  perform app.log_message(l_function_name,
    sqlerrm::text || '; ' ||
    'context: ' || l_context,
    'ERROR');

  return null;
end;
$$;


ALTER FUNCTION app.get_config(p_name text) OWNER TO proxy_user;

--
-- Name: log_message(text, text, text); Type: FUNCTION; Schema: app; Owner: proxy_user
--

CREATE FUNCTION app.log_message(p_function_name text, p_message text, p_log_level text DEFAULT 'DEBUG'::text) RETURNS void
    LANGUAGE plpgsql
    AS $$
declare
begin
  insert into app.db_log (function_name, message, log_level)
    values (p_function_name, p_message, p_log_level);
end;
$$;


ALTER FUNCTION app.log_message(p_function_name text, p_message text, p_log_level text) OWNER TO proxy_user;

SET default_tablespace = '';

--
-- Name: config; Type: TABLE; Schema: app; Owner: proxy_user
--

CREATE TABLE app.config (
    id integer NOT NULL,
    name text NOT NULL,
    value text,
    description text
);


ALTER TABLE app.config OWNER TO proxy_user;

--
-- Name: config_id_seq; Type: SEQUENCE; Schema: app; Owner: proxy_user
--

CREATE SEQUENCE app.config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE app.config_id_seq OWNER TO proxy_user;

--
-- Name: config_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: proxy_user
--

ALTER SEQUENCE app.config_id_seq OWNED BY app.config.id;


--
-- Name: db_log; Type: TABLE; Schema: app; Owner: proxy_user
--

CREATE TABLE app.db_log (
    id bigint NOT NULL,
    log_date timestamp without time zone DEFAULT now() NOT NULL,
    log_level character varying(10) DEFAULT 'DEBUG'::character varying NOT NULL,
    function_name character varying(200),
    message character varying(4000)
);


ALTER TABLE app.db_log OWNER TO proxy_user;

--
-- Name: db_log_id_seq; Type: SEQUENCE; Schema: app; Owner: proxy_user
--

CREATE SEQUENCE app.db_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE app.db_log_id_seq OWNER TO proxy_user;

--
-- Name: db_log_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: proxy_user
--

ALTER SEQUENCE app.db_log_id_seq OWNED BY app.db_log.id;


--
-- Name: flyway_schema_history; Type: TABLE; Schema: app; Owner: proxy_user
--

CREATE TABLE app.flyway_schema_history (
    installed_rank integer NOT NULL,
    version character varying(50),
    description character varying(200) NOT NULL,
    type character varying(20) NOT NULL,
    script character varying(1000) NOT NULL,
    checksum integer,
    installed_by character varying(100) NOT NULL,
    installed_on timestamp without time zone DEFAULT now() NOT NULL,
    execution_time integer NOT NULL,
    success boolean NOT NULL
);


ALTER TABLE app.flyway_schema_history OWNER TO proxy_user;

--
-- Name: proxy_list; Type: TABLE; Schema: data; Owner: proxy_user
--

CREATE TABLE data.proxy_list (
    id bigint NOT NULL,
    proxy_ip inet NOT NULL,
    proxy_port integer NOT NULL,
    country text,
    anonymity text,
    last_checked text,
    loading_source text,
    entdate timestamp without time zone DEFAULT now() NOT NULL,
    moddate timestamp without time zone DEFAULT now() NOT NULL,
    reload_count integer DEFAULT 0 NOT NULL
);


ALTER TABLE data.proxy_list OWNER TO proxy_user;

--
-- Name: proxy_list_archive; Type: TABLE; Schema: data; Owner: proxy_user
--

CREATE TABLE data.proxy_list_archive (
    id bigint,
    proxy_ip inet,
    proxy_port integer,
    country text,
    anonymity text,
    last_checked text,
    loading_source text,
    entdate timestamp without time zone,
    moddate timestamp without time zone,
    reload_count integer
);


ALTER TABLE data.proxy_list_archive OWNER TO proxy_user;

--
-- Name: proxy_list_id_seq; Type: SEQUENCE; Schema: data; Owner: proxy_user
--

CREATE SEQUENCE data.proxy_list_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE data.proxy_list_id_seq OWNER TO proxy_user;

--
-- Name: proxy_list_id_seq; Type: SEQUENCE OWNED BY; Schema: data; Owner: proxy_user
--

ALTER SEQUENCE data.proxy_list_id_seq OWNED BY data.proxy_list.id;


--
-- Name: dbinfo; Type: TABLE; Schema: public; Owner: proxy_user
--

CREATE TABLE public.dbinfo (
    id integer NOT NULL,
    key text NOT NULL,
    value text
);


ALTER TABLE public.dbinfo OWNER TO proxy_user;

--
-- Name: dbinfo_id_seq; Type: SEQUENCE; Schema: public; Owner: proxy_user
--

CREATE SEQUENCE public.dbinfo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dbinfo_id_seq OWNER TO proxy_user;

--
-- Name: dbinfo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: proxy_user
--

ALTER SEQUENCE public.dbinfo_id_seq OWNED BY public.dbinfo.id;


--
-- Name: config id; Type: DEFAULT; Schema: app; Owner: proxy_user
--

ALTER TABLE ONLY app.config ALTER COLUMN id SET DEFAULT nextval('app.config_id_seq'::regclass);


--
-- Name: db_log id; Type: DEFAULT; Schema: app; Owner: proxy_user
--

ALTER TABLE ONLY app.db_log ALTER COLUMN id SET DEFAULT nextval('app.db_log_id_seq'::regclass);


--
-- Name: proxy_list id; Type: DEFAULT; Schema: data; Owner: proxy_user
--

ALTER TABLE ONLY data.proxy_list ALTER COLUMN id SET DEFAULT nextval('data.proxy_list_id_seq'::regclass);


--
-- Name: dbinfo id; Type: DEFAULT; Schema: public; Owner: proxy_user
--

ALTER TABLE ONLY public.dbinfo ALTER COLUMN id SET DEFAULT nextval('public.dbinfo_id_seq'::regclass);


--
-- Name: config config_pkey; Type: CONSTRAINT; Schema: app; Owner: proxy_user
--

ALTER TABLE ONLY app.config
    ADD CONSTRAINT config_pkey PRIMARY KEY (id);


--
-- Name: db_log db_log_pkey; Type: CONSTRAINT; Schema: app; Owner: proxy_user
--

ALTER TABLE ONLY app.db_log
    ADD CONSTRAINT db_log_pkey PRIMARY KEY (id);


--
-- Name: flyway_schema_history flyway_schema_history_pk; Type: CONSTRAINT; Schema: app; Owner: proxy_user
--

ALTER TABLE ONLY app.flyway_schema_history
    ADD CONSTRAINT flyway_schema_history_pk PRIMARY KEY (installed_rank);


--
-- Name: config name__uniq; Type: CONSTRAINT; Schema: app; Owner: proxy_user
--

ALTER TABLE ONLY app.config
    ADD CONSTRAINT name__uniq UNIQUE (name);


--
-- Name: proxy_list proxy_list__uniq1; Type: CONSTRAINT; Schema: data; Owner: proxy_user
--

ALTER TABLE ONLY data.proxy_list
    ADD CONSTRAINT proxy_list__uniq1 UNIQUE (proxy_ip, proxy_port);


--
-- Name: proxy_list proxy_list_pkey; Type: CONSTRAINT; Schema: data; Owner: proxy_user
--

ALTER TABLE ONLY data.proxy_list
    ADD CONSTRAINT proxy_list_pkey PRIMARY KEY (id);


--
-- Name: dbinfo dbinfo_pkey; Type: CONSTRAINT; Schema: public; Owner: proxy_user
--

ALTER TABLE ONLY public.dbinfo
    ADD CONSTRAINT dbinfo_pkey PRIMARY KEY (id);


--
-- Name: flyway_schema_history_s_idx; Type: INDEX; Schema: app; Owner: proxy_user
--

CREATE INDEX flyway_schema_history_s_idx ON app.flyway_schema_history USING btree (success);


--
-- PostgreSQL database dump complete
--

