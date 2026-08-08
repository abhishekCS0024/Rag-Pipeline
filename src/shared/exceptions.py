class AppError(Exception):
    pass


class DocumentNotFoundError(AppError):
    pass


class UnsupportedFileTypeError(AppError):
    pass


class ParsingError(AppError):
    pass


class StorageError(AppError):
    pass
