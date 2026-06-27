## Backend Setup
I'm using WSL on my local machine btw

```bash
cd backend

# If you don't have uv (macOS/Linux/WSL)
curl -Ls https://astral.sh/uv/install.sh | sh  
# powershell install (Windows):
# irm https://astral.sh/uv/install.ps1 | iex

# create virtual environment
uv venv

# activate it
source .venv/bin/activate   # mac/linux/wsl
# .venv\Scripts\activate    # windows (if needed)

# install dependencies from lockfile
uv sync

# Start server
fastapi dev