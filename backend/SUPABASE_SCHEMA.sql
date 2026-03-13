-- Supabase SQL Schema for AI Data Cleaner SaaS
-- Copy and paste this into the Supabase SQL Editor to setup your database

-- ==================== USERS TABLE ====================
CREATE TABLE public.users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  password_hash text NOT NULL,
  full_name text NOT NULL,
  subscription_tier text DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Index on email for faster lookups
CREATE INDEX idx_users_email ON public.users(email);

-- ==================== PROJECTS TABLE ====================
CREATE TABLE public.projects (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  name text NOT NULL,
  description text,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Indexes for querying user projects
CREATE INDEX idx_projects_user_id ON public.projects(user_id);

-- ==================== DATASETS TABLE ====================
CREATE TABLE public.datasets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  filename text NOT NULL,
  file_path text NOT NULL,
  size_bytes integer NOT NULL,
  metadata jsonb,
  health_score float8,
  upload_date timestamp with time zone DEFAULT now(),
  last_analysis timestamp with time zone,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Indexes
CREATE INDEX idx_datasets_project_id ON public.datasets(project_id);
CREATE INDEX idx_datasets_health_score ON public.datasets(health_score);

-- ==================== ANALYSIS_RESULTS TABLE ====================
CREATE TABLE public.analysis_results (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  dataset_id uuid NOT NULL REFERENCES public.datasets(id) ON DELETE CASCADE,
  health_score float8 NOT NULL,
  profiling_data jsonb NOT NULL,
  recommendations jsonb NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Indexes
CREATE INDEX idx_analysis_dataset_id ON public.analysis_results(dataset_id);
CREATE INDEX idx_analysis_created_at ON public.analysis_results(created_at DESC);

-- ==================== TEAM_MEMBERS TABLE ====================
CREATE TABLE public.team_members (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  role text NOT NULL DEFAULT 'editor' CHECK (role IN ('owner', 'editor', 'viewer')),
  created_at timestamp with time zone DEFAULT now(),
  UNIQUE(project_id, user_id)
);

-- Indexes
CREATE INDEX idx_team_members_project_id ON public.team_members(project_id);
CREATE INDEX idx_team_members_user_id ON public.team_members(user_id);

-- ==================== API_KEYS TABLE ====================
CREATE TABLE public.api_keys (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  name text NOT NULL,
  key_hash text NOT NULL UNIQUE,
  last_used timestamp with time zone,
  created_at timestamp with time zone DEFAULT now(),
  UNIQUE(user_id, name)
);

-- Indexes
CREATE INDEX idx_api_keys_user_id ON public.api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON public.api_keys(key_hash);

-- ==================== ROW LEVEL SECURITY ====================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

-- Users can only see their own profile
CREATE POLICY "Users can view own profile" ON public.users
  FOR SELECT USING (auth.uid()::text = id::text);

-- Users can only manage their own projects
CREATE POLICY "Users can manage own projects" ON public.projects
  FOR ALL USING (user_id = auth.uid());

-- Users can only see datasets in their projects
CREATE POLICY "Users can view own datasets" ON public.datasets
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.projects p
      WHERE p.id = datasets.project_id AND p.user_id = auth.uid()
    )
  );

-- Users can only see analysis for their datasets
CREATE POLICY "Users can view own analysis" ON public.analysis_results
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.datasets d
      JOIN public.projects p ON p.id = d.project_id
      WHERE d.id = analysis_results.dataset_id AND p.user_id = auth.uid()
    )
  );

-- Users can only see team members for their projects
CREATE POLICY "Users can view team members" ON public.team_members
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.projects p
      WHERE p.id = team_members.project_id AND p.user_id = auth.uid()
    )
  );

-- Users can only manage their own API keys
CREATE POLICY "Users can manage own API keys" ON public.api_keys
  FOR ALL USING (user_id = auth.uid());
