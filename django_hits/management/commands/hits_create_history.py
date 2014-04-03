from django.core.management.base import BaseCommand
from optparse import make_option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-b', '--bucket', action='store', dest='bucket',
                    help='Select desired buckets to create history for (by default no bucket will be created)'),
        make_option('-a', '--all-buckets', action='store_true', dest='all_buckets',
                    help='Create history for all buckets'),
    )
    help = ''
    args = ''

    def handle(self, *filenames, **options):
        from ...models import Hit
        from ...utils import create_hit_history

        queryset = Hit.objects.all()
        if not options['all_buckets']:
            if options['bucket'] is None:
                queryset = queryset.filter(bucket__isnull=True)
            else:
                queryset = queryset.filter(bucket=options['bucket'])
        for hit in queryset:
            create_hit_history(hit)
