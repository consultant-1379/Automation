import behave


def after_step(context, step):
    if step.name == 'I start the Scenario of polling the state of network service using service ID for deployed node':
        context.execute_steps("Then I start the Scenario of checking LCM workflow")
    elif step.name == 'I start the Scenario of checking LCM workflow':
        context.execute_steps("Then I start the Scenario of checking ECM order status")


def after_scenario(context, scenario):
    if scenario.status == 'failed':
        context.feature.skip()
