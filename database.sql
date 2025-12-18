-- PSYPREDICT - FULL DATABASE SCHEMA

-- 1. Create 'conversations' table
create table public.conversations (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  title text
);

-- 2. Create 'messages' table
create table public.messages (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) not null,
  conversation_id uuid references public.conversations(id), 
  content text not null,
  metadata jsonb, 
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. Create 'profiles' table (Decoupled from auth.users to prevent Race Conditions)
-- Note: 'id' will still match auth.users(id) logic-wise, but we remove the strict constraint
create table public.profiles (
  id uuid primary key, 
  updated_at timestamp with time zone,
  full_name text,
  avatar_url text,
  email text,
  password_hash text 
);

-- 4. Enable Row Level Security (RLS)
alter table public.conversations enable row level security;
alter table public.messages enable row level security;
alter table public.profiles enable row level security;

-- 5. RLS Policies for Conversations
create policy "Users can view their own conversations"
  on public.conversations for select using (auth.uid() = user_id);

create policy "Users can insert their own conversations"
  on public.conversations for insert with check (auth.uid() = user_id);

create policy "Users can update their own conversations"
  on public.conversations for update using (auth.uid() = user_id);

create policy "Users can delete their own conversations"
  on public.conversations for delete using (auth.uid() = user_id);

-- 6. RLS Policies for Messages
create policy "Users can view their own messages"
  on public.messages for select using (auth.uid() = user_id);

create policy "Users can insert their own messages"
  on public.messages for insert with check (auth.uid() = user_id);

create policy "Users can delete their own messages"
  on public.messages for delete using (auth.uid() = user_id);

-- 7. RLS Policies for Profiles
-- Allow public read (for basic info) or restrict to owner depending on needs
create policy "Public profiles are viewable by everyone" 
  on public.profiles for select using (true);

-- Allow ANY insert to support the signup flow fallback
-- Security is maintained by PK uniqueness (id)
create policy "Allow insert for profile creation" 
  on public.profiles for insert with check (true);

-- Only owner can update
create policy "Users can update own profile" 
  on public.profiles for update using (auth.uid() = id);

-- 8. Grant Permissions
grant all on public.profiles to postgres, anon, authenticated, service_role;