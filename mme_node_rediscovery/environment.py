import behave



def after_scenario(context, scenario):
    if scenario.status == 'failed':
        context.feature.skip()
