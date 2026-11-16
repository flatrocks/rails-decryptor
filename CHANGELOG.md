# railsdecryptor changelog

## v1.0.0
  * **Major Feature**: Added support for both Rails 7.0 and Rails 7.1+ encryption methods
  * **Auto-Detection**: Automatic detection of encryption method - tries SHA-256 (Rails 7.1+) first, falls back to SHA-1 (Rails 7.0)
  * **Compression Support**: Automatic detection and decompression of zlib-compressed encrypted fields
  * **Comprehensive Testing**: Added test fixtures using real Rails 8.1 encryption with random keys (safe to commit), including compression tests
  * **Performance**: Minimal overhead - fallback only occurs for Rails 7.0 data, compression detection automatic

## v0.0.0
  * Initial release

