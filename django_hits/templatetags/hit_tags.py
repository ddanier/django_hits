from django import template
from django_hits.models import Hit

register = template.Library()


class HitNode(template.Node):
    def __init__(self, context_var_name, as_var_name, bucket_var_name, count, count_bucket_only=False):
        self.context_var_name = context_var_name
        self.as_var_name = as_var_name
        self.bucket_var_name = bucket_var_name
        self.count = count
        self.count_bucket_only = count_bucket_only

    def _handle_hit(self, context, obj, bucket, count, user, ip):
        was_counted = False
        hit_cache_key = (obj, bucket)
        if hit_cache_key in context._hit_cache_:
            hit, was_counted = context._hit_cache_[hit_cache_key]
        else:
            hit = Hit.objects.get_for(obj, bucket=bucket)
        if count and not was_counted:
            was_counted = hit.hit(user, ip)
        context._hit_cache_[hit_cache_key] = (hit, was_counted)
        return hit


    def render(self, context):
        if not hasattr(context, '_hit_cache_'):
            context._hit_cache_ = {}
        bucket = None
        try:
            obj = self.context_var_name.resolve(context)
            if self.bucket_var_name:
                bucket = self.bucket_var_name.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        try:
            user = template.Variable('user').resolve(context)
            if user.is_anonymous():
                user = None
        except template.VariableDoesNotExist:
            user = None
        count = self.count
        ip = None
        if count:
            try:
                request = template.Variable('request').resolve(context)
                if 'REMOTE_ADDR' in request.META:
                    ip = request.META['REMOTE_ADDR']
            except template.VariableDoesNotExist:
                pass
        hit = self._handle_hit(context, obj, bucket, count, user, ip)
        if not bucket is None:
            if not self.count_bucket_only:  # we count a global hit, too
                self._handle_hit(context, obj, None, count, user, ip)
        if self.as_var_name:
            context[self.as_var_name] = hit
        return ''


@register.tag
def get_hit(parser, token):
    '''
    {% get_hit for obj as hit %}
    {% get_hit for "static_page" as hit %}
    {% get_hit for obj bucket "foo" as hit %}
    {% get_hit for "static_page" bucket "foo" as hit %}
    '''
    tokens = token.split_contents()
    tag_name = tokens.pop(0)
    if not len(tokens) in (2, 4, 6,):
        raise template.TemplateSyntaxError, "%r tag requires 2, 4 or 6 arguments" % tag_name
    i = 0
    context_var_name = None
    as_var_name = None
    bucket_var_name = None
    while i < len(tokens):
        instruction = tokens[i]
        value = tokens[i + 1]
        if instruction == 'for':
            context_var_name = parser.compile_filter(value)
        elif instruction == 'as':
            as_var_name = value
        elif instruction == 'bucket':
            bucket_var_name = parser.compile_filter(value)
        else:
            raise template.TemplateSyntaxError, "Invalid instruction for %s tag ('%s')" % (tag_name, instruction)
        i += 2
    if context_var_name is None:
        raise template.TemplateSyntaxError, "%s tag requires some object to get hits for ('for')" % tag_name
    if as_var_name is None:
        raise template.TemplateSyntaxError, "%s tag requires some context name to write hit into ('as')" % tag_name
    return HitNode(context_var_name, as_var_name, bucket_var_name, False)

@register.tag
def count_hit(parser, token):
    '''
    {% count_hit for obj %}
    {% count_hit for obj as hit %}
    {% count_hit for "static_page" %}
    {% count_hit for "static_page" as hit %}
    {% count_hit for obj bucket "foo" %}
    {% count_hit for obj bucket "foo" as hit %}
    {% count_hit for "static_page" bucket "foo" %}
    {% count_hit for "static_page" bucket "foo" as hit %}
    {% count_hit for obj bucket "foo" only %}
    {% count_hit for obj bucket "foo" only as hit %}
    {% count_hit for "static_page" bucket "foo" only %}
    {% count_hit for "static_page" bucket "foo" only as hit %}
    '''
    tokens = token.split_contents()
    tag_name = tokens.pop(0)
    i = 0
    context_var_name = None
    as_var_name = None
    bucket_var_name = None
    count_bucket_only = False
    while i < len(tokens):
        try:
            instruction = tokens[i]
            value = tokens[i + 1]
        except IndexError:
            raise template.TemplateSyntaxError, "Invalid usage of %s tag" % tag_name
        if instruction == 'for':
            context_var_name = parser.compile_filter(value)
        elif instruction == 'as':
            as_var_name = value
        elif instruction == 'bucket':
            bucket_var_name = parser.compile_filter(value)
            try:
                _only = tokens[i + 2]
                if _only == 'only':
                    count_bucket_only = True
                    i += 1  # we have to eat one more token
            except IndexError:
                pass  # no problem, only is optional
        else:
            raise template.TemplateSyntaxError, "Invalid instruction for %s tag ('%s')" % (tag_name, instruction)
        i += 2
    if context_var_name is None:
        raise template.TemplateSyntaxError, "%s tag requires some object to count hits for ('for')" % tag_name
    return HitNode(context_var_name, as_var_name, bucket_var_name, True, count_bucket_only)

