from django import template

register = template.Library()


@register.filter
def compacta(periodo):
    periodos = list(sorted(int(_) for _ in periodo.split(',')))
    if not periodos:
        return
    if len(periodos) == 1:
        return periodo
    sequencias = []
    anterior = periodos.pop(0)
    sequencia = [anterior, anterior]
    for periodo in periodos:
        if anterior + 1 == periodo:
            sequencia[-1] = periodo
            anterior = periodo
            continue
        sequencias.append(sequencia)
        sequencia = [periodo, periodo]
        anterior = periodo
    if not sequencias or sequencia != sequencias[-1]:
        sequencias.append(sequencia)
    return ', '.join(['{}-{}'.format(a, b) if a != b else '{}'.format(a) for a, b in sequencias])


@register.filter
def chunks(iterable, chunk_size):
    if not hasattr(iterable, '__iter__'):
        # can't use "return" and "yield" in the same function
        yield iterable
    else:
        i = 0
        chunk = []
        for item in iterable:
            chunk.append(item)
            i += 1
            if not i % chunk_size:
                yield chunk
                chunk = []
        if chunk:
            # some items will remain which haven't been yielded yet,
            # unless len(iterable) is divisible by chunk_size
            yield chunk
