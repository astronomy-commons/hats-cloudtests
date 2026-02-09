# Debugging number of operations/connections with HTTP

- Changed the http internal process to log all requests to a text file.
- Ran a single unit test. `$ pytest --cloud=http -k test_cone_search_filters_correct`
- Look at how very many file requests are happening:

```
127.0.0.1 - - [09/Feb/2026 13:46:24] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:24] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:24] code 404, message File not found
127.0.0.1 - - [09/Feb/2026 13:46:24] "GET /data/small_sky_order1/hats.properties HTTP/1.1" 404 -
127.0.0.1 - - [09/Feb/2026 13:46:24] code 404, message File not found
127.0.0.1 - - [09/Feb/2026 13:46:24] "GET /data/small_sky_order1/properties HTTP/1.1" 404 -
127.0.0.1 - - [09/Feb/2026 13:46:24] "GET /data/small_sky_order1/collection.properties HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:24] "GET /data/small_sky_order1/collection.properties HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:24] "HEAD /data/small_sky_order1/collection.properties HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:24] "GET /data/small_sky_order1/collection.properties HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/hats.properties HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/hats.properties HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/hats.properties HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/dataset/_common_metadata HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/dataset/_metadata HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/dataset/_common_metadata HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/dataset/_common_metadata HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/dataset/_common_metadata HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/dataset/_common_metadata HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/partition_info.csv HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/partition_info.csv HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/partition_info.csv HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/partition_info.csv HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/point_map.fits HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/point_map.fits HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/point_map.fits HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1_margin/hats.properties HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1_margin/hats.properties HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1_margin/hats.properties HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1_margin/hats.properties HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1_margin/dataset/_common_metadata HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1_margin/dataset/_metadata HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1_margin/dataset/_common_metadata HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1_margin/dataset/_common_metadata HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1_margin/dataset/_common_metadata HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1_margin/dataset/_common_metadata HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1_margin/partition_info.csv HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1_margin/partition_info.csv HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1_margin/partition_info.csv HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1_margin/partition_info.csv HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] code 404, message File not found
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1_margin/point_map.fits HTTP/1.1" 404 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=45.parquet?columns=id,ra,dec,ra_error,dec_error&filters=_healpix_29%3E%3D3170534137668829184,_healpix_29%3C3314649325744685056 HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=44.parquet?columns=id,ra,dec,ra_error,dec_error&filters=_healpix_29%3E%3D3170534137668829184,_healpix_29%3C3314649325744685056 HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=45.parquet?columns=id,ra,dec,ra_error,dec_error&filters=_healpix_29%3E%3D3170534137668829184,_healpix_29%3C3314649325744685056 HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=44.parquet?columns=id,ra,dec,ra_error,dec_error&filters=_healpix_29%3E%3D3170534137668829184,_healpix_29%3C3314649325744685056 HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=45.parquet?columns=id,ra,dec,ra_error,dec_error&filters=_healpix_29%3E%3D3170534137668829184,_healpix_29%3C3314649325744685056 HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=44.parquet?columns=id,ra,dec,ra_error,dec_error&filters=_healpix_29%3E%3D3170534137668829184,_healpix_29%3C3314649325744685056 HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=47.parquet HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=45.parquet HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=44.parquet HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=46.parquet HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=47.parquet HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=45.parquet HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=44.parquet HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "GET /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=46.parquet HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=47.parquet HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=44.parquet HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=45.parquet HTTP/1.1" 200 -
127.0.0.1 - - [09/Feb/2026 13:46:25] "HEAD /data/small_sky_order1/small_sky_order1/dataset/Norder=1/Dir=0/Npix=46.parquet HTTP/1.1" 200 -
```