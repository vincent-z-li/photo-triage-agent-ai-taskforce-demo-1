class PhotoTriageError(Exception):
    pass


class ImageProcessingError(PhotoTriageError):
    pass


class QualityAnalysisError(PhotoTriageError):
    pass


class MCPServerError(PhotoTriageError):
    pass


class ValidationError(PhotoTriageError):
    pass


class ModelError(PhotoTriageError):
    pass