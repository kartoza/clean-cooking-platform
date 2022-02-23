from django.core.cache import cache


def get_cache_dataset(dataset_key):
    """
    Check if key is in list of dataset keys
    if exist then return the cached dataset
    :param dataset_key: key to check
    """
    dataset_keys_cache = cache.get('dataset_keys')
    dataset = None

    if not dataset_keys_cache:
        cache.set('dataset_keys', [dataset_key])
    else:
        dataset = cache.get(dataset_key)
        if not dataset:
            if dataset_key in dataset_keys_cache:
                dataset_keys_cache.remove(dataset_key)
                cache.set('dataset_keys', dataset_keys_cache)

    return dataset


def set_cache_dataset(dataset_key, dataset):
    """
    Store dataset to cache with key, also store key in the dataset_keys
    :param dataset_key: key for the dataset
    :param dataset: dataset object
    """
    dataset_keys_cache = cache.get('dataset_keys')

    if dataset_keys_cache:
        if dataset_key not in dataset_keys_cache:
            dataset_keys_cache.append(dataset_key)
            cache.set('dataset_keys', dataset_keys_cache)

    cache.set(dataset_key, dataset)

    return dataset


def delete_all_dataset_cache():
    """
    Delete all dataset cache
    """
    dataset_keys_cache = cache.get('dataset_keys')

    if dataset_keys_cache:
        cache.delete_many(dataset_keys_cache)
        cache.delete('dataset_keys')


def delete_all_vector_point_cache():
    keys = cache.get('vector_keys')

    if keys:
        cache.delete_many(keys)
        cache.delete('vector_keys')

def delete_vector_point_cache(vector_id):
    keys = cache.get('vector_keys')
    if keys and vector_id in keys:
        keys.remove(vector_id)
        cache.set('vector_keys', keys)

    cache.delete(vector_id)

def set_cache_vector_points(vector_id, data):
    keys = cache.get('vector_keys')
    if keys:
        if vector_id not in keys:
            keys.append(vector_id)
            cache.set('vector_keys', keys)
    else:
        cache.set('vector_keys', [vector_id])
    cache.set(vector_id, data)


def get_cache_vector_points(vector_id):
    keys = cache.get('vector_keys')
    dataset = None

    if not keys:
        cache.set('vector_keys', [vector_id])
    else:
        dataset = cache.get(vector_id)
        if not dataset:
            if vector_id in keys:
                keys.remove(vector_id)
                cache.set('vector_keys', keys)

    return dataset
