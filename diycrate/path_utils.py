import os
import time
import traceback
from functools import partial

from boxsdk.exception import BoxAPIException

from diycrate.file_operations import wm, mask
from diycrate.item_queue_io import download_queue, upload_queue
from diycrate.cache_utils import redis_key, r_c


def walk_and_notify_and_download_tree(path, box_folder, client):
    """
    Walk the path recursively and add watcher and create the path.
    :param path:
    :param box_folder:
    :param client:
    :return:
    """
    if os.path.isdir(path):
        wm.add_watch(path, mask, rec=True, auto_add=True)
        local_files = os.listdir(path)
    b_folder = client.folder(folder_id=box_folder['id']).get()
    num_entries_in_folder = b_folder['item_collection']['total_count']
    limit = 100
    for offset in range(0, num_entries_in_folder, limit):
        for box_item in b_folder.get_items(limit=limit, offset=offset):
            if box_item['name'] in local_files:
                local_files.remove(box_item['name'])
    for local_file in local_files:  # prioritize the local_files not yet on box's server.
        cur_box_folder = b_folder
        local_path = os.path.join(path, local_file)
        if os.path.isfile(local_path):
            upload_queue.put([os.path.getmtime(local_path), partial(cur_box_folder.upload, local_path, local_file),
                              client._oauth])
    for offset in range(0, num_entries_in_folder, limit):
        for box_item in b_folder.get_items(limit=limit, offset=offset):
            if box_item['name'] in local_files:
                local_files.remove(box_item['name'])
            if box_item['type'] == 'folder':
                local_path = os.path.join(path, box_item['name'])
                if not os.path.isdir(local_path):
                    os.mkdir(local_path)
                try:
                    walk_and_notify_and_download_tree(local_path,
                                                      client.folder(folder_id=box_item['id']).get(), client)
                except BoxAPIException as e:
                    print(traceback.format_exc())
                    if e.status == 404:
                        print('Box says: {}, {}, is a 404 status.'.format(box_item['id'], box_item['name']))
                        print('But, this is a folder, we do not handle recursive folder deletes correctly yet.')
            else:
                try:
                    file_obj = box_item
                    download_queue.put((file_obj, os.path.join(path, box_item['name']), client._oauth))
                except BoxAPIException as e:
                    print(traceback.format_exc())
                    if e.status == 404:
                        print('Box says: {}, {}, is a 404 status.'.format(box_item['id'], box_item['name']))
                        if r_c.exists(redis_key(box_item['id'])):
                            print('Deleting {}, {}'.format(box_item['id'], box_item['name']))
                            r_c.delete(redis_key(box_item['id']))


def re_walk(path, box_folder, client):
    """

    :param path:
    :param box_folder:
    :param client:
    :return:
    """
    while True:
        walk_and_notify_and_download_tree(path, box_folder, client)
        time.sleep(3600)  # once an hour we walk the tree