
from django.core.context_processors import csrf
from django.shortcuts import HttpResponseRedirect, render_to_response


def test_auth(request):
    c = {}
#    c.update(csrf(request))

    if request.method == 'POST':

        c['result'] = 'success'
        c['token'] = 'TestToken123'

        ret_url = request.GET.get('next')
        return HttpResponseRedirect(ret_url)

    return render_to_response('person/test_auth.html', c)
