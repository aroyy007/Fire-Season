-- POST-MVP REFERENCE ONLY. The Competition MVP uses immutable artifact schemas
-- in backend/schemas and has no runtime database.
-- Fire Season: proposed PostgreSQL 15+ / PostGIS schema.
-- Not yet applied to a running database. Apply with a migration owner;
-- use a separate non-owner, non-BYPASSRLS API role in deployment.
BEGIN;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE SCHEMA IF NOT EXISTS fireseason;
SET search_path = fireseason, public;

CREATE TABLE app_user (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  identity_subject text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE dataset (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  short_name text NOT NULL,
  version text NOT NULL,
  platform text NOT NULL,
  stream text NOT NULL CHECK (stream IN ('science_mask','recent_detection','reference')),
  source_url text NOT NULL,
  nominal_resolution_m integer CHECK (nominal_resolution_m > 0),
  processing_level text NOT NULL,
  license_note text NOT NULL,
  access_status text NOT NULL CHECK (access_status IN ('documented','discovered','downloaded','decoded')),
  quality_notice text,
  checked_at timestamptz NOT NULL,
  UNIQUE(short_name, version, platform)
);

CREATE TABLE granule (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  dataset_id bigint NOT NULL REFERENCES dataset(id),
  provider_id text NOT NULL,
  source_url text NOT NULL,
  observed_start timestamptz NOT NULL,
  observed_end timestamptz NOT NULL,
  retrieved_at timestamptz,
  sha256 text CHECK (sha256 ~ '^[0-9a-f]{64}$'),
  object_key text,
  size_bytes bigint CHECK (size_bytes >= 0),
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  CHECK (observed_end >= observed_start),
  CHECK ((sha256 IS NULL) = (object_key IS NULL)),
  UNIQUE NULLS NOT DISTINCT(dataset_id, provider_id, sha256)
);
CREATE INDEX granule_dataset_time_idx ON granule(dataset_id, observed_start);

CREATE TABLE source_snapshot (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  manifest_sha256 text NOT NULL UNIQUE CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$'),
  manifest_object_key text NOT NULL,
  qa_policy_version text NOT NULL,
  grid_version text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE snapshot_granule (
  snapshot_id uuid NOT NULL REFERENCES source_snapshot(id),
  granule_id bigint NOT NULL REFERENCES granule(id),
  PRIMARY KEY(snapshot_id, granule_id)
);
CREATE INDEX snapshot_granule_reverse_idx ON snapshot_granule(granule_id);

CREATE TABLE region (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid REFERENCES app_user(id),
  name text NOT NULL,
  revision integer NOT NULL DEFAULT 1 CHECK (revision > 0),
  parent_revision_id uuid REFERENCES region(id),
  is_public boolean NOT NULL DEFAULT false,
  boundary geometry(MultiPolygon, 4326) NOT NULL,
  geometry_sha256 text NOT NULL CHECK (geometry_sha256 ~ '^[0-9a-f]{64}$'),
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (owner_id IS NOT NULL OR is_public),
  CHECK (ST_IsValid(boundary) AND NOT ST_IsEmpty(boundary)),
  CHECK (ST_NPoints(boundary) <= 10000),
  CHECK (ST_XMin(Box3D(boundary)) >= -180 AND ST_XMax(Box3D(boundary)) <= 180),
  CHECK (ST_YMin(Box3D(boundary)) >= -90 AND ST_YMax(Box3D(boundary)) <= 90)
);
CREATE INDEX region_geometry_idx ON region USING gist(boundary);
CREATE INDEX region_owner_idx ON region(owner_id);

CREATE TABLE calibration (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  version text NOT NULL,
  source_dataset_id bigint NOT NULL REFERENCES dataset(id),
  reference_dataset_id bigint NOT NULL REFERENCES dataset(id),
  training_snapshot_id uuid NOT NULL REFERENCES source_snapshot(id),
  status text NOT NULL CHECK (status IN ('experimental','released','withdrawn')),
  domain_manifest jsonb NOT NULL,
  model_sha256 text NOT NULL CHECK (model_sha256 ~ '^[0-9a-f]{64}$'),
  model_object_key text NOT NULL,
  code_revision text NOT NULL,
  qa_policy_version text NOT NULL,
  evaluation_object_key text NOT NULL,
  release_review jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (source_dataset_id <> reference_dataset_id),
  CHECK (status <> 'released' OR release_review IS NOT NULL),
  UNIQUE(name, version)
);

CREATE TABLE analysis (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid REFERENCES app_user(id),
  region_id uuid NOT NULL REFERENCES region(id),
  snapshot_id uuid NOT NULL REFERENCES source_snapshot(id),
  calibration_id uuid REFERENCES calibration(id),
  is_public boolean NOT NULL DEFAULT false,
  input_sha256 text NOT NULL CHECK (input_sha256 ~ '^[0-9a-f]{64}$'),
  config jsonb NOT NULL,
  start_date date NOT NULL,
  end_date date NOT NULL,
  status text NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','running','succeeded','failed','cancelled')),
  comparison_status text CHECK (comparison_status IN ('available','experimental','insufficient_support','unsupported')),
  error_code text,
  error_message text,
  created_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz,
  CHECK (end_date >= start_date),
  CHECK (owner_id IS NOT NULL OR is_public),
  CHECK (status NOT IN ('succeeded','failed','cancelled') OR completed_at IS NOT NULL),
  CHECK (comparison_status <> 'available' OR calibration_id IS NOT NULL)
);
CREATE INDEX analysis_owner_time_idx ON analysis(owner_id, created_at DESC, id);
CREATE INDEX analysis_input_idx ON analysis(input_sha256);
CREATE INDEX analysis_region_idx ON analysis(region_id);
CREATE INDEX analysis_snapshot_idx ON analysis(snapshot_id);

CREATE TABLE analysis_job (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  analysis_id uuid NOT NULL REFERENCES analysis(id),
  attempt integer NOT NULL CHECK (attempt > 0),
  status text NOT NULL CHECK (status IN ('queued','leased','succeeded','failed','cancelled')),
  worker_id text,
  lease_until timestamptz,
  heartbeat_at timestamptz,
  error_code text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(analysis_id, attempt)
);
CREATE INDEX job_queued_idx ON analysis_job(created_at) WHERE status = 'queued';
CREATE UNIQUE INDEX job_one_active_idx ON analysis_job(analysis_id) WHERE status IN ('queued','leased');

-- Whole-region monthly summaries; block-month analytical rows live in Parquet.
CREATE TABLE calendar_bin (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  analysis_id uuid NOT NULL REFERENCES analysis(id),
  dataset_id bigint NOT NULL REFERENCES dataset(id),
  month date NOT NULL CHECK (extract(day FROM month) = 1),
  value_kind text NOT NULL CHECK (value_kind IN ('observed','modeled','unavailable')),
  metric text NOT NULL CHECK (metric = 'active_cell_days_per_1000_valid_cell_days'),
  fire_cell_days bigint CHECK (fire_cell_days >= 0),
  valid_cell_days bigint CHECK (valid_cell_days >= 0),
  eligible_land_cell_days bigint CHECK (eligible_land_cell_days > 0),
  estimate double precision CHECK (estimate BETWEEN 0 AND 1000),
  lower_bound double precision CHECK (lower_bound BETWEEN 0 AND 1000),
  upper_bound double precision CHECK (upper_bound BETWEEN 0 AND 1000),
  interval_method text,
  calibration_id uuid REFERENCES calibration(id),
  unavailable_reason text,
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  CHECK (fire_cell_days <= valid_cell_days),
  CHECK (valid_cell_days <= eligible_land_cell_days),
  CHECK (lower_bound <= estimate AND estimate <= upper_bound),
  CHECK ((lower_bound IS NULL AND upper_bound IS NULL AND interval_method IS NULL)
      OR (lower_bound IS NOT NULL AND upper_bound IS NOT NULL AND interval_method IS NOT NULL)),
  CHECK ((value_kind = 'unavailable' AND estimate IS NULL AND unavailable_reason IS NOT NULL AND lower_bound IS NULL)
      OR (value_kind <> 'unavailable' AND estimate IS NOT NULL AND unavailable_reason IS NULL)),
  CHECK (value_kind <> 'modeled' OR calibration_id IS NOT NULL),
  CHECK (value_kind <> 'observed' OR (valid_cell_days IS NOT NULL AND valid_cell_days > 0 AND fire_cell_days IS NOT NULL AND calibration_id IS NULL)),
  UNIQUE(analysis_id, dataset_id, month, value_kind)
);

CREATE TABLE artifact (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id uuid NOT NULL REFERENCES analysis(id),
  kind text NOT NULL CHECK (kind IN ('receipt','calendar_csv','calendar_parquet','reference_labels','evaluation','brief_pdf')),
  object_key text NOT NULL,
  sha256 text NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
  media_type text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(analysis_id, kind, sha256)
);
CREATE INDEX artifact_analysis_idx ON artifact(analysis_id);

CREATE TABLE brief (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id uuid NOT NULL REFERENCES analysis(id),
  owner_id uuid REFERENCES app_user(id),
  status text NOT NULL CHECK (status IN ('queued','running','succeeded','failed')),
  generator text NOT NULL CHECK (generator IN ('template','llm')),
  model_identifier text,
  prompt_version text,
  body_markdown text,
  claims jsonb NOT NULL DEFAULT '[]'::jsonb,
  validation_result jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (generator <> 'llm' OR (model_identifier IS NOT NULL AND prompt_version IS NOT NULL)),
  CHECK (status <> 'succeeded' OR (body_markdown IS NOT NULL AND validation_result IS NOT NULL))
);
CREATE INDEX brief_analysis_idx ON brief(analysis_id);

CREATE TABLE idempotency_request (
  owner_id uuid NOT NULL REFERENCES app_user(id),
  key text NOT NULL,
  request_sha256 text NOT NULL CHECK (request_sha256 ~ '^[0-9a-f]{64}$'),
  analysis_id uuid NOT NULL REFERENCES analysis(id),
  expires_at timestamptz NOT NULL,
  PRIMARY KEY(owner_id, key)
);

-- Backend sets this transaction-locally after verifying identity.
-- Never let a browser/database client set its own identity context.
CREATE FUNCTION current_actor() RETURNS uuid LANGUAGE sql STABLE AS $$
  SELECT NULLIF(current_setting('app.user_id', true), '')::uuid
$$;

ALTER TABLE region ENABLE ROW LEVEL SECURITY;
ALTER TABLE region FORCE ROW LEVEL SECURITY;
CREATE POLICY region_read ON region FOR SELECT USING (is_public OR owner_id = current_actor());
CREATE POLICY region_insert ON region FOR INSERT WITH CHECK (owner_id = current_actor() AND NOT is_public);

ALTER TABLE analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis FORCE ROW LEVEL SECURITY;
CREATE POLICY analysis_read ON analysis FOR SELECT USING (is_public OR owner_id = current_actor());
CREATE POLICY analysis_insert ON analysis FOR INSERT WITH CHECK (
  owner_id = current_actor() AND NOT is_public
  AND EXISTS (SELECT 1 FROM region r WHERE r.id = region_id AND (r.is_public OR r.owner_id = current_actor()))
);

ALTER TABLE calendar_bin ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_bin FORCE ROW LEVEL SECURITY;
CREATE POLICY bin_read ON calendar_bin FOR SELECT USING (
  EXISTS (SELECT 1 FROM analysis a WHERE a.id = analysis_id AND (a.is_public OR a.owner_id = current_actor()))
);
ALTER TABLE artifact ENABLE ROW LEVEL SECURITY;
ALTER TABLE artifact FORCE ROW LEVEL SECURITY;
CREATE POLICY artifact_read ON artifact FOR SELECT USING (
  EXISTS (SELECT 1 FROM analysis a WHERE a.id = analysis_id AND (a.is_public OR a.owner_id = current_actor()))
);
ALTER TABLE brief ENABLE ROW LEVEL SECURITY;
ALTER TABLE brief FORCE ROW LEVEL SECURITY;
CREATE POLICY brief_read ON brief FOR SELECT USING (
  (owner_id = current_actor() OR owner_id IS NULL)
  AND EXISTS (SELECT 1 FROM analysis a WHERE a.id = analysis_id AND (a.is_public OR a.owner_id = current_actor()))
);
-- No runtime update/delete policies: used region revisions and analyses are immutable
-- to API callers. A trusted worker role is provisioned separately for lifecycle writes.
-- Do not grant API users access to app_user, analysis_job or idempotency_request.
COMMIT;
