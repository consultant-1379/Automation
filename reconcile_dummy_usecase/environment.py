import behave

flag = False

def after_scenario(context, scenario):
    if scenario.status == 'failed':
        context.feature.skip()



def before_feature(context,feature):
    print('before feature '+feature.name)
    print(feature.status)
    if flag:
        feature.skip()


def after_feature(context ,feature):
    print('after feature' + str(feature.status))
    if feature.status == 'failed':
        global flag
        flag = True		

		