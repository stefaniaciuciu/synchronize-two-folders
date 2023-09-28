import argparse
import filecmp
import shutil
import os
import json


def compareSourceAndOldReplica(source, oldReplica):
    newFiles =[]
    newDirectories=[]
    removedFiles=[]
    removedDirectories=[]
    copiedFiles=[]

    for file in os.listdir(source):
        sourceFile = os.path.join(source,file)
        replicaFile = os.path.join(oldReplica, file)

        if os.path.isdir(sourceFile) and os.path.isdir(replicaFile):
            compareSourceAndOldReplica(sourceFile,replicaFile)
        elif os.path.exists(replicaFile):
            copiedFiles.append(replicaFile)
        else:
            newFiles.append(sourceFile)
        if os.path.exists(sourceFile) is not True and os.path.exists(replicaFile):
            removedFiles.append(replicaFile)

        if os.path.isdir(sourceFile) and os.path.exists(replicaFile) is not True:
            newDirectories.append(sourceFile)
        if os.path.exists(sourceFile) is not True and os.path.isdir(replicaFile):
            removedDirectories.append(replicaFile)

    createJSON(newFiles, newDirectories, removedFiles, removedDirectories, copiedFiles)


def compareSourceAndJson(source, lastJson):

    with open(lastJson, 'r') as json_file:
        data = json.load(json_file)

    newFiles = []
    newDirectories = []
    removedFiles = []
    removedDirectories = []
    copiedFiles = []

    for file in os.listdir(source):
        if file in data["newFiles"] or file in data["copiedFiles"]:
            copiedFiles.append(file)
        if file not in data["newFiles"] and file not in data["copiedFiles"]:
            newFiles.append(file)

        for file2 in data["newFiles"]:
            if file2 not in os.listdir(source):
                removedFiles.append(file2)

        for file3 in data["copiedFiles"]:
            if file3 not in os.listdir(source):
                removedFiles.append(file3)

    createJSON(newFiles, newDirectories, removedFiles, removedDirectories, copiedFiles)


def createJSON(newFiles, newDirectories, removedFiles, removedDirectories, copiedFiles):

    data = {
        "numberOfNewFiles": len(newFiles),
        "newFiles": newFiles,
        "numberOfNewDirectories": len(newDirectories),
        "newDirectories": newDirectories,
        "numberOfRemovedFiles": len(removedFiles),
        "removedFiles": removedFiles,
        "numberOfRemovedDirectories": len(removedDirectories),
        "removedDirectories": removedDirectories,
        "numberOfCopiedFiles": len(copiedFiles),
        "copiedFiles": copiedFiles
    }

    file_path = "directory/synchronization_logs.json"
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)


def copySourceToReplica(source, replica):
    if not os.path.exists(replica):
        os.makedirs(replica)
        copyAllFiles(source, replica)
    else:
        cmp = filecmp.dircmp(source, replica)

        for missing_file in cmp.left_only:
            sourceFile = os.path.join(source, missing_file)
            replicaFile = os.path.join(replica, missing_file)
            if os.path.isdir(sourceFile):
                copySourceToReplica(sourceFile, replicaFile)
            else:
                shutil.copy2(sourceFile, replicaFile)

        for extra_file in cmp.right_only:
            extraFile = os.path.join(replica, extra_file)
            if os.path.isdir(extraFile):
                shutil.rmtree(extraFile)
            else:
                os.remove(extraFile)

        for common_dir in cmp.common_dirs:
            copySourceToReplica(
                os.path.join(source, common_dir),
                os.path.join(replica, common_dir)
            )


def copyAllFiles(source, replica):
    for root, dirs, files in os.walk(source):
        for file in files:
            sourceFile = os.path.join(root, file)
            replicaFile = os.path.join(replica, os.path.relpath(sourceFile, source))
            if not os.path.exists(replicaFile) or os.stat(sourceFile).st_mtime > os.stat(replicaFile).st_mtime:
                if not os.path.exists(os.path.dirname(replicaFile)):
                    os.makedirs(os.path.dirname(replicaFile))
                shutil.copy2(sourceFile, replicaFile)


parser = argparse.ArgumentParser(description="Read the path for each folder")

parser.add_argument("source", type=str, help="Source folder path")
parser.add_argument("replica", type=str, help="Replica folder path")

args = parser.parse_args()

if os.path.isdir(args.source) is not True:
    raise argparse.ArgumentTypeError(f"{args.source} is not the path of a directory!")

newFiles = []
newDirectories = []
removedFiles = []
removedDirectories = []
copiedFiles = []

createJSON(newFiles,newDirectories,removedFiles,removedDirectories,copiedFiles)
copySourceToReplica(args.source, args.replica)
compareSourceAndJson(args.source, "synchronization_logs.json")















