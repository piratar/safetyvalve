icepet
======

after installing, make sure to run:

    cd icepet
    pip install -r requirements.txt

then:

    cd icepet (yes, again)
    python manage.py syncdb (if you haven't already done so)
    python manage.py collectstatic (optional in dev)
    python manage.py updatealthingi (will poll for frumvarp)
    python manage.py runserver (to run a dev server)
