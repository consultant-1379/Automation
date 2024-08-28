import sys
import os
from behave import __main__ as runner_with_options
import start_script

if __name__ == '__main__':
    sys.stdout.flush()
    print(os.getcwd())
    start_script.start_execution('EPIS','do_init.json')
    first = ' -f allure_behave.formatter:AllureFormatter -o features '
    feature_file_path = 'features/step_parameters_parse.feature'
    options = ' --no-capture --no-capture-stderr -f plain'
    full_runner_options = first + feature_file_path + options
    runner_with_options.main(full_runner_options)