# -*- coding:utf-8 -*-
# Author: hankcs
# Date: 2019-12-31 19:24
import os
import traceback

from hanlp import pretrained
from hanlp.common.component import Component
from hanlp.utils.io_util import get_resource, load_json, eprint
from hanlp.utils.reflection import object_from_class_path, str_to_type
from hanlp import version


def load_from_meta_file(save_dir, meta_filename='meta.json', **kwargs) -> Component:
    identifier = save_dir
    load_path = save_dir
    save_dir = get_resource(save_dir)
    metapath = os.path.join(save_dir, meta_filename)
    if not os.path.isfile(metapath):
        tips = ''
        if save_dir.isupper():
            from difflib import SequenceMatcher
            similar_keys = sorted(pretrained.ALL.keys(),
                                  key=lambda k: SequenceMatcher(None, save_dir, metapath).ratio(),
                                  reverse=True)[:5]
            tips = f'Check its spelling based on the available keys:\n' + \
                   f'{sorted(pretrained.ALL.keys())}\n' + \
                   f'Tips: it might be one of {similar_keys}'
        raise FileNotFoundError(f'The identifier {save_dir} resolves to a non-exist meta file {metapath}. {tips}')
    meta: dict = load_json(metapath)
    cls = meta.get('class_path', None)
    assert cls, f'{meta_filename} doesn\'t contain class_path field'
    try:
        obj: Component = object_from_class_path(cls, **kwargs)
        if hasattr(obj, 'load') and os.path.isfile(os.path.join(save_dir, 'config.json')):
            obj.load(save_dir)
            obj.meta['load_path'] = load_path
        return obj
    except Exception as e:
        eprint(f'Failed to load {identifier}. See stack trace below')
        traceback.print_exc()
        old_version = meta.get("hanlp_version", "unknown")
        cur_version = version.__version__
        if old_version != cur_version:
            eprint(
                f'{identifier} was created with hanlp-{old_version}, but you are running {cur_version}. Try to upgrade hanlp with\n'
                f'pip install --upgrade hanlp')
        exit(1)


def load_from_meta(meta: dict) -> Component:
    cls = meta.get('class_path', None)
    assert cls, f'{meta} doesn\'t contain class_path field'
    cls = str_to_type(cls)
    return cls.from_meta(meta)
