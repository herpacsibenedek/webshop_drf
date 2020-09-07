import random
import string


def random_string_generator(size=10, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_random_string_generator(instance, size):
    """
    Creates a unique random string with a given size
    It assumes your instance has a slug field.
    """
    slug = random_string_generator(size)
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        return unique_random_string_generator(instance, size)
    return slug


def router_extend(base_router, extend_router, name):
    """
    Modifies base_router' registry by adding a name
    with a registry information of an extend_router
    """
    for registry in extend_router.registry:
        # (prefix, viewset, basename)
        r = list(registry)
        r[0] = f"{name}/{registry[0]}"
        # registry accepts a list of tuples
        base_router.registry.extend([tuple(r)])

    return base_router
