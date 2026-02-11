import asyncio
import uuid
from datetime import datetime
from pathlib import Path

from specs import validate_product_spec, validate_design_spec
from file_generator import generate_project_files
from state_machine import ProjectStateMachine

# A tiny in-memory mock for motor's AsyncIOMotorClient database and collections
class MockCollection:
    def __init__(self):
        self.store = {}

    async def insert_one(self, doc):
        key = doc.get('project_id') or doc.get('id') or str(len(self.store)+1)
        self.store[key] = doc
        return type('R', (), {'inserted_id': key})

    async def find_one(self, filter, projection=None):
        # simple find by project_id or id
        for v in self.store.values():
            match = True
            for k, val in filter.items():
                if v.get(k) != val:
                    match = False
                    break
            if match:
                # emulate motor returning dict-like object
                return v
        return None

    async def update_one(self, filter, update, upsert=False):
        existing = await self.find_one(filter)
        if not existing and upsert:
            # build new
            new = {'project_id': filter.get('project_id')}
            # apply $set
            if '$set' in update:
                new.update(update['$set'])
            self.store[new['project_id']] = new
            return type('R', (), {'matched_count': 0, 'modified_count': 0})
        if not existing:
            return type('R', (), {'matched_count': 0, 'modified_count': 0})
        # apply $set
        if '$set' in update:
            existing.update(update['$set'])
        # apply $push for history
        if '$push' in update:
            for k, v in update['$push'].items():
                existing.setdefault(k, []).append(v)
        self.store[existing.get('project_id') or existing.get('id')] = existing
        return type('R', (), {'matched_count': 1, 'modified_count': 1})


class MockDB:
    def __init__(self):
        self.projects = MockCollection()
        self.project_specs = MockCollection()
        self.generated_results = MockCollection()

    def __getitem__(self, name):
        # Return self as a db with collections
        return self


class MockClient:
    def __init__(self):
        self._db = MockDB()

    def __getitem__(self, name):
        return self._db


async def main():
    print('\n=== E2E SMOKE: specs -> state -> generation ===')

    client = MockClient()
    psm = ProjectStateMachine(client, 'mockdb')

    project_id = str(uuid.uuid4())

    # Create project
    doc = await psm.create_project(project_id, 'E2E Test Project', 'user-123')
    print('Project created:', doc)

    # Prepare specs
    product_spec = {
        'name': 'E2EApp',
        'description': 'End-to-end test app',
        'features': [
            {'id': 'f1', 'name': 'Auth', 'description': 'User auth'}
        ]
    }
    design_spec = {
        'name': 'E2EDesign',
        'description': 'Simple design',
        'pages': [
            {'id': 'p1', 'route': '/', 'title': 'Home', 'components': []}
        ]
    }

    v1, e1 = validate_product_spec(product_spec)
    v2, e2 = validate_design_spec(design_spec)
    print('Product valid:', v1, 'Design valid:', v2)
    if not (v1 and v2):
        print('Validation errors:', e1, e2)
        return

    # Simulate storing specs
    await client._db.project_specs.insert_one({'project_id': project_id, 'product_spec': product_spec, 'design_spec': design_spec, 'updated_at': datetime.utcnow().isoformat()})

    # Transition to ARCHITECTED
    await psm.transition(project_id, 'ARCHITECTED', 'user-123')
    proj = await psm.get(project_id)
    print('After transition:', proj)

    # Run file generation
    orchestrator_outputs = {
        'product_manager': product_spec,
        'ui_designer': design_spec,
        'frontend_engineer': {
            'code': 'FILE: frontend/src/pages/index.tsx\n```tsx\nexport default function Home(){ return <h1>E2E Home</h1> }\n```'
        },
        'backend_engineer': {
            'code': 'FILE: server.js\n```js\nconsole.log("server")\n```'
        }
    }

    res = await generate_project_files(project_id, orchestrator_outputs, output_dir='./generated_projects_e2e')
    print('\nGeneration completed. Summary:')
    print(res)


if __name__ == '__main__':
    asyncio.run(main())
