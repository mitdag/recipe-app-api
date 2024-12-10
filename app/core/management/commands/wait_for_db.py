from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2OpsError
import time


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Checking if the db is up ...")
        db_up = False
        while not db_up:
            try:
                self.check(databases=["default"])
                db_up = True
            except (OperationalError, Psycopg2OpsError):
                self.stdout.write("\tNot yet ...")
                time.sleep(1)

        self.stdout.write("Now db is ready!")
