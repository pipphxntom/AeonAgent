# Supabase Setup Guide for AeonAgent

## 🚀 Quick Start with Supabase

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up/Login with GitHub (recommended)
4. Click "New Project"
5. Choose your organization
6. Enter project details:
   - **Name**: `aeonagent` 
   - **Database Password**: Generate a strong password (save this!)
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Free tier (perfect for development)

### 2. Get Your Supabase Credentials

After project creation, go to Settings → API:

```bash
# Copy these values to your .env file:
SUPABASE_URL=https://[your-project-id].supabase.co
SUPABASE_ANON_KEY=[your-anon-key]
SUPABASE_SERVICE_KEY=[your-service-role-key]
```

Go to Settings → API → JWT Settings:
```bash
SUPABASE_JWT_SECRET=[your-jwt-secret]
```

### 3. Set Up Database Schema

#### Option A: Using Supabase SQL Editor (Recommended)

1. Go to SQL Editor in your Supabase dashboard
2. Create a new query and paste this schema:

```sql
-- Enable Row Level Security
ALTER DATABASE postgres SET row_security = on;

-- Create tenants table
CREATE TABLE public.tenants (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE,
    org_name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    plan VARCHAR(50) DEFAULT 'trial',
    status VARCHAR(20) DEFAULT 'active',
    settings JSONB DEFAULT '{}',
    stripe_customer_id VARCHAR(255) UNIQUE,
    billing_email VARCHAR(255),
    trial_start_date TIMESTAMPTZ DEFAULT NOW(),
    trial_end_date TIMESTAMPTZ,
    trial_queries_used INTEGER DEFAULT 0,
    trial_queries_limit INTEGER DEFAULT 100,
    trial_upload_mb_used INTEGER DEFAULT 0,
    trial_upload_mb_limit INTEGER DEFAULT 10,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create users table
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    auth_provider VARCHAR(50) DEFAULT 'supabase',
    auth_provider_id VARCHAR(255) UNIQUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role VARCHAR(50) DEFAULT 'user',
    permissions JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMPTZ,
    tenant_id INTEGER REFERENCES public.tenants(id) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create agent_types table
CREATE TABLE public.agent_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    config_template JSONB NOT NULL,
    default_model VARCHAR(100) DEFAULT 'gemini-pro',
    default_temperature DECIMAL DEFAULT 0.7,
    trial_enabled BOOLEAN DEFAULT TRUE,
    base_price_monthly DECIMAL DEFAULT 99.0,
    price_per_query DECIMAL DEFAULT 0.1,
    supports_file_upload BOOLEAN DEFAULT TRUE,
    supports_integrations BOOLEAN DEFAULT TRUE,
    max_context_length INTEGER DEFAULT 16000,
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create agent_instances table
CREATE TABLE public.agent_instances (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    tenant_id INTEGER REFERENCES public.tenants(id) NOT NULL,
    agent_type_id INTEGER REFERENCES public.agent_types(id) NOT NULL,
    config JSONB NOT NULL,
    model VARCHAR(100),
    temperature DECIMAL,
    system_prompt TEXT,
    status VARCHAR(20) DEFAULT 'provisioning',
    resource_quota JSONB DEFAULT '{}',
    queries_count INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    last_used TIMESTAMPTZ,
    provisioned_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create documents table
CREATE TABLE public.documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    content_type VARCHAR(100),
    file_size INTEGER,
    source VARCHAR(100) DEFAULT 'upload',
    source_url VARCHAR(500),
    source_metadata JSONB DEFAULT '{}',
    processing_status VARCHAR(20) DEFAULT 'pending',
    processing_error TEXT,
    extracted_text TEXT,
    chunk_count INTEGER DEFAULT 0,
    tenant_id INTEGER REFERENCES public.tenants(id) NOT NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create clause_chunks table
CREATE TABLE public.clause_chunks (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding_id VARCHAR(255) UNIQUE,
    embedding_model VARCHAR(100) DEFAULT 'text-embedding-ada-002',
    metadata JSONB DEFAULT '{}',
    document_id INTEGER REFERENCES public.documents(id) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create interactions table
CREATE TABLE public.interactions (
    id SERIAL PRIMARY KEY,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    model VARCHAR(100) NOT NULL,
    temperature DECIMAL,
    tokens_input INTEGER,
    tokens_output INTEGER,
    tokens_total INTEGER,
    response_time_ms INTEGER,
    retrieval_time_ms INTEGER,
    llm_time_ms INTEGER,
    context_chunks JSONB DEFAULT '[]',
    top_k INTEGER,
    rerank_score DECIMAL,
    status VARCHAR(20) DEFAULT 'completed',
    error_message TEXT,
    tenant_id INTEGER REFERENCES public.tenants(id) NOT NULL,
    user_id INTEGER REFERENCES public.users(id) NOT NULL,
    agent_instance_id INTEGER REFERENCES public.agent_instances(id) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create feedback table
CREATE TABLE public.feedback (
    id SERIAL PRIMARY KEY,
    rating INTEGER NOT NULL,
    feedback_type VARCHAR(20) DEFAULT 'rating',
    edit_text TEXT,
    comment TEXT,
    category VARCHAR(50),
    tags JSONB DEFAULT '[]',
    interaction_id INTEGER REFERENCES public.interactions(id) NOT NULL,
    user_id INTEGER REFERENCES public.users(id) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create subscriptions table
CREATE TABLE public.subscriptions (
    id SERIAL PRIMARY KEY,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_price_id VARCHAR(255),
    stripe_product_id VARCHAR(255),
    plan_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    amount DECIMAL NOT NULL,
    currency VARCHAR(3) DEFAULT 'usd',
    interval VARCHAR(20) DEFAULT 'month',
    query_limit INTEGER,
    user_limit INTEGER,
    storage_limit_gb INTEGER,
    agent_limit INTEGER,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    trial_start TIMESTAMPTZ,
    trial_end TIMESTAMPTZ,
    canceled_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    tenant_id INTEGER REFERENCES public.tenants(id) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create billing_records table
CREATE TABLE public.billing_records (
    id SERIAL PRIMARY KEY,
    stripe_invoice_id VARCHAR(255) UNIQUE,
    stripe_charge_id VARCHAR(255),
    stripe_payment_intent_id VARCHAR(255),
    amount DECIMAL NOT NULL,
    currency VARCHAR(3) DEFAULT 'usd',
    status VARCHAR(20) NOT NULL,
    description TEXT,
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    queries_billed INTEGER DEFAULT 0,
    overage_amount DECIMAL DEFAULT 0.0,
    tenant_id INTEGER REFERENCES public.tenants(id) NOT NULL,
    subscription_id INTEGER REFERENCES public.subscriptions(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert sample agent types
INSERT INTO public.agent_types (name, display_name, description, category, config_template) VALUES
('hr_assistant', 'HR Assistant', 'AI assistant for HR-related tasks and employee support', 'hr', '{"system_prompt": "You are an HR assistant AI."}'),
('sales_ops', 'Sales Operations', 'AI assistant for sales processes and pipeline management', 'sales', '{"system_prompt": "You are a Sales Operations AI assistant."}'),
('legal', 'Legal Assistant', 'AI assistant for legal document review and guidance', 'legal', '{"system_prompt": "You are a Legal AI assistant."}');

-- Enable Row Level Security policies
ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_instances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.interactions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for multi-tenant isolation
CREATE POLICY "Users can only see their own tenant data" ON public.tenants
    FOR ALL USING (id = (SELECT tenant_id FROM public.users WHERE users.auth_provider_id = auth.uid()::text));

CREATE POLICY "Users can only see their own user data" ON public.users
    FOR ALL USING (tenant_id = (SELECT tenant_id FROM public.users WHERE users.auth_provider_id = auth.uid()::text));

-- Add indexes for performance
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_tenant_id ON public.users(tenant_id);
CREATE INDEX idx_agent_instances_tenant_id ON public.agent_instances(tenant_id);
CREATE INDEX idx_documents_tenant_id ON public.documents(tenant_id);
CREATE INDEX idx_interactions_tenant_id ON public.interactions(tenant_id);
CREATE INDEX idx_interactions_user_id ON public.interactions(user_id);
```

