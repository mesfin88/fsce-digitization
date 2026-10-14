# FSCE Digitization — Django + MySQL + React

Starter implementation for physical archive inventory, manually assigned scanner batches, QC, private DSpace submissions, and Department Head publication approval.

## Decisions enforced
- `PhysicalFile.case` is a `OneToOneField`: one physical file per case number.
- Every `BatchItem` stores an explicitly selected scanner; no automatic allocation.
- DSpace submissions are locally represented as private/unpublished until the Department Head approves. The DSpace adapter is intentionally a stub: do not deploy publication actions until it is implemented for your installed DSpace version and verifies remote visibility.

## Run locally
Backend (Python 3.12+, MySQL 8+):
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
python manage.py makemigrations accounts archiveops workflow
python manage.py migrate
python manage.py seed_roles
python manage.py createsuperuser
python manage.py runserver
```
Use `cp .env.example .env` on Linux. Set database credentials before migrating. Set `DJANGO_TEST_SQLITE=1` for isolated local tests.

Frontend:
```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

## API overview
- `GET/POST /api/cases/`
- `GET/POST /api/physical-files/`
- `GET/POST /api/archive-locations/`
- `GET/POST /api/batches/`
- `POST /api/batches/{id}/add_item/` body: `{"physical_file": 1, "scanner": 2}`
- `POST /api/batches/{id}/dispatch/`
- `POST /api/batches/{id}/receive/` body: `{"exceptions": "..." }`
- `GET/POST /api/digital-assets/`
- `GET/POST /api/qc/`
- `POST /api/submissions/create-private/` body: `{"qc": 1}`
- `POST /api/submissions/{id}/approve-publication/`

## DSpace integration warning
`DspaceGateway` raises `NotImplementedError` until connected to your actual DSpace version. Implement it to:
1. Submit into a private workspace/workflow state.
2. Verify remote item is not publicly discoverable.
3. Return the item UUID and handle.
4. On Head approval, invoke the supported DSpace workflow action and verify it is public.
5. Use idempotency/reconciliation so network timeouts do not create duplicate items.

Do not set local status to published merely because a request was sent.

## Deployment
`deployment/compose.yml` runs MySQL, Django/Gunicorn, and Nginx-served React. Copy `deployment/.env.example` to `deployment/.env`, set unique strong secrets, and review hosts/TLS/proxy settings before deployment. The example publishes HTTP on port 8080; put it behind your approved HTTPS reverse proxy before real court data is used.

## Production checklist
- Configure court-approved AD/SSO; the starter uses Django session/basic authentication for development.
- Set `DEBUG=0`, a strong secret, exact allowed hosts, secure cookies and HTTPS.
- Restrict database and file-share permissions; encrypt backups; perform restore drills.
- Review retention, audit access, logging, monitoring, and disaster recovery with court ICT/security.
- Never commit `.env`, tokens, case PDFs, real metadata, or database dumps.
- Test on staging against the exact DSpace release before enabling submission/publication.
