# Beta deployment on GCP

One Compute Engine virtual machine runs the whole catalog with Docker Compose:
- Infrahub 1.11.8, from the unchanged `docker-compose.yml` in the repository root;
- the catalog service (`frontend/api/Dockerfile`);
- Caddy, which serves the built web app (`frontend/web/Dockerfile`), forwards `/api` to the
  catalog service and gets HTTPS certificates from Let's Encrypt.

Only Caddy is reachable from the internet (`deploy/docker-compose.gcp.yml`):

| Address | Who can open it |
|---------|-----------------|
| `https://<ip-with-dashes>.sslip.io` | The beta group, with one shared user name and password |
| `https://infrahub.<ip-with-dashes>.sslip.io` | Maintainers, with Infrahub's login. Anonymous access is turned off. |

## Before a public launch

The shared password limits submissions to the beta group. These items from `frontend/README.md`
are still open and must be fixed before the password is removed:
1. Spam protection on `POST /api/submissions` (spec 005, FR-019).
2. The service account can merge its own proposed changes (spec 005, FR-020).

`deploy/setup-vm.sh` replaces Infrahub's published default passwords, tokens and secret key.

## Values used below

| Value | Default |
|-------|---------|
| Project | `naf-product-catalog` |
| Region and zone | `us-central1`, `us-central1-a` |
| Machine | `e2-highmem-2` (2 vCPU, 16 GB) as a Spot VM. The local stack uses about 7 GB. |
| Disk | 50 GB, Debian 12 |

## 1. Create the machine (on your computer)

Install the Google Cloud CLI and sign in once:

```bash
brew install --cask google-cloud-sdk
gcloud auth login
gcloud config set project naf-product-catalog
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
```

Create the static address, the firewall rule for HTTP and HTTPS, and the machine:

```bash
gcloud services enable compute.googleapis.com
gcloud compute addresses create catalog-beta-ip --region us-central1
gcloud compute firewall-rules create catalog-beta-web \
  --allow tcp:80,tcp:443,udp:443 --target-tags catalog-beta-web
gcloud compute instances create catalog-beta \
  --machine-type e2-highmem-2 \
  --provisioning-model SPOT --instance-termination-action STOP \
  --image-family debian-12 --image-project debian-cloud \
  --boot-disk-size 50GB --boot-disk-type pd-balanced \
  --address catalog-beta-ip --tags catalog-beta-web
```

SSH uses the `default-allow-ssh` rule of the default network.

A Spot VM costs less, but Google can stop it at any time. The disk, the data and the static
address are kept, and every container starts again on its own when the machine starts. Google does
not start the machine again by itself. To start it:

```bash
gcloud compute instances start catalog-beta
```

To check whether it is running: `gcloud compute instances describe catalog-beta --format='value(status)'`.

## 2. Start the stack (on the machine)

```bash
gcloud compute ssh catalog-beta
sudo apt-get update && sudo apt-get install -y git
sudo git clone https://github.com/qduk/infrahub-product-catalog.git /opt/catalog
cd /opt/catalog
sudo deploy/setup-vm.sh <your email, for certificate notices>
```

The script installs Docker, writes `deploy/.env` with new Infrahub passwords and tokens, creates
the beta password in `deploy/secrets/`, and starts everything. Both files are readable only by
root, and Git ignores them. The first start takes several minutes.

Read the values you need next:

```bash
sudo grep -E 'SITE_HOST|INFRAHUB_INITIAL_ADMIN_(PASSWORD|TOKEN)' deploy/.env
sudo cat deploy/secrets/beta-login.txt
```

## 3. Load the schema (on your computer)

Point `infrahubctl` at the deployed Infrahub. `deploy/infrahubctl.beta.toml` is ignored by Git.

```bash
printf 'server_address = "https://infrahub.<SITE_HOST>"\n' > deploy/infrahubctl.beta.toml
export INFRAHUBCTL_CONFIG=deploy/infrahubctl.beta.toml
export INFRAHUB_API_TOKEN=<INFRAHUB_INITIAL_ADMIN_TOKEN from deploy/.env>
uv run infrahubctl info

uv run infrahubctl branch create load-schema
uv run infrahubctl schema load --branch load-schema schemas/
```

In Infrahub, open a proposed change from `load-schema` to `main` and merge it. No checks run yet,
because the repository is not connected.

## 4. Connect the repository and load the catalog (on your computer)

The repository's queries read the catalog schema, so the schema must be on `main` first.

```bash
uv run infrahubctl object load bootstrap/repository.yml
```

Wait until the repository shows as in sync in Infrahub (**Integrations > Repositories**). Then
load the catalog on a branch:

```bash
uv run infrahubctl branch create load-catalog
uv run infrahubctl object load --branch load-catalog objects/
```

Open a proposed change from `load-catalog` to `main`. Wait for the checks: all must pass, and
`catalog_coverage_check` lists the products with no coverage claim as warnings. Then merge it.

## 5. Connect the catalog service (on your computer, then on the machine)

Create the service account on the deployed Infrahub:

```bash
cd frontend/api
INFRAHUB_ADDRESS=https://infrahub.<SITE_HOST> INFRAHUB_ADMIN_TOKEN=<admin token> \
  uv run python bootstrap_service_account.py
```

On the machine, put the printed token in `CATALOG_API_TOKEN` in `/opt/catalog/deploy/.env`, then
restart the service:

```bash
cd /opt/catalog
sudo nano deploy/.env
sudo docker compose -f docker-compose.yml -f deploy/docker-compose.gcp.yml --env-file deploy/.env up -d catalog-api
```

## 6. Give the beta group access

Send the group `https://<SITE_HOST>` and the user name and password from
`deploy/secrets/beta-login.txt`.

## Updating

```bash
gcloud compute ssh catalog-beta
cd /opt/catalog && sudo git pull && sudo deploy/setup-vm.sh <your email>
```

After a change to `checks/`, `queries/` or `.infrahub.yml`, also run **Import latest commit** on
the repository in the deployed Infrahub. Open proposed changes keep the checks of the commit their
branch was created from: rebase them to run the new checks.

## Changing the beta password

```bash
sudo rm /opt/catalog/deploy/secrets/basic_auth.caddy /opt/catalog/deploy/secrets/beta-login.txt
cd /opt/catalog && sudo deploy/setup-vm.sh <your email>
```

## If the HTTPS certificate is not issued

Caddy logs the reason: `sudo docker compose -f docker-compose.yml -f deploy/docker-compose.gcp.yml
--env-file deploy/.env logs web`. Ports 80 and 443 must be open (step 1), and Let's Encrypt limits
how many certificates it issues for one name each week.