3. Run the query to create all tables

#### Option B: Using Migration Files

If you prefer to use Alembic migrations, keep your existing migration setup and run:

```bash
cd backend
alembic upgrade head
```

### 4. Set Up Authentication

#### Enable Authentication Providers

1. Go to Authentication → Settings in Supabase dashboard
2. Enable the providers you want:
   - **Email**: Always enabled (for basic signup/login)
   - **Google**: For OAuth login
   - **GitHub**: For developer-friendly login
   - **Microsoft**: For enterprise users

#### Configure Email Templates (Optional)

1. Go to Authentication → Email Templates
2. Customize signup confirmation, password reset emails
3. Add your branding and messaging

### 5. Configure Row Level Security (RLS)

RLS is crucial for multi-tenant security:

1. Go to Authentication → Policies
2. Verify the policies we created above
3. Test with different users to ensure isolation

### 6. Update Your Environment Variables

Create `.env` file in your backend folder:

```bash
# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here
SUPABASE_JWT_SECRET=your_jwt_secret_here

# Redis & Qdrant (local development)
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333

# AI Models
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key

# Other settings...
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## 🎯 Free Tier Limits & Pricing

### Supabase Free Tier:
- **Database**: 500MB PostgreSQL
- **Authentication**: Unlimited users
- **Storage**: 1GB file storage
- **Bandwidth**: 2GB/month
- **Edge Functions**: 500K invocations/month
- **Realtime**: Unlimited connections

### When to Upgrade:
- **Pro Plan ($25/month)**: 8GB database, 100GB bandwidth
- **Team Plan ($599/month)**: More resources, collaboration features

## 🔐 Authentication Comparison

### Supabase Auth (Recommended) ✅
- **Cost**: Free (included with Supabase)
- **Features**: Email, OAuth, phone auth, MFA
- **Integration**: Native with Supabase database
- **Pros**: Simple, integrated, good docs
- **Cons**: Newer ecosystem

### Auth0 Alternative
- **Cost**: Free up to 7,000 MAUs
- **Features**: Advanced security, enterprise SSO
- **Integration**: Requires separate setup
- **Pros**: Mature, enterprise-ready
- **Cons**: More complex, separate billing

### Firebase Auth Alternative
- **Cost**: Free (pay for usage)
- **Features**: Google ecosystem integration
- **Integration**: Good with Google services
- **Pros**: Reliable, well-documented
- **Cons**: Google lock-in

## 🚀 Development Workflow

1. **Start local services**:
   ```bash
   docker-compose up -d redis qdrant
   ```

2. **Install dependencies**:
   ```bash
   cd backend && pip install -r requirements.txt
   cd ../frontend && npm install
   ```

3. **Start backend**:
   ```bash
   cd backend && uvicorn main:app --reload
   ```

4. **Start frontend**:
   ```bash
   cd frontend && npm run dev
   ```

5. **Test authentication**:
   - Visit http://localhost:3000
   - Try signup/login flows
   - Check Supabase dashboard for user creation

## 🔧 Troubleshooting

### Common Issues:

1. **Connection Error**: Check SUPABASE_URL format
2. **Auth Failed**: Verify SUPABASE_ANON_KEY
3. **Permission Denied**: Check RLS policies
4. **Schema Error**: Ensure all tables created

### Debug Commands:

```bash
# Test Supabase connection
python -c "from services.supabase_auth import supabase_auth; print('✅ Supabase connected')"

# Check environment variables
python -c "from core.config import settings; print(f'Supabase URL: {settings.SUPABASE_URL}')"
```

## 📚 Next Steps

1. **Frontend Integration**: Update React components to use Supabase
2. **Real-time Features**: Add live notifications with Supabase realtime
3. **File Storage**: Use Supabase Storage for document uploads
4. **Analytics**: Set up usage tracking
5. **Monitoring**: Add Supabase monitoring to dashboards

You're now ready to develop with Supabase! 🎉
