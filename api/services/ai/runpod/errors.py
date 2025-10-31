from enum import Enum


class ErrorCode(str, Enum):
    CONFIG_NOT_FOUND = "CONFIG_NOT_FOUND"
    RUNPOD_API_KEY_MISSING = "RUNPOD_API_KEY_MISSING"
    POD_CREATION_FAILED = "POD_CREATION_FAILED"
    POD_NOT_READY = "POD_NOT_READY"
    POD_CONNECTION_FAILED = "POD_CONNECTION_FAILED"
    POD_ALLOCATION_TIMEOUT = "POD_ALLOCATION_TIMEOUT"
    WORKFLOW_UNKNOWN = "WORKFLOW_UNKNOWN"
    WORKFLOW_EXECUTION_FAILED = "WORKFLOW_EXECUTION_FAILED"
    RSYNC_FAILED = "RSYNC_FAILED"
    HTTP_DOWNLOAD_FAILED = "HTTP_DOWNLOAD_FAILED"
    FILE_TRANSFER_FAILED = "FILE_TRANSFER_FAILED"
    QUEUE_NOT_RUNNING = "QUEUE_NOT_RUNNING"
    REQUEST_TIMEOUT = "REQUEST_TIMEOUT"
    INVALID_INPUT = "INVALID_INPUT"


ERROR_MESSAGES = {
    ErrorCode.CONFIG_NOT_FOUND: "Required configuration file not found",
    ErrorCode.RUNPOD_API_KEY_MISSING: "RunPod API key not found",
    ErrorCode.POD_CREATION_FAILED: "Failed to create RunPod pod",
    ErrorCode.POD_NOT_READY: "Pod did not become ready in time",
    ErrorCode.POD_CONNECTION_FAILED: "Failed to get pod connection info",
    ErrorCode.POD_ALLOCATION_TIMEOUT: "Pod allocation timed out",
    ErrorCode.WORKFLOW_UNKNOWN: "Unknown workflow requested",
    ErrorCode.WORKFLOW_EXECUTION_FAILED: "Workflow execution failed",
    ErrorCode.RSYNC_FAILED: "Rsync transfer failed",
    ErrorCode.HTTP_DOWNLOAD_FAILED: "HTTP download failed",
    ErrorCode.FILE_TRANSFER_FAILED: "Failed to transfer generated file",
    ErrorCode.QUEUE_NOT_RUNNING: "Queue manager is not running",
    ErrorCode.REQUEST_TIMEOUT: "Workflow execution timed out",
    ErrorCode.INVALID_INPUT: "Invalid or missing input",
}


