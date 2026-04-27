# Stella Tower Assistant

较之前版本有较大改动，目前还没有改动逻辑，仅调整文件结构增加Vue前端，依旧可以纯CLI启动

## Structure

- `apps/api`: automation engine, FastAPI server, websocket events.
- `apps/web`: Vue 3 dashboard built with Vite.
- `docs`: architecture notes and API contract.

## Backend

Run from `apps/api`:

```bash
python -m stellatowerassistant.cli run
python -m stellatowerassistant.cli serve
python -m stellatowerassistant.ocr_capture
```

## Frontend

Run from `apps/web`:

```bash
npm install
npm run dev
```

The web app expects the backend API at `http://127.0.0.1:8765`.

## One-command dev start

From the repository root in PowerShell:

```powershell
.\scripts\start-dev.ps1
```

For the standalone OCR capture tool:

```powershell
.\scripts\start-ocr-capture.ps1
```

If frontend dependencies are not installed yet:

```powershell
.\scripts\start-dev.ps1 -InstallDependencies
```
