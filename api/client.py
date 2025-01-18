import requests
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from . import endpoints
from . import API_VERSION, DEFAULT_API_URL, DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """API Response container"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None

class BlendTaggerAPI:
    """BlendTagger API Client"""

    def __init__(self, api_key: str, base_url: str = DEFAULT_API_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': f'BlendTagger-Client/{API_VERSION}'
        })

    def _make_request(self,
                     method: str,
                     endpoint: str,
                     data: Optional[Dict] = None,
                     params: Optional[Dict] = None) -> APIResponse:
        """Make HTTP request to API"""
        url = f"{self.base_url}/{API_VERSION}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data if data else None,
                params=params if params else None,
                timeout=DEFAULT_TIMEOUT
            )

            response.raise_for_status()
            return APIResponse(
                success=True,
                data=response.json() if response.content else None,
                status_code=response.status_code
            )

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e.response, 'json'):
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', error_msg)
                except:
                    pass

            logger.error(f"API request failed: {error_msg}")
            return APIResponse(
                success=False,
                error=error_msg,
                status_code=e.response.status_code if hasattr(e, 'response') else None
            )

    def submit_annotation(self, data: Dict[str, Any]) -> APIResponse:
        """Submit annotation data to repository"""
        return self._make_request('POST', endpoints.SUBMIT_ANNOTATION, data=data)

    def get_submission_status(self, submission_id: str) -> APIResponse:
        """Get status of a submission"""
        return self._make_request('GET', f"{endpoints.SUBMISSION_STATUS}/{submission_id}")

    def get_dataset_info(self, dataset_id: str) -> APIResponse:
        """Get information about a dataset"""
        return self._make_request('GET', f"{endpoints.DATASET_INFO}/{dataset_id}")

    def list_datasets(self, page: int = 1, per_page: int = 20) -> APIResponse:
        """List available datasets"""
        params = {'page': page, 'per_page': per_page}
        return self._make_request('GET', endpoints.LIST_DATASETS, params=params)

    def create_dataset(self, name: str, description: str) -> APIResponse:
        """Create a new dataset"""
        data = {
            'name': name,
            'description': description
        }
        return self._make_request('POST', endpoints.CREATE_DATASET, data=data)

    def update_dataset(self, dataset_id: str, data: Dict[str, Any]) -> APIResponse:
        """Update dataset information"""
        return self._make_request('PUT', f"{endpoints.UPDATE_DATASET}/{dataset_id}", data=data)

    def delete_submission(self, submission_id: str) -> APIResponse:
        """Delete a submission"""
        return self._make_request('DELETE', f"{endpoints.DELETE_SUBMISSION}/{submission_id}")

    def get_user_stats(self) -> APIResponse:
        """Get user statistics"""
        return self._make_request('GET', endpoints.USER_STATS)

    def validate_token(self) -> APIResponse:
        """Validate API token"""
        return self._make_request('GET', endpoints.VALIDATE_TOKEN)

    def search_annotations(self,
                         query: str,
                         filters: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Search annotations in repository"""
        data = {
            'query': query,
            'filters': filters or {}
        }
        return self._make_request('POST', endpoints.SEARCH_ANNOTATIONS, data=data)

    def get_annotation_metrics(self, annotation_id: str) -> APIResponse:
        """Get metrics for specific annotation"""
        return self._make_request('GET', f"{endpoints.ANNOTATION_METRICS}/{annotation_id}")

    def batch_submit(self, submissions: List[Dict[str, Any]]) -> List[APIResponse]:
        """Submit multiple annotations in batch"""
        responses = []
        for submission in submissions:
            response = self.submit_annotation(submission)
            responses.append(response)
        return responses

class APICache:
    """Cache for API responses"""
    def __init__(self, max_size: int = 100):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if available"""
        import time
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < 300:  # 5 minute cache
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Cache a value"""
        import time
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._cache.keys(),
                           key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        self._cache[key] = (value, time.time())

def register():
    pass  # No registration needed for API client

def unregister():
    pass
