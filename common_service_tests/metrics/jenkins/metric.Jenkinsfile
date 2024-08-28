#!/usr/bin/env groovy
/* IMPORTANT:
 *
 * In order to make this pipeline work, the following configuration on Jenkins is required:
 * - slave with a specific label (see pipeline.agent.label below)
 */

def bob = new BobCommand().toString()

pipeline {
    agent {
        label 'evo_docker_engine'
    }
    parameters {
        string(name: 'VALUE_PACK', defaultValue: 'eo', description: 'pick which product we want to test, eg vnfm')
        string(name: 'HOST_URL', defaultValue: 'http://prometheus.p6-opstk-4a-de-cni-ecfe-8.athtem.eei.ericsson.se', description: 'URL where EO Chart is installed')

    }
    stages {
        stage('Clean Workspace') {
            steps {
                sh "${bob} clean-workspace"
            }
        }

        stage('set up the test') {
            steps {
                script {
                    //TODO(eforaar) will move the code to bob python image
//                   sh "${bob} metric-test-setup"
                sh "python -m pip install --user -r ./common_service_tests/metrics/requirements.txt"
                }
            }
        }
        stage('Test Metrics ') {
            steps {
                script {
                    //TODO(eforaar) will move the code to bob python image
//                    def bobWithParams = new BobCommand()
//                            .envVars([
//                                    'HOST_URL'        : params.HOST_URL,
//                                    'VALUE_PACK'      : params.VALUE_PACK,
//                            ])
//                            .toString()
//                    sh "${bobWithParams} metric-test-run"

                    sh "python -m pytest  --rootdir=common_service_tests/metrics/   common_service_tests/metrics/tests/pm-server.py --url ${HOST_URL} -m ${VALUE_PACK}"
                }

            }
        }
    }
}

// More about @Builder: http://mrhaki.blogspot.com/2014/05/groovy-goodness-use-builder-ast.html
import groovy.transform.builder.Builder
import groovy.transform.builder.SimpleStrategy

@Builder(builderStrategy = SimpleStrategy, prefix = '')
class BobCommand {
    def bobImage = 'armdocker.rnd.ericsson.se/sandbox/adp-staging/adp-cicd/bob.2.0:1.7.0-20'
    def envVars = [:]
    def needDockerSocket = true
    def rulesetPath = '\${WORKSPACE}/ruleset/ruleset2.0.yaml'

    String toString() {
        def env = envVars
                .collect({ entry -> "-e ${entry.key}=\"${entry.value}\"" })
                .join(' ')
        def cmd = """\
            |docker run
            |--init
            |--rm
            |--workdir \${PWD}
            |--user \$(set +x; id -u):\$(set +x; id -g)
            |-v \${PWD}:\${PWD}
            |-v /etc/group:/etc/group:ro
            |-v /etc/passwd:/etc/passwd:ro
            |-v \${HOME}/.docker:\${HOME}/.docker
            |${needDockerSocket ? '-v /var/run/docker.sock:/var/run/docker.sock' : ''}
            |${env}
            |\$(set +x; for group in \$(id -G); do printf ' --group-add %s' "\$group"; done)
            |${bobImage}
            |-r ${rulesetPath}
            |"""
        return cmd
                .stripMargin()           // remove indentation
                .replace('\n', ' ')      // join lines
                .replaceAll(/[ ]+/, ' ') // replace multiple spaces by one
    }
}
