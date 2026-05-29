"""
CV-Craft-Studio - Resume Version History
Session-based versioning with JSON import/export. No database required.
"""

import json
import copy
import datetime
from typing import List, Dict, Optional
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

VERSION_KEY = 'resume_versions'
MAX_VERSIONS = 20


def init_version_history():
    """Initialize version history in session state."""
    if VERSION_KEY not in st.session_state:
        st.session_state[VERSION_KEY] = []


def save_version(resume_data: Dict, label: str = '') -> Dict:
    """
    Save current resume data as a new version.
    Returns the saved version dict.
    """
    init_version_history()
    now = datetime.datetime.now()
    version = {
        'id': len(st.session_state[VERSION_KEY]) + 1,
        'label': label or f'Version {len(st.session_state[VERSION_KEY]) + 1}',
        'timestamp': now.isoformat(),
        'timestamp_display': now.strftime('%d %b %Y, %I:%M %p'),
        'data': copy.deepcopy(resume_data),
        'summary': _get_version_summary(resume_data),
    }
    versions = st.session_state[VERSION_KEY]
    versions.append(version)
    # Keep only last MAX_VERSIONS
    if len(versions) > MAX_VERSIONS:
        st.session_state[VERSION_KEY] = versions[-MAX_VERSIONS:]
    return version


def get_versions() -> List[Dict]:
    """Return all saved versions, newest first."""
    init_version_history()
    return list(reversed(st.session_state[VERSION_KEY]))


def load_version(version_id: int) -> Optional[Dict]:
    """Load a specific version by ID."""
    init_version_history()
    for v in st.session_state[VERSION_KEY]:
        if v['id'] == version_id:
            return copy.deepcopy(v['data'])
    return None


def delete_version(version_id: int) -> bool:
    """Delete a specific version by ID."""
    init_version_history()
    before = len(st.session_state[VERSION_KEY])
    st.session_state[VERSION_KEY] = [
        v for v in st.session_state[VERSION_KEY] if v['id'] != version_id
    ]
    return len(st.session_state[VERSION_KEY]) < before


def clear_all_versions():
    """Delete all saved versions."""
    st.session_state[VERSION_KEY] = []


def _get_version_summary(resume_data: Dict) -> Dict:
    """Get a quick summary of the resume data for display."""
    name = resume_data.get('personal', {}).get('name', 'Unnamed')
    sections = []
    if resume_data.get('summary'):
        sections.append('Summary')
    if resume_data.get('education'):
        sections.append(f"{len(resume_data['education'])} Education")
    if resume_data.get('experience'):
        sections.append(f"{len(resume_data['experience'])} Experience")
    if resume_data.get('projects'):
        sections.append(f"{len(resume_data['projects'])} Projects")
    if resume_data.get('skills'):
        sections.append('Skills')
    if resume_data.get('certifications'):
        sections.append(f"{len(resume_data['certifications'])} Certs")
    return {
        'name': name,
        'sections': sections,
        'section_count': len(sections),
    }


# ─────────────────────────────────────────────────────────────────────────────
# JSON EXPORT / IMPORT
# ─────────────────────────────────────────────────────────────────────────────

def export_all_versions_json() -> bytes:
    """Export all versions as a JSON file."""
    init_version_history()
    export_data = {
        'app': 'CV-Craft-Studio',
        'exported_at': datetime.datetime.now().isoformat(),
        'version_count': len(st.session_state[VERSION_KEY]),
        'versions': st.session_state[VERSION_KEY],
    }
    return json.dumps(export_data, indent=2, ensure_ascii=False).encode('utf-8')


def export_single_version_json(version_id: int) -> Optional[bytes]:
    """Export a single version as JSON."""
    init_version_history()
    for v in st.session_state[VERSION_KEY]:
        if v['id'] == version_id:
            return json.dumps(v['data'], indent=2, ensure_ascii=False).encode('utf-8')
    return None


def import_versions_json(json_bytes: bytes) -> Dict:
    """
    Import versions from a JSON file.
    Returns {'success': bool, 'count': int, 'error': str}
    """
    init_version_history()
    try:
        data = json.loads(json_bytes.decode('utf-8'))
        if 'versions' in data:
            imported = data['versions']
        elif isinstance(data, list):
            imported = data
        elif isinstance(data, dict) and 'personal' in data:
            # Single resume JSON
            imported = [{
                'id': len(st.session_state[VERSION_KEY]) + 1,
                'label': 'Imported Resume',
                'timestamp': datetime.datetime.now().isoformat(),
                'timestamp_display': datetime.datetime.now().strftime('%d %b %Y, %I:%M %p'),
                'data': data,
                'summary': _get_version_summary(data),
            }]
        else:
            return {'success': False, 'count': 0, 'error': 'Unrecognized JSON format'}

        existing_ids = {v['id'] for v in st.session_state[VERSION_KEY]}
        added = 0
        for v in imported:
            if isinstance(v, dict):
                # Re-assign ID to avoid conflicts
                v['id'] = max((x['id'] for x in st.session_state[VERSION_KEY]), default=0) + 1
                if 'summary' not in v and 'data' in v:
                    v['summary'] = _get_version_summary(v['data'])
                st.session_state[VERSION_KEY].append(v)
                added += 1

        return {'success': True, 'count': added, 'error': ''}
    except Exception as e:
        return {'success': False, 'count': 0, 'error': str(e)}


def get_version_count() -> int:
    init_version_history()
    return len(st.session_state[VERSION_KEY])
