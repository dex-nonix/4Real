
Got it. Here’s a precise, paste-ready section for the STT plugin README that matches your model: connection-scoped configuration by name, DB-backed, no user accounts, all presets attached to the configuration.

### Configuration Model (Connection-Scoped, DB-Backed)

- **No user accounts**: The system resolves configuration by a single key: `configuration_name`.
- **Connection-scoped**: The client connects and supplies `configuration_name`. That selects the entire STT pipeline.
- **DB source of truth**: All parts of the pipeline are normalized in the database and attached to the chosen configuration.
- **Single → Multi capable**: Designed for a single-user deployment; supports many named configurations for advanced/multi-tenant scenarios without introducing users.

#### Terms
- `configuration_name`: Unique key the client provides per connection/job.
- `STT Configuration`: A composition that references all presets required for a full pipeline.

#### Minimal Schema (normalized, configuration-centric)
- `stt_configuration` (unique: `name`)
  - `engine_preset_id` → `stt_engine_preset`
  - `preprocess_preset_id` → `stt_preprocess_preset`
  - `streaming_preset_id` → `stt_streaming_preset`
  - `feature_preset_id` → `stt_feature_preset`
  - `postprocess_preset_id` → `stt_postprocess_preset`
  - `enabled`, `version`, `updated_at`
- `stt_engine_preset` (type, model, device, compute_json, enabled)
- `stt_preprocess_preset` (resample_hz, vad_json, denoise_json, normalize_json, enabled)
- `stt_streaming_preset` (format, frame_ms, partial_results, endpointing_json, max_session_minutes, enabled)
- `stt_feature_preset` (language_detection, diarization_json, timestamps, punctuation, enabled)
- `stt_postprocess_preset` (remove_fillers, capitalize_sentences, custom_rules_json, enabled)
- `stt_session` (id, connection_id, configuration_name, pipeline_snapshot_json, state, started_at, ended_at, stats_json)
- `stt_job` (id, source_type, configuration_name, pipeline_snapshot_json, status, result_json, created_at, finished_at)

Notes:
- JSON fields hold small knobs only; structure and reuse come from normalized presets.
- `stt_configuration.name` is the only key the client needs.

#### Resolution Flow (effective config)
1) Load `stt_configuration` by `configuration_name`.
2) Join linked presets to build the pipeline.
3) Produce `effective_config` (snapshot) and store in `stt_session.pipeline_snapshot_json` (or job snapshot).
4) Use this snapshot for all processing; do not re-resolve mid-session.

#### Client Contract
- Connection or request MUST include `configuration_name`.
- Optional request-level overrides MAY be supported (small deltas), but the default path is “configuration-only”.

Example (stream init):
```json
{
  "configuration_name": "default-speech"
}
```

#### Processing Flow (per connection)
- Receive frames (PCM16/Opus).
- Apply `preprocess_preset` (resample → VAD gate → denoise → normalize).
- Feed into engine from `engine_preset`.
- Streaming behavior from `streaming_preset` (partials, endpointing).
- Enhance output via `feature_preset` (timestamps, optional diarization, language detection).
- Clean text via `postprocess_preset`.
- Persist metrics and session stats.

#### Change Management / Versions
- Config edits update `stt_configuration.version`.
- Sessions/jobs always use their stored `pipeline_snapshot_json` for auditability.
- Future connections using the same `configuration_name` pick up new version automatically.

#### Admin/CRUD
- Manage `stt_configuration` and presets once; reuse across connections.
- Keep routers thin; use DI services. Routers resolve `configuration_name` and call service_call_and_respond.

#### Defaults
- A single `default-speech` configuration SHOULD exist; clients can omit explicit selection if the server applies a default policy.


And here’s a super-short “front-file” snippet you can paste at the top of the project to reset context:

```text
STT CONFIG BASELINE (Nonix)

- No users. Client supplies configuration_name per connection/job.
- DB is the source of truth:
  stt_configuration (name) → engine/preprocess/streaming/features/postprocess presets.
- On connect: resolve configuration_name → build effective_config → snapshot to session/job.
- All behavior (denoise, VAD, streaming, timestamps, etc.) derives from the selected configuration.
- Routers thin. All logic in services. Reuse presets; no duplication.
```