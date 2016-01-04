Öryggisventill (Safety Valve)
======

*nix system requirements:

    libmysqlclient-dev (if intending to use mysql as a db, which is reccomended)
    python-dev
    libxml2-dev
    libxslt-dev
    gettext
    ---
    sudo apt-get install libmysqlclient-dev python-dev libxml2-dev libxslt-dev gettext (on a debian/ubuntu based flavor)

after cloning, make sure to run:

    cd safetyvalve
    pip install distribute==0.7.3
    pip install -r requirements.txt

NB: If you intend to use different backend than MySQL, you don't need the mysql-python lib listed in the requirements.txt.

then:

    cd safetyvalve (yes, again)
    cp safetyvalve/local_settings.py{-example,}
    # Edit the safetyvalve/local_settings.py to set database info and config your local instance
    # e.g. vim safetyvalve/local_settings.py
    python manage.py makemigrations petition althingi person
    python manage.py migrate
    python manage.py collectstatic (optional in dev)
    python manage.py updatealthingi (will poll for frumvarp)
    python manage.py runserver (to run a dev server)

Translating
------
At the project's root directory (where 'manage.py' recides), run the following

    django-admin makemessages -l is # (or some other code instead of 'is')

This will update the translation source file at: locale/is/LC_MESSAGES/django.po
Edit the file and translate the strings. Then run:

    django-admin compilemessages

This will compile the translation file into the target file at: locale/is/LC_MESSAGES/django.mo

Then the server will need restarting to take the changes into account.

