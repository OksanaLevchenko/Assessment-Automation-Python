#!/bin/bash

# Check for the --cluster argument
if [ "$1" == "--cluster" ] && [ -n "$2" ]; then
  CLUSTER_NAME=$2
else
  echo "Usage: $0 --cluster <cluster-name>"
  exit 1
fi

# Create the top-level directory with the cluster name
mkdir -p "$CLUSTER_NAME"

# Get all api-resources that are namespaced, get all namespaces, for each api-resource it finds look into every namespace for it. Output that to json and store it in a folder
for resource in $(kubectl api-resources --namespaced=true --no-headers | grep -v secrets | awk '{print $1}'); do
  echo "Processing resource: $resource"
  for ns in $(kubectl get namespaces -o jsonpath='{.items[*].metadata.name}'); do
    echo "  Namespace: $ns"
    mkdir -p "$CLUSTER_NAME/$ns/$resource"
    for obj in $(kubectl get $resource -n $ns -o jsonpath='{.items[*].metadata.name}'); do
      echo "    Object: $obj"
      kubectl get $resource $obj -n $ns -o json > "$CLUSTER_NAME/$ns/$resource/$obj.json"
    done
  done
done

echo "Processing completed. JSON files stored in the '$CLUSTER_NAME' directory."
