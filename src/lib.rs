//! Wrappers for [LAPACKE] \(C).
//!
//! ## [Architecture]
//!
//! ## Example
//!
//! ```no_run
//! use lapacke::*;
//!
//! let n = 3;
//! let mut a = vec![
//!     3.0, 1.0, 1.0,
//!     1.0, 3.0, 1.0,
//!     1.0, 1.0, 3.0,
//! ];
//! let mut w = vec![0.0; n as usize];
//! let info;
//!
//! unsafe {
//!     info = dsyev(Layout::ColumnMajor, b'V', b'U', n, &mut a, n, &mut w);
//! }
//!
//! assert!(info == 0);
//! for (one, another) in w.iter().zip(&[2.0, 2.0, 5.0]) {
//!     assert!((one - another).abs() < 1e-14);
//! }
//! ```
//!
//! [architecture]: https://blas-lapack-rs.github.io/architecture
//! [lapacke]: https://en.wikipedia.org/wiki/LAPACK

extern crate lapacke_sys as ffi;
extern crate libc;
extern crate num_complex as num;

use std::mem::transmute;

use libc::c_char;

/// A complex number with 32-bit parts.
#[allow(non_camel_case_types)]
pub type c32 = num::Complex<f32>;

/// A complex number with 64-bit parts.
#[allow(non_camel_case_types)]
pub type c64 = num::Complex<f64>;

pub type Select2F32 = Option<extern "C" fn(*const f32, *const f32) -> i32>;
pub type Select3F32 = Option<extern "C" fn(*const f32, *const f32, *const f32) -> i32>;

pub type Select2F64 = Option<extern "C" fn(*const f64, *const f64) -> i32>;
pub type Select3F64 = Option<extern "C" fn(*const f64, *const f64, *const f64) -> i32>;

pub type Select1C32 = Option<extern "C" fn(*const c32) -> i32>;
pub type Select2C32 = Option<extern "C" fn(*const c32, *const c32) -> i32>;

pub type Select1C64 = Option<extern "C" fn(*const c64) -> i32>;
pub type Select2C64 = Option<extern "C" fn(*const c64, *const c64) -> i32>;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
#[repr(C)]
pub enum Error {
    None = 0,
    WorkMemory = -1010,
    TransposeMemory = -1011,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
#[repr(C)]
pub enum Layout {
    RowMajor = 101,
    ColumnMajor = 102,
}

impl PartialEq<i32> for Error {
    #[inline(always)]
    fn eq(&self, other: &i32) -> bool {
        i32::from(*self) == *other
    }
}

impl PartialEq<Error> for i32 {
    #[inline(always)]
    fn eq(&self, other: &Error) -> bool {
        other == self
    }
}

macro_rules! convert {
    ($($from:ident => $into:ident,)*) => (
        $(impl From<$from> for $into {
            #[inline(always)]
            fn from(value: $from) -> $into {
                unsafe { ::std::mem::transmute(value) }
            }
        })*
    );
}

convert! {
    Error => i32,
    Layout => i32,
}

include!("lapacke-sys.rs");
