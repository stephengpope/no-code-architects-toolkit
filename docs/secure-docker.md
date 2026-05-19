# Secured Docker image (multi-stage)

`Dockerfile.multistage` is an alternative, CVE-hardened build of the NCA toolkit
image. The default `Dockerfile` is unchanged — use this one if you want a
smaller, more locked-down image and don't need the Playwright-backed
screenshot endpoint.

## Build

```bash
docker build -f Dockerfile.multistage -t nca-toolkit:secured .
```

Run it the same way as the default image.

## What changes

- **Multi-stage build.** Compilers, `-dev` headers, and other build tools live
  only in the builder stage and never reach the final image. The runtime stage
  contains just the shared libraries ffmpeg needs.
- **Playwright + Chromium are not installed.** This closes several HIGH CVEs
  (nss, cups, and others pulled in by Chromium) at the cost of disabling the
  `POST /v1/image/screenshot_webpage` endpoint on this image. All other
  endpoints behave identically.
- **gnutls removed.** ffmpeg is built without `--enable-gnutls`; SRT uses the
  openssl backend. Closes the gnutls CVE cluster.
- **libtheora dropped from ffmpeg.** Re-add `--enable-libtheora` to the
  `configure` line if you need Theora output.
- **Pinned pip baselines.** `wheel`, `setuptools`, and `jaraco.context` are
  pinned to patched versions at install time.
- **Trixie point release.** `apt-get -y upgrade` runs in the runtime stage to
  pick up the latest Debian trixie patches at build time.

## When to use the default Dockerfile instead

- You use `POST /v1/image/screenshot_webpage` and need Playwright/Chromium.
- You need Theora output from ffmpeg.
- You rely on the gnutls TLS backend specifically.

## Image size

Smaller than the single-stage image — compilers and `-dev` packages don't ship.
Exact numbers depend on base image versions at build time.
