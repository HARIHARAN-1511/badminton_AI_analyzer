import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'
import './VideoUpload.css'

function VideoUpload({ onUploadComplete }) {
    const [uploading, setUploading] = useState(false)
    const [uploadProgress, setUploadProgress] = useState(0)
    const [error, setError] = useState(null)
    const [selectedFile, setSelectedFile] = useState(null)

    const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
        setError(null)

        if (rejectedFiles.length > 0) {
            const rejection = rejectedFiles[0]
            if (rejection.errors[0]?.code === 'file-too-large') {
                setError('File is too large. Maximum size is 2GB.')
            } else if (rejection.errors[0]?.code === 'file-invalid-type') {
                setError('Invalid file type. Only MP4 files are accepted.')
            } else {
                setError('File rejected. Please try again.')
            }
            return
        }

        if (acceptedFiles.length > 0) {
            setSelectedFile(acceptedFiles[0])
        }
    }, [])

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'video/mp4': ['.mp4']
        },
        maxSize: 2 * 1024 * 1024 * 1024, // 2GB
        multiple: false
    })

    const handleUpload = async () => {
        if (!selectedFile) return

        setUploading(true)
        setUploadProgress(0)
        setError(null)

        const formData = new FormData()
        formData.append('file', selectedFile)

        try {
            const response = await axios.post('/api/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                onUploadProgress: (progressEvent) => {
                    const progress = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    )
                    setUploadProgress(progress)
                }
            })

            if (response.data.success) {
                onUploadComplete(response.data)
            }
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                'Upload failed. Please try again.'
            )
        } finally {
            setUploading(false)
        }
    }

    const cancelSelection = () => {
        setSelectedFile(null)
        setError(null)
        setUploadProgress(0)
    }

    const formatFileSize = (bytes) => {
        if (bytes < 1024) return bytes + ' B'
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
        if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
        return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
    }

    return (
        <div className="video-upload">
            {!selectedFile ? (
                <div
                    {...getRootProps()}
                    className={`dropzone ${isDragActive ? 'active' : ''}`}
                >
                    <input {...getInputProps()} />
                    <div className="dropzone-content">
                        <div className="dropzone-icon">📹</div>
                        <h3>Drag & drop your video here</h3>
                        <p>or click to browse files</p>
                        <span className="dropzone-hint">MP4 format • Max 2GB</span>
                    </div>
                </div>
            ) : (
                <div className="file-selected">
                    <div className="file-info">
                        <div className="file-icon">🎬</div>
                        <div className="file-details">
                            <h4>{selectedFile.name}</h4>
                            <p>{formatFileSize(selectedFile.size)}</p>
                        </div>
                        {!uploading && (
                            <button className="btn-remove" onClick={cancelSelection}>
                                ✕
                            </button>
                        )}
                    </div>

                    {uploading ? (
                        <div className="upload-progress">
                            <div className="progress-bar">
                                <div
                                    className="progress-bar-fill"
                                    style={{ width: `${uploadProgress}%` }}
                                />
                            </div>
                            <span className="progress-text">
                                Uploading... {uploadProgress}%
                            </span>
                        </div>
                    ) : (
                        <button
                            className="btn btn-primary btn-lg upload-btn"
                            onClick={handleUpload}
                        >
                            ⬆️ Upload Video
                        </button>
                    )}
                </div>
            )}

            {error && (
                <div className="upload-error">
                    <span>⚠️</span> {error}
                </div>
            )}
        </div>
    )
}

export default VideoUpload
