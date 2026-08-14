import numpy as np
import os

def search_index(bench_mark, a):
    x = np.asanyarray(bench_mark)
    y = np.asanyarray(a)
    index = np.argsort(x)
    sorted_x = x[index]
    sorted_index = np.searchsorted(sorted_x, y)
    y_index = np.take(index, sorted_index, mode="clip")
    mask = x[y_index] != y
    result = np.ma.array(y_index, mask=mask, fill_value=0)
    return result


def forward_fill(arr, axis=0, zero_fill=False):
    arr = arr.swapaxes(axis, -1)
    if zero_fill:
        mask = arr == 0
    else:
        mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[-1]), 0)
    np.maximum.accumulate(idx, axis=-1, out=idx)
    out = arr[tuple(np.arange(idx.shape[x])[(None,) * x + (slice(None),) + (None,) * (idx.ndim - x - 1)]
                    for x in range(idx.ndim - 1)) + (idx,)]
    out = out.swapaxes(axis, -1)
    return out


def get_numpy_head(shape, dtype='float32'):
    head = [
        147, 78, 85, 77, 80, 89, 1, 0, 118, 0, 123, 39, 100, 101, 115, 99, 114, 39, 58, 32,
        39, 60, 102, 56, 39, 44, 32, 39, 102, 111, 114, 116, 114, 97, 110, 95, 111, 114, 100, 101,
        114, 39, 58, 32, 70, 97, 108, 115, 101, 44, 32, 39, 115, 104, 97, 112, 101, 39, 58, 32,
        40, 41, 44, 32, 125, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 10
    ]
    dtype_dict = {
        'bool': [124, 98, 49],
        'int8': [124, 105, 49],
        'int16': [60, 105, 50],
        'int32': [60, 105, 52],
        'int64': [60, 105, 56],
        'float32': [60, 102, 52],
        'float64': [60, 102, 56]
    }
    shape_map = {
        '0': 48,
        '1': 49,
        '2': 50,
        '3': 51,
        '4': 52,
        '5': 53,
        '6': 54,
        '7': 55,
        '8': 56,
        '9': 57,
        ',': 44,
        ' ': 32
    }
    shape_value = [shape_map[x] for x in str(shape)[1: -1]] + [41, 44, 32, 125]
    head[21: 24] = dtype_dict[dtype]
    head[61: 61 + len(shape_value)] = shape_value
    return head


def store_augmented_matrix(arr, file, axis=2, length=6000, offset_days=0):
    amend_shape = list(arr.shape)
    amend_shape[axis] = length
    total_shape = amend_shape.copy()
    total_shape[0] += offset_days
    amend_shape = tuple(amend_shape)
    total_shape = tuple(total_shape)
    head = get_numpy_head(total_shape, arr.dtype.name)
    if not os.path.exists(file):
        fp = np.memmap(file, dtype='uint8', mode='w+', offset=0, shape=128)
        fp[:] = head
        del fp
    else:
        fp = np.memmap(file, dtype='uint8', mode='r+', offset=0, shape=128)
        fp[:] = head
        del fp
    offset = 128 + offset_days * arr[0].nbytes // arr.shape[axis] * length
    fp = np.memmap(file, dtype=arr.dtype.name, mode='r+', offset=offset, shape=amend_shape)
    fp[tuple([slice(None)] * axis + [slice(None, arr.shape[axis])] + [
        slice(None)] * (arr.ndim - axis - 1))] = arr
    if 'float' in arr.dtype.name:
        fp[tuple([slice(None)] * axis + [slice(arr.shape[axis], None)] + [
            slice(None)] * (arr.ndim - axis - 1))] = np.nan
    elif 'bool' in arr.dtype.name:
        fp[tuple([slice(None)] * axis + [slice(arr.shape[axis], None)] + [
            slice(None)] * (arr.ndim - axis - 1))] = False
    else:
        raise TypeError("Unsupported type like int32.")
    del fp