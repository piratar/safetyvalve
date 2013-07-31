Öryggisventill (Safety Valve)
======

*nix system requirements:

    libmysqlclient-dev (if intending to use mysql as a db, which is reccomended)
    python-dev
    libxml2-dev
    libxslt-dev
    ---
    sudo apt-get install libmysqlclient-dev python-dev libxml2-dev libxslt-dev (on a debian/ubuntu based flavor)

after cloning, make sure to run:

    cd safetyvalve
    pip install -r requirements.txt

NB: If you intend to use different backend than MySQL, you don't need the mysql-python lib listed in the requirements.txt.

then:

    cd safetyvalve (yes, again)
    cp safetyvalve/local_settings.py{-example,}
    # Edit the safetyvalve/local_settings.py to set database info and config your local instance
    # e.g. vim safetyvalve/local_settings.py
    python manage.py syncdb (if you haven't already done so)
    python manage.py collectstatic (optional in dev)
    python manage.py updatealthingi (will poll for frumvarp)
    python manage.py runserver (to run a dev server)
