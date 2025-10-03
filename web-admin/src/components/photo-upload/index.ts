// Photo upload components
export { PhotoUploader } from './PhotoUploader'
export { PhotoGallery } from './PhotoGallery'
export { PhotoManager } from './PhotoManager'

// Re-export types
export type { 
  PhotoUpload, 
  PhotoMetadata, 
  UploadProgress, 
  UploadError,
  PhotoGalleryItem,
  PhotoGallery as PhotoGalleryType,
  PresignedUrlRequest,
  PresignedUrlResponse,
  UploadSession
} from '@/lib/types/photo-upload'

// Re-export services
export { uploadService } from '@/lib/services/upload-service'
export { EXIFExtractor, FileValidator } from '@/lib/utils/exif'