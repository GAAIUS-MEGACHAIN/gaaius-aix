from typing import Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

# State definitions
STATES = [
    'CREATED',
    'SPEC_GENERATED',
    'ARCHITECTED',
    'CODE_GENERATED',
    'VALIDATED',
    'RUNNING',
    'DEPLOYABLE'
]


class ProjectStateMachine:
    def __init__(self, db_client: AsyncIOMotorClient, db_name: str):
        self.db = db_client[db_name]

    async def create_project(self, project_id: str, name: str, owner: str) -> Dict[str, Any]:
        doc = {
            'project_id': project_id,
            'name': name,
            'owner': owner,
            'state': 'CREATED',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'meta': {}
        }
        await self.db.projects.insert_one(doc)
        return doc

    async def get(self, project_id: str) -> Dict[str, Any]:
        return await self.db.projects.find_one({'project_id': project_id}, {'_id': 0})

    async def transition(self, project_id: str, to_state: str, actor: str) -> Dict[str, Any]:
        if to_state not in STATES:
            raise ValueError('Invalid state')

        current = await self.get(project_id)
        if not current:
            raise ValueError('Project not found')

        # Very simple state progression guard: new state must be in STATES
        await self.db.projects.update_one(
            {'project_id': project_id},
            {'$set': {'state': to_state, 'updated_at': datetime.utcnow().isoformat()}, '$push': {'history': {'ts': datetime.utcnow().isoformat(), 'actor': actor, 'to': to_state}}}
        )
        return await self.get(project_id)
