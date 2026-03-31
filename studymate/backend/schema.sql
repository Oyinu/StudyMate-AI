-- ================================================================
-- StudyMate AI — Supabase Database Schema
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- ================================================================

-- 1. USERS TABLE
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  email text unique not null,
  password_hash text not null,
  created_at timestamp with time zone default now()
);

-- 2. DOCUMENTS TABLE (uploaded PDFs)
create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  filename text not null,
  storage_path text,
  file_url text,
  extracted_text text,
  char_count integer default 0,
  created_at timestamp with time zone default now()
);

-- 3. QUIZZES TABLE
create table if not exists quizzes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  document_id uuid references documents(id) on delete set null,
  title text not null,
  difficulty text default 'medium' check (difficulty in ('easy', 'medium', 'hard')),
  num_mcq integer default 0,
  num_theory integer default 0,
  questions jsonb not null,
  is_shared boolean default false,
  created_at timestamp with time zone default now()
);

-- 4. RESULTS TABLE
create table if not exists results (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  quiz_id uuid references quizzes(id) on delete cascade,
  mcq_score integer default 0,
  total_mcq integer default 0,
  mcq_percentage integer default 0,
  grade text default 'F',
  time_taken_seconds integer default 0,
  time_display text,
  theory_answers jsonb,
  mcq_feedback jsonb,
  submitted_at timestamp with time zone default now()
);

-- ================================================================
-- ROW LEVEL SECURITY (RLS) — Recommended for Supabase
-- ================================================================

alter table users enable row level security;
alter table documents enable row level security;
alter table quizzes enable row level security;
alter table results enable row level security;

-- Users can only read/update their own profile
create policy "Users: own data only" on users
  for all using (auth.uid()::text = id::text);

-- Documents: owner access only
create policy "Documents: owner only" on documents
  for all using (user_id::text = auth.uid()::text);

-- Quizzes: owner access, or shared quizzes are public
create policy "Quizzes: owner or shared" on quizzes
  for select using (user_id::text = auth.uid()::text or is_shared = true);

create policy "Quizzes: owner write" on quizzes
  for insert with check (user_id::text = auth.uid()::text);

create policy "Quizzes: owner update" on quizzes
  for update using (user_id::text = auth.uid()::text);

-- Results: owner only
create policy "Results: owner only" on results
  for all using (user_id::text = auth.uid()::text);

-- ================================================================
-- STORAGE BUCKET — Run in Supabase Dashboard → Storage
-- Create a bucket named: studymate-pdfs
-- Set it to Public or Private based on your preference
-- ================================================================
