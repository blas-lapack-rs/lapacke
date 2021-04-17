# LAPACKE [![Package][package-img]][package-url] [![Documentation][documentation-img]][documentation-url] [![Build][build-img]][build-url]

The package provides wrappers for [LAPACKE] (C).

## [Architecture]

## Example

```rust
use lapacke::*;

let n = 3;
let mut a = vec![
    3.0, 1.0, 1.0,
    1.0, 3.0, 1.0,
    1.0, 1.0, 3.0,
];
let mut w = vec![0.0; n as usize];
let info;

unsafe {
    info = dsyev(Layout::ColumnMajor, b'V', b'U', n, &mut a, n, &mut w);
}

assert!(info == 0);
for (one, another) in w.iter().zip(&[2.0, 2.0, 5.0]) {
    assert!((one - another).abs() < 1e-14);
}
```

## Development

The function definitions are generated via a Python script based on the content
of [`lapacke-sys`]. To re-generate, run the following commands:

```sh
./bin/generate.py --sys ../lapacke-sys > src/functions.rs
rustfmt src/functions.rs
```

## Contribution

Your contribution is highly appreciated. Do not hesitate to open an issue or a
pull request. Note that any contribution submitted for inclusion in the project
will be licensed according to the terms given in [LICENSE.md](LICENSE.md).

[architecture]: https://blas-lapack-rs.github.io/architecture
[lapacke]: https://en.wikipedia.org/wiki/LAPACK

[`lapacke-sys`]: https://github.com/blas-lapack-rs/lapacke-sys

[build-img]: https://travis-ci.org/blas-lapack-rs/lapacke.svg?branch=master
[build-url]: https://travis-ci.org/blas-lapack-rs/lapacke
[documentation-img]: https://docs.rs/lapacke/badge.svg
[documentation-url]: https://docs.rs/lapacke
[package-img]: https://img.shields.io/crates/v/lapacke.svg
[package-url]: https://crates.io/crates/lapacke
