# PostgreSQL Database Setup Guide

This guide helps you set up PostgreSQL for the RM Platform development environment.

## 🚨 Quick Fix for "role does not exist" Error

If you're getting the error:
```
createdb: error: connection to server on socket "/run/postgresql/.s.PGSQL.5432" failed: FATAL: role "zero" does not exist
```

This means PostgreSQL is trying to connect with your system username, but that user doesn't exist in PostgreSQL.

### Solution 1: Create PostgreSQL User (Recommended)

1. **Switch to postgres user and create your user:**
```bash
sudo -u postgres createuser --interactive
```

2. **When prompted:**
   - Enter role name: `zero` (or your system username)
   - Shall the new role be a superuser? `y`

3. **Create the database:**
```bash
createdb rm_platform_dev
```

### Solution 2: Use postgres User Directly

1. **Create database as postgres user:**
```bash
sudo -u postgres createdb rm_platform_dev
```

2. **Update your .env file:**
```env
DB_USER=postgres
DB_PASSWORD=
```

### Solution 3: Set Password Authentication

1. **Connect as postgres user:**
```bash
sudo -u postgres psql
```

2. **Create user with password:**
```sql
CREATE USER zero WITH PASSWORD 'your_password';
ALTER USER zero CREATEDB;
ALTER USER zero WITH SUPERUSER;
\q
```

3. **Update your .env file:**
```env
DB_USER=zero
DB_PASSWORD=your_password
```

## 📋 Complete PostgreSQL Setup

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS (with Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**CentOS/RHEL:**
```bash
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Verify Installation

```bash
sudo systemctl status postgresql
psql --version
```

### 3. Configure PostgreSQL

#### Option A: Development Setup (Simple)

1. **Switch to postgres user:**
```bash
sudo -i -u postgres
```

2. **Create development user:**
```bash
createuser --interactive --pwprompt rmplatform
```
   - Enter password: `rmplatform123`
   - Shall the new role be a superuser? `y`

3. **Create development database:**
```bash
createdb -O rmplatform rm_platform_dev
exit
```

4. **Update .env file:**
```env
DB_NAME=rm_platform_dev
DB_USER=rmplatform
DB_PASSWORD=rmplatform123
DB_HOST=localhost
DB_PORT=5432
```

#### Option B: Production-like Setup

1. **Edit PostgreSQL configuration:**
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

2. **Uncomment and modify:**
```
listen_addresses = 'localhost'
port = 5432
max_connections = 100
```

3. **Edit authentication:**
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

4. **Add/modify lines:**
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

5. **Restart PostgreSQL:**
```bash
sudo systemctl restart postgresql
```

## 🛠️ Database Setup Script

Create a simple setup script:

```bash
#!/bin/bash
# save as setup_db.sh

echo "Setting up PostgreSQL for RM Platform..."

# Check if PostgreSQL is running
if ! systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL..."
    sudo systemctl start postgresql
fi

# Create user and database
sudo -u postgres psql <<EOF
-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'rmplatform') THEN
        CREATE USER rmplatform WITH PASSWORD 'rmplatform123';
        ALTER USER rmplatform CREATEDB;
        ALTER USER rmplatform WITH SUPERUSER;
    END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE rm_platform_dev OWNER rmplatform'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'rm_platform_dev')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE rm_platform_dev TO rmplatform;
EOF

echo "✅ Database setup complete!"
echo "Database: rm_platform_dev"
echo "User: rmplatform"
echo "Password: rmplatform123"
echo ""
echo "Update your .env file with these credentials."
```

Make it executable and run:
```bash
chmod +x setup_db.sh
./setup_db.sh
```

## 🔧 Testing Database Connection

### 1. Test with psql
```bash
psql -h localhost -U rmplatform -d rm_platform_dev
```

### 2. Test with Django
```bash
# Activate virtual environment first
source venv/bin/activate

# Test database connection
python manage.py dbshell
```

### 3. Run Django migrations
```bash
python manage.py migrate
```

## 🚨 Troubleshooting

### Common Issues

**1. PostgreSQL not running:**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**2. Permission denied:**
```bash
sudo -u postgres psql
ALTER USER your_username WITH SUPERUSER;
```

**3. Connection refused:**
- Check if PostgreSQL is listening on port 5432:
```bash
sudo netstat -plunt | grep 5432
```

**4. Password authentication failed:**
- Reset user password:
```bash
sudo -u postgres psql
ALTER USER rmplatform PASSWORD 'new_password';
```

**5. Database doesn't exist:**
```bash
sudo -u postgres createdb rm_platform_dev
# or
psql -U rmplatform -c "CREATE DATABASE rm_platform_dev;"
```

### Reset Everything (Nuclear Option)

If you want to start fresh:

```bash
# Stop Django development server
# Drop database
sudo -u postgres dropdb rm_platform_dev

# Drop user
sudo -u postgres psql -c "DROP USER IF EXISTS rmplatform;"

# Recreate everything
sudo -u postgres psql <<EOF
CREATE USER rmplatform WITH PASSWORD 'rmplatform123';
ALTER USER rmplatform CREATEDB;
ALTER USER rmplatform WITH SUPERUSER;
CREATE DATABASE rm_platform_dev OWNER rmplatform;
GRANT ALL PRIVILEGES ON DATABASE rm_platform_dev TO rmplatform;
EOF

# Run migrations
python manage.py migrate
```

## 📋 Environment Configuration

Update your `.env` file with the correct database settings:

```env
# Database Configuration
DB_NAME=rm_platform_dev
DB_USER=rmplatform
DB_PASSWORD=rmplatform123
DB_HOST=localhost
DB_PORT=5432
```

## 🔒 Security Notes

### Development
- The setup above is for development only
- Uses simple passwords for convenience
- Allows local connections without encryption

### Production
- Use strong, unique passwords
- Enable SSL/TLS encryption
- Restrict connection permissions
- Use environment variables for credentials
- Consider using connection pooling (PgBouncer)
- Regular security updates

### Production Example:
```env
DB_NAME=rm_platform_prod
DB_USER=rm_prod_user
DB_PASSWORD=very-secure-random-password-here
DB_HOST=your-db-server.com
DB_PORT=5432
```

## 📚 Additional Resources

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [Django Database Configuration](https://docs.djangoproject.com/en/5.0/ref/settings/#databases)
- [psycopg3 Documentation](https://www.psycopg.org/psycopg3/docs/)

## ✅ Quick Verification Checklist

- [ ] PostgreSQL service is running
- [ ] Database user exists with proper permissions
- [ ] Database `rm_platform_dev` exists
- [ ] Can connect with: `psql -h localhost -U rmplatform -d rm_platform_dev`
- [ ] Django can connect: `python manage.py dbshell`
- [ ] Migrations run successfully: `python manage.py migrate`

Once all items are checked, your database is ready for RM Platform development!