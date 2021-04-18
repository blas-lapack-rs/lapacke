#!/usr/bin/env python

import argparse
import os
import re

from function import Function
from function import read

select_re = re.compile('LAPACK_(\w)_SELECT(\d)')


def is_scalar(name, cty, f):
    return ( \
        'c_char' in cty or
        name in [
            'abnrm',
            'abstol',
            'amax',
            'anorm',
            'bbnrm',
            'colcnd',
            'ihi',
            'il',
            'ilo',
            'info',
            'iter',
            'iu',
            'l',
            'liwork',
            'lrwork',
            'lwork',
            'm',
            'mm',
            'n',
            'n_err_bnds',
            'nb',
            'nrhs',
            'rank',
            'rcond',
            'rowcnd',
            'rpvgrw',
            'sdim',
            'tryrac',
            'vu',
        ] or
        name in [
            'alpha',
        ] and (
            'larfg' in f.name
        ) or
        name in [
            'dif',
        ] and not (
            'tgsen' in f.name or
            'tgsna' in f.name
        ) or
        name in [
            'p',
        ] and not (
            'tgevc' in f.name
        ) or
        name in [
            'q'
        ] and (
            'lapack_int' in cty
        ) or
        name in [
            'vl',
            'vr',
        ] and not (
            'geev' in f.name or
            'ggev' in f.name or
            'hsein' in f.name or
            'tgevc' in f.name or
            'tgsna' in f.name or
            'trevc' in f.name or
            'trsna' in f.name
        ) or
        name.startswith('k') and not (
            'lapmr' in f.name or
            'lapmt' in f.name
        ) or
        name.startswith('inc') or
        name.startswith('ld') or
        name.startswith('tol') or
        name.startswith('vers')
    )


def translate_name(name):
    mapping = {
        'matrix_layout': 'layout',
    }
    return mapping.get(name, name)


def translate_base_type(cty):
    if 'c_char' in cty:
        return 'u8'
    elif 'c_float' in cty:
        return 'f32'
    elif 'c_double' in cty:
        return 'f64'
    elif 'lapack_int' in cty:
        return 'i32'
    elif 'lapack_logical' in cty:
        return 'i32'
    elif 'lapack_complex_float' in cty:
        return 'c32'
    elif 'lapack_complex_double' in cty:
        return 'c64'

    assert False, 'cannot translate `{}`'.format(cty)


def translate_signature_type(name, cty, f):
    if name == 'layout':
        return 'Layout'

    m = select_re.match(cty)
    if m is not None:
        if m.group(1) == 'S':
            return 'Select{}F32'.format(m.group(2))
        elif m.group(1) == 'D':
            return 'Select{}F64'.format(m.group(2))
        elif m.group(1) == 'C':
            return 'Select{}C32'.format(m.group(2))
        elif m.group(1) == 'Z':
            return 'Select{}C64'.format(m.group(2))

    base = translate_base_type(cty)
    if '*const' in cty:
        if is_scalar(name, cty, f):
            return base
        else:
            return '&[{}]'.format(base)
    elif '*mut' in cty:
        if is_scalar(name, cty, f):
            return '&mut {}'.format(base)
        else:
            return '&mut [{}]'.format(base)

    return base


def translate_body_argument(name, rty):
    if rty == 'Layout':
        return '{}.into()'.format(name)

    if rty.startswith('Select'):
        return 'transmute({})'.format(name)

    if rty == 'u8':
        return '{} as c_char'.format(name)
    elif rty == '&mut u8':
        return '{} as *mut _ as *mut _'.format(name)

    elif rty == 'i32':
        return name
    elif rty == '&mut i32':
        return name
    elif rty == '&[i32]':
        return '{}.as_ptr()'.format(name)
    elif rty == '&mut [i32]':
        return '{}.as_mut_ptr()'.format(name)

    elif rty.startswith('f'):
        return name
    elif rty.startswith('&mut f'):
        return name
    elif rty.startswith('&[f'):
        return '{}.as_ptr()'.format(name)
    elif rty.startswith('&mut [f'):
        return '{}.as_mut_ptr()'.format(name)

    elif rty.startswith('c'):
        return 'transmute({})'.format(name)
    elif rty.startswith('&mut c'):
        return '{} as *mut _ as *mut _'.format(name)
    elif rty.startswith('&[c'):
        return '{}.as_ptr() as *const _'.format(name)
    elif rty.startswith('&mut [c'):
        return '{}.as_mut_ptr() as *mut _'.format(name)

    assert False, 'cannot translate `{}: {}`'.format(name, rty)


def format_signature(f):
    args = format_signature_arguments(f)
    if f.ret is None:
        return 'pub unsafe fn {}({})'.format(f.name, args)
    else:
        return 'pub unsafe fn {}({}) -> {}'.format(f.name, args,
                                                   translate_base_type(f.ret))


def format_signature_arguments(f):
    s = []
    for name, cty in f.args:
        name = translate_name(name)
        s.append('{}: {}'.format(name, translate_signature_type(name, cty, f)))
    return ', '.join(s)


def format_body(f):
    return 'ffi::LAPACKE_{}({})'.format(f.name, format_body_arguments(f))


def format_body_arguments(f):
    s = []
    for name, cty in f.args:
        name = translate_name(name)
        rty = translate_signature_type(name, cty, f)
        s.append(translate_body_argument(name, rty))
    return ', '.join(s)


def process(code):
    lines = filter(lambda line: not re.match(r'^\s*//.*', line),
                   code.split('\n'))
    lines = re.sub(r'\s+', ' ', ''.join(lines)).strip().split(';')
    lines = filter(lambda line: not re.match(r'^\s*$', line), lines)
    return [Function.parse(line) for line in lines]


def write(functions):
    for f in functions:
        print('\n#[inline]')
        print(format_signature(f) + ' {')
        print('    ' + format_body(f) + '\n}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sys', default='lapacke-sys')
    arguments = parser.parse_args()
    path = os.path.join(arguments.sys, 'src', 'lib.rs')
    write(process(read(path)))
