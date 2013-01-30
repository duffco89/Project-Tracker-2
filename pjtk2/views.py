from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.context_processors import csrf

from pjtk2.models import Milestone
#from pjtk2.forms import MilestoneForm
from pjtk2.forms import AdditionalReportsForm, CoreReportsForm


def ReportMilestones(request):
    #reports = MilestoneForm()
    core =  CoreReportsForm()
    additional = AdditionalReportsForm()

    return render_to_response('simpleform.html',
                              {'core':core, 'additional':additional},
                              context_instance=RequestContext(request)
        )
