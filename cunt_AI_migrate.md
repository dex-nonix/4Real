# Migration System - Final Implementation

## Architecture Integration

Your system uses **AsyncSessionLocal** for all database access. Migrations integrate as a service that can be injected anywhere using `@NxInject(MigrationService)`.

## MigrationService Implementation

```python
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy import text
from nonix_web_db import AsyncSessionLocal

class MigrationService:
    """Injectable migration service using AsyncSessionLocal"""

    def __init__(self):
        self.migration_dir = Path("./migrations")
        self.log_file = self.migration_dir / ".migration_log"
        self.error_log_file = self.migration_dir / ".migration_errors.log"

    async def run_all_migrations(self) -> Dict[str, Any]:
        """Execute all pending migrations atomically"""
        session = AsyncSessionLocal()

        try:
            pending = await self._get_pending_migrations()

            for migration_dir in pending:
                await self._execute_migration_point(session, migration_dir)

            await session.commit()
            await self._log_successful_migrations(pending)

            return {"status": "success", "count": len(pending)}

        except Exception as e:
            await session.rollback()
            await self._log_error(str(e))
            return {"status": "error", "error": str(e)}

        finally:
            await session.close()

    async def _execute_migration_point(self, session, migration_dir: Path):
        """Execute files in migration directory using shared session"""
        files = sorted([f for f in migration_dir.iterdir() if f.is_file()])

        for file_path in files:
            if file_path.suffix == '.sql':
                sql = await self._read_file(file_path)
                await session.execute(text(sql))
            elif file_path.suffix == '.py':
                await self._execute_python_migration(session, file_path)

    async def _execute_python_migration(self, session, file_path: Path):
        """Execute Python migration with session access"""
        code = await self._read_file(file_path)
        globals_dict = {'session': session}
        exec(code, globals_dict)

    async def _get_pending_migrations(self) -> List[Path]:
        """Get unexecuted migration directories, sorted alphabetically"""
        if not self.migration_dir.exists():
            return []

        executed = await self._get_executed_ids()
        pending = [d for d in self.migration_dir.iterdir()
                  if d.is_dir() and d.name not in executed]
        return sorted(pending, key=lambda x: x.name)

    async def _get_executed_ids(self) -> set:
        """Get IDs of executed migrations"""
        if not self.log_file.exists():
            return set()
        content = await self._read_file(self.log_file)
        return set(line.strip() for line in content.splitlines())

    async def _log_successful_migrations(self, migrations: List[Path]):
        """Log completed migrations"""
        for migration in migrations:
            await self._append_file(self.log_file, f"{migration.name}\n")

    async def _log_error(self, error: str):
        """Log errors with timestamp"""
        import datetime
        timestamp = datetime.datetime.now().isoformat()
        await self._append_file(self.error_log_file, f"[{timestamp}] {error}\n")

    async def _read_file(self, path: Path) -> str:
        """Async file reading"""
        import aiofiles
        async with aiofiles.open(path, 'r') as f:
            return await f.read()

    async def _append_file(self, path: Path, content: str):
        """Async file appending"""
        import aiofiles
        async with aiofiles.open(path, 'a') as f:
            await f.write(content)
```

## Service Registration

Add to your plugin's injectables:

```python
@injectables([
    # ... existing services ...
    MigrationService
])
class NxWebAgenticPlugin(BasePlugin):
    pass
```

## Usage Examples

**API Endpoint:**
```python
@router("/migrations")
class MigrationRouter:
    migration_service = NxInject(MigrationService)

    @route("/run", methods=["POST"])
    async def run(self):
        return await self.migration_service.run_all_migrations()
```

**Python Migration File:**
```python
# Inside migration files, session is available
users = await session.execute(select(User))
for user in users.scalars():
    user.migrated = True
```

## File Structure

```
migrations/
├── 001_initial/
│   ├── create_tables.sql
│   └── seed_data.py
├── 002_updates/
│   └── alter_schema.sql
├── .migration_log
└── .migration_errors.log
```

## Key Features

- **Single Session**: One AsyncSessionLocal session for entire migration run
- **Atomic Transactions**: All migrations commit together or rollback together
- **Injectable**: Can be used from routers, services, or anywhere
- **Async Compatible**: Works with your existing async patterns
- **Error Logging**: Comprehensive error tracking
- **File Sorting**: Alphabetical execution within migration directories

This integrates seamlessly with your AsyncSessionLocal architecture and dependency injection system.