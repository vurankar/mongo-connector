properties([
  parameters([
    string(
      defaultValue: 'default',
      description: "Leaving this value as default means the build job will attempt to use the same branch as the main repo (mongo-connector) and default to master if the branch does not exist",
      name: 'ELASTIC2_DOC_MANAGER_BRANCH',
      trim: true),
  ])
])

podTemplate(
  label: "mongo-connector-build-pod",
  containers: [
    containerTemplate(name: 'jenkins-slave', image: 'jenkins/jnlp-slave:3.10-1', ttyEnabled: true, command: 'cat'),
    containerTemplate(name: 'python-build-container', image: 'python:3.5-jessie', command: 'cat', ttyEnabled: true),
    containerTemplate(name: 'docker', image: 'docker:1.12.6', command: 'cat', ttyEnabled: true),
  ],
  volumes:[
    hostPathVolume(mountPath: '/var/run/docker.sock', hostPath: '/var/run/docker.sock'),
  ]
)
{
  node("mongo-connector-build-pod") {
    container('jenkins-slave') {
      stage('Set build params') {
        def timeStamp = Calendar.getInstance().getTime().format('YYMMddHHmm',TimeZone.getTimeZone('UTC'))
        def imageTag = "${env.BRANCH_NAME}-${timeStamp}"
        env.IMAGE_TAG = imageTag
        currentBuild.displayName = "${env.IMAGE_TAG}"
        currentBuild.description = "Built from branch: ${env.BRANCH_NAME}"
      }
      stage('Clone repository') {
        def mongoConnectorBranch = "${BRANCH_NAME}".trim()
        checkout([
          $class: 'GitSCM',
          branches: [[name: "*/${env.BRANCH_NAME}"]],
          extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: 'mongo-connector']],
          userRemoteConfigs: scm.userRemoteConfigs
        ])

        def subRepoBranchName = getBranchName("${ELASTIC2_DOC_MANAGER_BRANCH}".trim(), mongoConnectorBranch)
        checkout([
          $class: 'GitSCM',
          branches: [[name: "*/${subRepoBranchName}"]],
          doGenerateSubmoduleConfigurations: false,
          extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: 'elastic2-doc-manager']],
          submoduleCfg: [],
          userRemoteConfigs: [[credentialsId: 'github', url: 'https://github.com/RiffynInc/elastic2-doc-manager.git']]
        ])

        // def elastic2DocManagerBranch = "${ELASTIC2_DOC_MANAGER_BRANCH}".trim()
        // dir('elastic2-doc-manager') {
        //   elastic2DocManagerBranch = checkoutBranch(mongoConnectorBranch, "elastic2-doc-manager", elastic2DocManagerBranch)
        // }
      }
    }
    container('python-build-container') {
      stage('Build wheels for mongo-connector and elastic2_doc_manager') {
        dir('mongo-connector'){
          sh 'python setup.py bdist_wheel'
        }
        dir('elastic2-doc-manager'){
          sh 'python setup.py bdist_wheel'
        }
        sh 'tar -zcvf mongo-connector/mongo-elastic.tar mongo-connector/dist/mongo_connector-*.whl elastic2-doc-manager/dist/elastic2_doc_manager-*.whl'
      }
    }
    container('docker') {
      def image
      stage('Build and push container') {
        dir('mongo-connector'){
          def tag = "riffyninc/mongo-connector:${env.IMAGE_TAG}"
          image = docker.build(tag)
          docker.withRegistry('https://registry.hub.docker.com', 'riffynbuild-dockerhub-credentials') {
            image.push()
            image.push("${env.BRANCH_NAME}-latest")
          }
        }
      }
    }
  }
}
def branchExists(branchName) {
  def branchExists = sh(returnStatus: true, script: "git show-branch remotes/origin/${branchName}")
  if (branchExists == 0) {
    return true
  }
  else {
    return false
  }
}

// Determine the subrepo branch name.
// this is a weak method because it does not check if the
// branches actually exist.
def getBranchName(subRepoBranch, mainRepoBranch) {
    // if user specified a branch then use it
      if (subRepoBranch.trim() != "default") {
        return subRepoBranch.trim()
      }
      // If the subRepoBranch is "default" then determine which branch to use based on the mainRepoBranch
      else
      {
        return mainRepoBranch
      }
}

// not used because branchExists() method has become cranky and
// does not recognize branches.
def checkoutBranch(mainRepoBranch, subRepoName, subRepoBranch) {
  // if user specified a branch then switch to it
  if (subRepoBranch.trim() != "default") {
    echo "Using user-specified branch ${subRepoBranch} on ${subRepoName}"
    if (!branchExists(subRepoBranch)) {
      throw new Exception("Branch ${subRepoBranch} does not exist on ${subRepoName}!")
    }
  }
  // If the subRepoBranch is "default" then determine which branch to use based on the mainRepoBranch
  else
  {
    // Try to use the same branch as main repo (unity or mesh)
    if (branchExists(mainRepoBranch)) {
      echo "Using the main repo branch ${mainRepoBranch} on ${subRepoName}"
      subRepoBranch = mainRepoBranch
    }
    //default to master if it does not exist
    else {
      echo "Using the default branch master"
      subRepoBranch = "master"
    }
  }
  echo "Checking out branch ${subRepoBranch} on ${subRepoName}"
  sh(returnStdout: true, script: "git checkout ${subRepoBranch}")
  //verify that indeed the branch was switched
  def onBranch = sh(returnStdout: true, script: "git branch | grep \\* | cut -d \' \' -f2")
  if (onBranch.trim() != subRepoBranch) {
    throw new Exception("Could not checkout branch ${subRepoBranch} on ${subRepoName}")
  }
  echo "Verified ${subRepoName} is on branch ${onBranch}"
  return subRepoBranch
}
