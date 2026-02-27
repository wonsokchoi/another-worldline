"""
Run Alembic migrations programmatically.
Usage: poetry run python run_migrations.py
"""
import subprocess
import sys
import os

def run_migrations():
    """Run alembic upgrade head."""
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)

    # Set DATABASE_URL from .env if not already set
    env_file = os.path.join(backend_dir, '.env')
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()

    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', '(not set)')}")
    print("Running: alembic upgrade head")

    result = subprocess.run(
        [sys.executable, '-m', 'alembic', 'upgrade', 'head'],
        capture_output=False,
        cwd=backend_dir,
    )

    if result.returncode == 0:
        print("Migration completed successfully.")
    else:
        print(f"Migration failed with return code {result.returncode}")
        sys.exit(result.returncode)


if __name__ == '__main__':
    run_migrations()
