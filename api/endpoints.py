from typing import Dict, Any
from dataclasses import dataclass

# Base endpoints
SUBMIT_ANNOTATION = "annotations/submit"
SUBMISSION_STATUS = "submissions"
DATASET_INFO = "datasets"
LIST_DATASETS = "datasets/list"
CREATE_DATASET = "datasets/create"
UPDATE_DATASET = "datasets"
DELETE_SUBMISSION = "submissions"
USER_STATS = "users/stats"
VALIDATE_TOKEN = "auth/validate"
SEARCH_ANNOTATIONS = "annotations/search"
ANNOTATION_METRICS = "annotations/metrics"

@dataclass
class APIEndpoint:
    """API Endpoint definition"""
    path: str
    method: str
    requires_auth: bool = True
    rate_limit: int = 60  # requests per minute
    cache_ttl: int = 300  # cache time to live in seconds

    def get_full_path(self, version: str = "v1") -> str:
        """Get full endpoint path with version"""
        return f"/{version}/{self.path.lstrip('/')}"

# Detailed endpoint definitions
ENDPOINTS = {
    # Annotation endpoints
    "submit_annotation": APIEndpoint(
        path=SUBMIT_ANNOTATION,
        method="POST",
        rate_limit=30
    ),
    "get_submission_status": APIEndpoint(
        path=SUBMISSION_STATUS + "/{submission_id}",
        method="GET",
        cache_ttl=60
    ),

    # Dataset endpoints
    "get_dataset_info": APIEndpoint(
        path=DATASET_INFO + "/{dataset_id}",
        method="GET",
        cache_ttl=3600
    ),
    "list_datasets": APIEndpoint(
        path=LIST_DATASETS,
        method="GET",
        cache_ttl=3600
    ),
    "create_dataset": APIEndpoint(
        path=CREATE_DATASET,
        method="POST",
        rate_limit=10
    ),
    "update_dataset": APIEndpoint(
        path=UPDATE_DATASET + "/{dataset_id}",
        method="PUT",
        rate_limit=10
    ),

    # User endpoints
    "get_user_stats": APIEndpoint(
        path=USER_STATS,
        method="GET",
        cache_ttl=300
    ),
    "validate_token": APIEndpoint(
        path=VALIDATE_TOKEN,
        method="GET",
        cache_ttl=3600
    ),

    # Search endpoints
    "search_annotations": APIEndpoint(
        path=SEARCH_ANNOTATIONS,
        method="POST",
        rate_limit=30,
        cache_ttl=60
    ),
    "get_annotation_metrics": APIEndpoint(
        path=ANNOTATION_METRICS + "/{annotation_id}",
        method="GET",
        cache_ttl=3600
    ),
}

def get_endpoint(name: str) -> APIEndpoint:
    """Get endpoint by name"""
    return ENDPOINTS.get(name)

def format_path(endpoint: APIEndpoint, **kwargs) -> str:
    """Format endpoint path with parameters"""
    return endpoint.path.format(**kwargs)

class APISchemas:
    """API request/response schemas"""

    SUBMIT_ANNOTATION_SCHEMA = {
        "type": "object",
        "required": ["objects"],
        "properties": {
            "metadata": {
                "type": "object",
                "properties": {
                    "version": {"type": "string"},
                    "timestamp": {"type": "string"},
                    "author": {"type": "string"}
                }
            },
            "objects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "type", "tags"],
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "tags": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "color": {
                                        "type": "array",
                                        "items": {"type": "number"},
                                        "minItems": 3,
                                        "maxItems": 4
                                    }
                                }
                            }
                        },
                        "mesh_annotations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "tag": {"type": "string"},
                                    "vertices": {
                                        "type": "array",
                                        "items": {"type": "integer"}
                                    },
                                    "edges": {
                                        "type": "array",
                                        "items": {"type": "integer"}
                                    },
                                    "faces": {
                                        "type": "array",
                                        "items": {"type": "integer"}
                                    }
                                }
                            }
                        },
                        "animation_tracks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "property_path": {"type": "string"},
                                    "keyframes": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "frame": {"type": "integer"},
                                                "value": {},
                                                "interpolation": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    DATASET_SCHEMA = {
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "description": {"type": "string"},
            "public": {"type": "boolean"},
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }

    @staticmethod
    def validate_submission(data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate submission data against schema"""
        from jsonschema import validate, ValidationError
        try:
            validate(instance=data, schema=APISchemas.SUBMIT_ANNOTATION_SCHEMA)
            return True, ""
        except ValidationError as e:
            return False, str(e)

def register():
    pass  # No registration needed for endpoints

def unregister():
    pass
