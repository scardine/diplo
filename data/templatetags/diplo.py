from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_pandas.io import read_frame
from unidecode import unidecode
import locale
locale.setlocale(locale.LC_NUMERIC, '')

register = template.Library()


def convert(v):
    try:
        return float(v)
    except ValueError:
        return v


def convert_serie(s):
    return [convert(_) for _ in s]


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


@register.simple_tag(takes_context=True)
def render_panel(context, painel):
    return mark_safe(painel.modelo.render(context))


@register.filter
def get_data(self, regionalizacao='munic'):
    return read_frame(self.dado_set.filter(localidade__tipo=regionalizacao))\
        .pivot(index='localidade', columns='ano', values='valor')


@register.filter
def order_df(df, ordem='localidade'):
    if ordem[0] == '-':
        ordem = ordem[1:]
        ascending = False
    else:
        ascending = True

    if ordem == 'localidade':
        df['_'] = df.index.map(unidecode)
    else:
        df['_'] = df[int(ordem)].map(convert)
    return df.sort_values('_', ascending=ascending).drop(labels=['_'], axis=1)


@register.filter
def to_html(df, format=''):
    if format:
        def f(v):
            try:
                return locale.format_string(format, float(v), grouping=True)
            except (ValueError, TypeError) as e:
                return v
        formatters = [f] * len(df.columns)
        return df.to_html(classes=['table', 'table-striped'], formatters=formatters).replace('border="1"', '')
    return df.to_html(classes=['table', 'table-striped'], decimal=',').replace('border="1"', '')


@register.filter
def to_json(df):
    return df.to_json()


@register.simple_tag(takes_context=True)
def static_page_link(context, url, label):
    if url.endswith('$'):
        url = url[:-1]
        active = context['request'].path == url
    else:
        active = context['request'].path.startswith(url)
    context = context.flatten()
    context['url'] = url
    context['label'] = label
    context['active'] = active
    return mark_safe(render_to_string('static-page-link.html', context=context))
