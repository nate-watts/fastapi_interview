# UV Install

<https://docs.astral.sh/uv/getting-started/installation/>

## Run Application

```sh
uv sync
chmod +x run.sh
./run.sh
# alternative:
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
