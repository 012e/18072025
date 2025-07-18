type FileId = int
type FileContentHash = str

type ContentLock = dict[FileId, FileContentHash]
