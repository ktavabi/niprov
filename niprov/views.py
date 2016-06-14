from pyramid.view import view_config
import os


@view_config(route_name='home', renderer='templates/home.mako')
def home(request):
    return {}

@view_config(route_name='latest', renderer='templates/list.mako')
def latest(request):
    repository = request.dependencies.getRepository()
    return {'images':repository.latest()}



@view_config(route_name='short', renderer='templates/single.mako')
def short(request):
    sid = request.matchdict['id']
    repository = request.dependencies.getRepository()
    return {'image':repository.byId(sid)}

@view_config(route_name='location', renderer='templates/single.mako')
def location(request):
    path = os.sep + os.path.join(*request.matchdict['path'])
    loc = request.matchdict['host'] + ':' + path
    repository = request.dependencies.getRepository()
    return {'image':repository.byLocation(loc)}

@view_config(route_name='stats', renderer='templates/stats.mako')
def stats(request):
    repository = request.dependencies.getRepository()
    return {'stats':repository.statistics()}

@view_config(route_name='pipeline', renderer='templates/pipeline.mako')
def pipeline(request):
    sid = request.matchdict['id']
    files = request.dependencies.getRepository()
    pipeline = request.dependencies.getPipelineFactory()
    return {'pipeline':pipeline.forFile(files.byId(sid)), 'sid':sid}

@view_config(route_name='subject', renderer='templates/list.mako')
def subject(request):
    subj = request.matchdict['subject']
    query = request.dependencies.getQuery()
    return {'images':query.bySubject(subj)}

@view_config(route_name='project', renderer='templates/list.mako')
def project(request):
    project = request.matchdict['project']
    query = request.dependencies.getQuery()
    return {'images':query.byProject(project)}

@view_config(route_name='user', renderer='templates/list.mako')
def user(request):
    user = request.matchdict['user']
    query = request.dependencies.getQuery()
    return {'images':query.byUser(user)}

@view_config(route_name='modality', renderer='templates/list.mako')
def modality(request):
    modality = request.matchdict['modality']
    query = request.dependencies.getQuery()
    return {'images':query.byModality(modality)}


