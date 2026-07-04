-- NomadShare - Supabase Schema

create table if not exists users (
    user_id bigint primary key,
    username text,
    first_name text,
    is_admin boolean default false,
    is_verified boolean default false,
    joined_date timestamptz default now(),
    total_files integer default 0
);

create table if not exists files (
    id uuid primary key,
    file_id text not null,
    file_name text,
    file_size bigint,
    file_type text,
    category text default 'document',
    uploaded_by bigint references users(user_id),
    upload_date timestamptz default now(),
    expiry_date timestamptz,
    access_count integer default 0,
    is_public boolean default true,
    short_url text
);

create table if not exists links (
    id uuid primary key,
    file_id uuid references files(id) on delete cascade,
    short_code text unique,
    full_url text,
    created_date timestamptz default now(),
    access_count integer default 0,
    is_active boolean default true
);

-- Key/value store used for the /mode toggle (defaults to 'private' if empty)
create table if not exists bot_settings (
    key text primary key,
    value text
);
