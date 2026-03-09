Plan: Redesign CLI File Handling — Upload From Anywhere, Auto-Download Output                                                                                            
                                                                                                                                                                              
     Context                                                                                                                                                                  
                                                                                                                                                                              
     The current CLI requires local files to be in ./local/input/ for Docker volume mount access. Patrick wants --file /any/path/on/disk to just work — the CLI uploads       
     the file to the API automatically, processes it, and downloads the result back. This is the key workflow: Claude Code (or a user) has a file anywhere on disk,           
     passes it to the CLI, and gets a transcription or converted file back without caring about Docker internals.                                                             
                                                                                                                                                                              
     Design Decisions (confirmed by Patrick)                                                                                                                                  
                                                                                                                                                                              
     1. Always multipart upload — --file always uploads via HTTP POST to /v1/files/upload, even on localhost. Volume mounts remain as an optional advanced optimization.      
     2. Auto-download output — CLI downloads result files to current directory by default. --output-dir / -o to specify a different location.                                 
     3. Human-readable text by default — Transcription prints plain text. File commands print the local path of the downloaded file. --json flag for full JSON.               
     4. Transparent download — CLI handles both cloud URLs (HTTP download) and file:// paths (copy from ./local/output/) automatically.                                       
                                                                                                                                                                              
     Changes                                                                                                                                                                  
                                                                                                                                                                              
     1. services/file_management.py — Server-side fix (1 line)                                                                                                                
                                                                          
     Add /data/output to ALLOWED_LOCAL_DIRS. Currently the upload-then-process flow on localhost fails because:
     - Upload endpoint saves to /data/output via LocalStorageProvider     
     - Processing endpoint calls download_file() with the file:///data/output/... URL
     - ALLOWED_LOCAL_DIRS only has /data/input and /tmp — rejects /data/output                                                                                                

     # Line ~30, change:
     ALLOWED_LOCAL_DIRS = ['/data/input', os.environ.get('LOCAL_STORAGE_PATH', '/tmp')]
     # To:
     ALLOWED_LOCAL_DIRS = ['/data/input', '/data/output', os.environ.get('LOCAL_STORAGE_PATH', '/tmp')]

     2. tools/nca.py — Major CLI overhaul

     a. Simplify resolve_file() (line 204)

     Remove is_local_api() branch. Always upload:
     def resolve_file(local_path):
         """Upload local file to API, return the storage URL."""
         return upload_file_to_api(local_path)

     b. Add download_output(url, output_dir) function (new)

     - HTTP/HTTPS URLs → download via urllib.request.urlopen in 8KB chunks
     - file:// URLs → translate file:///data/output/X to ./local/output/X, copy with shutil.copy2
     - Returns local file path, or None on failure (prints warning to stderr)

     c. Add handle_output(result, command, output_dir, json_mode) function (new)

     Replaces print_result(). Logic per command type:

     ┌───────────────┬───────────────────────────────────────────────┬─────────────────────────────────────────────┐
     │ Command type  │                   Examples                    │                  Behavior                   │
     ├───────────────┼───────────────────────────────────────────────┼─────────────────────────────────────────────┤
     │ Text commands │ transcribe, metadata, silence, status, test   │ Print text/data directly to stdout          │
     ├───────────────┼───────────────────────────────────────────────┼─────────────────────────────────────────────┤
     │ File commands │ convert, caption, video-trim, thumbnail, etc. │ Download file, print local path             │
     ├───────────────┼───────────────────────────────────────────────┼─────────────────────────────────────────────┤
     │ --json mode   │ Any                                           │ Print full JSON response (current behavior) │
     └───────────────┴───────────────────────────────────────────────┴─────────────────────────────────────────────┘

     Special handling for transcribe: print response.text directly. If --srt was requested, also print SRT. If --segments, print segments as JSON.

     For 202 responses (webhook mode): print job_id and message, skip download.

     d. Add global --json and --output-dir flags (in build_parser(), line 671)

     parser.add_argument("--json", dest="json_output", action="store_true",
                         help="Output full JSON response")
     parser.add_argument("--output-dir", "-o", default=".",
                         help="Directory for downloaded output files (default: current directory)")

     e. Update all command handlers

     Replace print_result(result) with handle_output(result, "command-name", args.output_dir, args.json_output) in all 18 command handlers.

     f. Update all --file help text

     Change "Local file path (must be in ./local/input/)" → "Local file path (uploaded automatically)" across ~10 subcommands.

     g. Update epilog

     Remove ./local/input/ references. New text:
     Local files:
       Use --file with any path. Files are uploaded to the API automatically.
       Output files are downloaded to the current directory (use -o to change).

     h. Remove dead code

     Delete translate_output_paths() and print_result() — fully replaced by handle_output().

     3. tools/claude-skill/SKILL.md — Update documentation

     - Replace ./local/input/ references with generic paths (~/videos/meeting.mp4)
     - Document --output-dir / -o and --json flags
     - Update examples to show the new simpler workflow

     4. tools/claude-skill/Workflows/*.md — Update all workflow docs (7 files)

     Update these files to use generic file paths and document output behavior:
     - Transcribe.md, ConvertMedia.md, CaptionVideo.md, VideoOps.md
     - Metadata.md, Silence.md, FFmpeg.md
     - Upload.md — document the manual upload command

     No changes needed: Screenshot.md, Download.md, Setup.md, TestConnect.md

     Files NOT Changed

     - 0 route files — the /v1/files/upload endpoint already works
     - Dockerfile — /data/input and /data/output directories already exist
     - Makefile — up-local target already works (volume mounts are optional advanced feature)
     - config.py, .env.example — no new config needed

     Implementation Order

     1. services/file_management.py (1-line server fix)
     2. tools/nca.py (bulk of work — new functions, update handlers, cleanup)
     3. tools/claude-skill/SKILL.md (docs)
     4. tools/claude-skill/Workflows/*.md (docs)

     Verification

     1. Syntax check: python3 -m py_compile tools/nca.py
     2. Upload from anywhere (local API):
     python3 tools/nca.py transcribe --file ~/Desktop/test-audio.mp3
     # Should: upload file, transcribe, print text to stdout
     3. Output download (file command):
     python3 tools/nca.py convert --file ~/Desktop/video.mp4 --format webm
     # Should: upload, convert, download result to ./video.webm, print path
     4. Output to custom dir:
     python3 tools/nca.py convert --file ~/Desktop/video.mp4 --format webm -o ~/Downloads
     # Should: download result to ~/Downloads/video.webm
     5. JSON mode:
     python3 tools/nca.py transcribe --file ~/Desktop/test.mp3 --json
     # Should: print full JSON response
     6. URL input unchanged:
     python3 tools/nca.py transcribe --media-url https://example.com/audio.mp3
     # Should: work exactly as before