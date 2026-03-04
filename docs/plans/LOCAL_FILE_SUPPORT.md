Plan: Add Local File I/O Support via Docker Volume Mounts                                                                                                                
                                                                                                                                                                              
     Context                                                                                                                                                                  
                                                                          
     The NCA Toolkit API currently only accepts URLs for input and uploads all output to cloud storage (S3/GCP). Patrick wants to process local files when running the
     API in Docker on his local machine. Files may be too large for HTTP upload, so the approach uses Docker volume mounts — a shared folder on the host that the
     container can read/write directly. This also makes cloud storage optional for local development.
                                                                          
     Approach: Volume Mounts + file:// URIs                                      
                                                                                 
     How it works:                                                        
     1. Host directories ./local/input and ./local/output are mounted into the container at /data/input and /data/output
     2. User places files in ./local/input/ on their host machine         
     3. API requests use file:///data/input/filename.mp4 instead of an HTTP URL
     4. download_file() detects file:// scheme and copies the local file instead of HTTP downloading
     5. When no cloud storage is configured, output files are saved to /data/output (visible at ./local/output/ on host)
     6. CLI auto-translates --file ./local/input/video.mp4 to the file:// URI
                                                                     
     Why not multipart upload: Volume mounts handle large files natively (no size limits, no HTTP timeouts, no memory buffering). No route or schema changes needed.
                                                                          
     Schema validation confirmed: The codebase does NOT use jsonschema.FormatChecker, so "format": "uri" is not enforced — any string passes. Zero schema changes needed.     

     Changes (7 files, 0 route files)

     1. Dockerfile — Create mount point directories

     Add before USER appuser:
     RUN mkdir -p /data/input /data/output && chown appuser:appuser /data/input /data/output

     2. services/file_management.py — Handle file:// URIs

     - Modify get_extension_from_url(): if scheme is file, get extension from path directly (skip HTTP HEAD request)
     - Modify download_file(): if scheme is file, copy the local file instead of HTTP download
     - Add path traversal protection: restrict file:// to /data/input and LOCAL_STORAGE_PATH
     - Use shutil.copy2() (not symlink) so existing cleanup code (os.remove()) doesn't delete the user's original file

     3. services/cloud_storage.py — Add LocalStorageProvider fallback

     - Add LocalStorageProvider class that copies output to /data/output and returns file:// URI
     - Modify get_storage_provider(): instead of raising ValueError when no cloud storage is configured, return LocalStorageProvider
     - New env var: LOCAL_OUTPUT_PATH (defaults to /data/output)

     4. config.py — Add LOCAL_OUTPUT_PATH

     LOCAL_OUTPUT_PATH = os.environ.get('LOCAL_OUTPUT_PATH', '/data/output')

     5. .env.example — Document new option

     Add commented LOCAL_OUTPUT_PATH variable.

     6. Makefile — Add up-local target

     New target that creates ./local/input and ./local/output directories, then runs Docker with volume mounts:
     -v $(CURDIR)/local/input:/data/input:ro
     -v $(CURDIR)/local/output:/data/output
     Also add to help menu. Keep existing up target unchanged for cloud users.

     7. tools/nca.py — Add --file flag and output path translation

     - Add --file / -f argument to commands that accept URL inputs
     - Make --file and --media-url/--video-url mutually exclusive
     - When --file is used, translate to file:///data/input/<basename>
     - When response contains file:///data/output/..., translate to ./local/output/... in display

     Files NOT Changed

     - 0 route files — routes pass URLs to services unchanged
     - 0 service files (other than file_management.py and cloud_storage.py) — services call download_file() which handles the new scheme transparently
     - 0 JSON schemas — format: uri is not enforced by default jsonschema

     Implementation Order

     1. Dockerfile (create directories)
     2. services/file_management.py (input handling)
     3. services/cloud_storage.py (output handling)
     4. config.py (new env var)
     5. .env.example (documentation)
     6. Makefile (up-local target + help)
     7. tools/nca.py (CLI convenience)

     Verification

     1. make up-local — container starts with volume mounts
     2. Place a test file in ./local/input/test.mp4
     3. Call API with file:///data/input/test.mp4 as the media URL (no cloud storage configured)
     4. Verify output appears in ./local/output/
     5. Call API with a regular HTTP URL — verify existing behavior unchanged
     6. Test via CLI: python3 tools/nca.py transcribe --file ./local/input/test.mp4