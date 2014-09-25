# -*- coding: utf-8 -*-
"""Basic admin manager for Shiva.

Usage:
    shiva-admin user create [<email>]
    shiva-admin user activate <email_or_id>
    shiva-admin user deactivate <email_or_id>
    shiva-admin user delete <email_or_id>
    shiva-admin (-h | --help)

Options:
    -h --help   Show this help message and exit
"""
import getpass
import logging
import sys

from docopt import docopt

from shiva.models import db, User
from shiva.utils import get_logger
from shiva.app import app

log = get_logger()


class UserExistsError(Exception):
    pass


def main():
    arguments = docopt(__doc__)
    ctx = app.test_request_context()
    ctx.push()

    if arguments['user']:
        if arguments['create']:
            create_user(arguments['<email>'], interactive=True)
        elif arguments['activate']:
            activate_user(arguments['<email_or_id>'])
        elif arguments['deactivate']:
            activate_user(arguments['<email_or_id>'])
        elif arguments['delete']:
            delete_user(arguments['<email_or_id>'])

    ctx.pop()


def create_user(email=None, password='', is_active=True, is_admin=None,
                interactive=False):
    """
    User creation function. If the `interactive` flag is set, it will delegate
    the task to the create_user_interactive() function.
    """

    if interactive:
        return create_user_interactive(email, password, is_active, is_admin)

    if not email:
        raise ValueError

    if get_user(email) is not None:
        raise UserExistsError

    if not isinstance(password, basestring):
        raise ValueError

    if password == '':
        is_active = False

    user = mk_user(email, password, is_active, is_admin)

    return user


def create_user_interactive(email=None, password='', is_active=True,
                            is_admin=True):
    """
    This function will interactively prompt for the required information. In
    case of error, instead of throwing exceptions will print human readable
    messages to stderr and exit with code 1.
    """

    if not email:
        email = raw_input('E-mail: ').strip()
        if not email:
            log.error('Error: E-mail cannot be empty.')
            sys.exit(1)

    if get_user(email) is not None:
        log.error('Error: User exists.')
        sys.exit(1)

    if not password:
        password = getpass.getpass()
        if not password:
            is_active = False

        pw_again = getpass.getpass('Again: ')

        if password != pw_again:
            log.error('Error: Password do not match.')
            sys.exit(1)

    if password == '':
        is_active = False
        log.info('Password is empty. User will not be active until a password '
                 'is set.')
    else:
        is_active = confirm('Is active?')

    if is_admin is None:
        is_admin = confirm('Is admin?')

    log.info('\nE-mail: %s\nPassword: %s\nActive: %s\nAdmin:%s\n' % (
        email, '(Empty)' if password == '' else '(Not shown)',
        'Yes' if is_active else 'No', 'Yes' if is_admin else 'No'))

    if not confirm('Are values correct?'):
        log.error('Aborting.')
        sys.exit(1)

    user = mk_user(email, password, is_active, is_admin)

    log.info('User #%s created successfuly.' % user.pk)

    return user


def mk_user(email, password, is_active, is_admin):
    user = User(email=email, password=password, is_active=is_active,
                is_admin=is_admin)

    db.session.add(user)
    db.session.commit()

    return user


def confirm(question):
    answer = raw_input('%s [Y/n]: ' % question).strip().lower()
    if answer not in ('', 'y', 'yes', 'n', 'no'):
        log.error('Error: Invalid value.')
        sys.exit(1)

    return (answer in ('', 'y', 'yes'))


def get_user(email_or_id):
    query = User.query

    try:
        pk = int(email_or_id)
        user = query.get(pk)
    except ValueError:
        email = email_or_id
        user = query.filter_by(email=email).first()
    except:
        user = None

    return user


def activate_user(email_or_id):
    user = get_user(email_or_id)
    user.is_active = True

    log.info('User #%s activated.' % user.pk)


def deactivate_user(email_or_id):
    user = get_user(email_or_id)
    user.is_active = False

    log.info('User #%s deactivated.' % user.pk)


def delete_user(email_or_id):
    user = get_user(email_or_id)

    _pk = user.pk

    db.session.delete(user)
    db.session.commit()

    log.info('User #%s deleted.' % _pk)
