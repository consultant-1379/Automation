import behave



check = False

def after_step(context, step):
    print (step.status)
    
    if step.name =='I start the Scenario of checking LCM workflow':
        context.execute_steps("Then I start the Scenario of checking ECM order status")
    elif step.name == 'I start the Scenario of checking ECM order status' or step.name == 'I start the Scenario of checking sync status of node in ENM':
        context.execute_steps("Then I start the Scenario of pinging the deployed Node")
    elif step.name =='I start the Scenario of pinging the deployed Node':
        if check :
            context.execute_steps("Then I start the Scenario of checking bulk configuration")




def after_scenario(context, scenario):
    if scenario.status == 'failed':
        context.feature.skip()



